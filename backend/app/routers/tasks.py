"""
Tasks API router (scanning, rule execution)
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Rule, Library, Candidate, SystemSettings, ActionLog
from app.schemas import ScanResponse
from app.security import decrypt_token
from app.integrations.plex import PlexIntegration
from app.integrations.radarr import RadarrIntegration
from app.integrations.sonarr import SonarrIntegration
from app.rule_engine import RuleEngine
from datetime import datetime, timedelta
import json

router = APIRouter()


def get_integrations(db: Session):
    """Get configured integrations"""
    settings = db.query(SystemSettings).first()
    if not settings or not settings.plex_url or not settings.plex_token_encrypted:
        return None, None, None
    
    plex_token = decrypt_token(settings.plex_token_encrypted)
    plex = PlexIntegration(settings.plex_url, plex_token)
    
    radarr = None
    if settings.radarr_url and settings.radarr_api_key_encrypted:
        radarr_key = decrypt_token(settings.radarr_api_key_encrypted)
        radarr = RadarrIntegration(settings.radarr_url, radarr_key)
    
    sonarr = None
    if settings.sonarr_url and settings.sonarr_api_key_encrypted:
        sonarr_key = decrypt_token(settings.sonarr_api_key_encrypted)
        sonarr = SonarrIntegration(settings.sonarr_url, sonarr_key)
    
    return plex, radarr, sonarr


def scan_rule(rule_id: int):
    """Scan a single rule and create candidates"""
    # Create a new database session for the background task
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule or not rule.enabled:
            db.close()
            return
        
        library = rule.library
        if not library:
            db.close()
            return
        
        plex, radarr, sonarr = get_integrations(db)
        if not plex:
            db.close()
            return
        
        engine = RuleEngine(plex, radarr, sonarr)
        
        conditions = json.loads(rule.conditions_json)
        actions = json.loads(rule.actions_json)
        immediate_actions = actions.get("immediate", [])
        delayed_actions = actions.get("delayed", [])
        
        # Clear existing candidates for this rule
        # Use delete with synchronize_session=False to avoid locking issues
        try:
            db.query(Candidate).filter(Candidate.rule_id == rule.id).delete(synchronize_session=False)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not clear existing candidates: {e}")
        
        candidates_created = 0
        
        if library.library_type == "movie":
            print(f"Scanning rule {rule_id}: Getting movies from library {library.plex_id}")
            movies = plex.get_movies(library.plex_id)
            print(f"Scanning rule {rule_id}: Found {len(movies)} movies")
            for movie in movies:
                item_data = plex.get_movie_data(movie)
                print(f"Scanning rule {rule_id}: Checking movie '{item_data['title']}' - lastPlayedDays: {item_data.get('lastPlayedDays')}")
                
                # Evaluate conditions
                matches = engine.evaluate_conditions(conditions, rule.logic, item_data)
                print(f"Scanning rule {rule_id}: Movie '{item_data['title']}' matches conditions: {matches}")
                if matches:
                    # Execute immediate actions (pass delayed_actions and item_data for variable replacement)
                    engine.execute_immediate_actions(immediate_actions, item_data["key"], "movie", rule.dry_run, delayed_actions, item_data)
                    
                    # Create ONE candidate per item with ALL delayed actions (not one per action)
                    if delayed_actions:
                        # Use the maximum delay_days from all actions for the scheduled date
                        max_delay = max([action.get("delay_days", 0) for action in delayed_actions], default=0)
                        scheduled_date = datetime.now() + timedelta(days=max_delay) if max_delay > 0 else None
                        
                        candidate = Candidate(
                            rule_id=rule.id,
                            plex_key=item_data["key"],
                            item_type="movie",
                            item_title=item_data["title"],
                            reason=f"Matched rule '{rule.name}'",
                            actions_json=json.dumps(delayed_actions),  # Store ALL actions, not just one
                            scheduled_date=scheduled_date
                        )
                        db.add(candidate)
                        candidates_created += 1
                        print(f"Scanning rule {rule_id}: Created candidate for '{item_data['title']}' with {len(delayed_actions)} actions")
        
        elif library.library_type == "show":
            shows = plex.get_shows(library.plex_id)
            for show in shows:
                seasons = plex.get_seasons(show)
                for season in seasons:
                    item_data = plex.get_season_data(season)
                    season_title = item_data.get('season_title', item_data.get('title', 'Unknown'))
                    print(f"Scanning rule {rule_id}: Checking season '{season_title}' (show: {item_data.get('show_title', 'N/A')}) - collections: {item_data.get('inCollections', [])}")
                    
                    # Evaluate conditions
                    matches = engine.evaluate_conditions(conditions, rule.logic, item_data)
                    print(f"Scanning rule {rule_id}: Season '{season_title}' matches conditions: {matches}")
                    if matches:
                        print(f"Scanning rule {rule_id}: Executing immediate actions for '{season_title}'")
                        # Execute immediate actions (pass delayed_actions and item_data for variable replacement)
                        action_results = engine.execute_immediate_actions(immediate_actions, item_data["key"], "season", rule.dry_run, delayed_actions, item_data)
                        print(f"Scanning rule {rule_id}: Immediate action results for '{season_title}': {action_results}")
                        
                        # Create ONE candidate per item with ALL delayed actions (not one per action)
                        if delayed_actions:
                            # Use the maximum delay_days from all actions for the scheduled date
                            max_delay = max([action.get("delay_days", 0) for action in delayed_actions], default=0)
                            scheduled_date = datetime.now() + timedelta(days=max_delay) if max_delay > 0 else None
                            
                            candidate = Candidate(
                                rule_id=rule.id,
                                plex_key=item_data["key"],
                                item_type="season",
                                item_title=item_data["season_title"],
                                season_number=item_data["season_number"],
                                show_title=item_data.get("show_title"),  # Store show title
                                episode_count=item_data.get("episode_count"),  # Store episode count
                                last_watched_episode_title=item_data.get("lastWatchedEpisodeTitle"),
                                last_watched_episode_number=item_data.get("lastWatchedEpisodeNumber"),
                                last_watched_episode_date=item_data.get("lastWatchedEpisodeDate"),
                                reason=f"Matched rule '{rule.name}'",
                                actions_json=json.dumps(delayed_actions),  # Store ALL actions, not just one
                                scheduled_date=scheduled_date
                            )
                            db.add(candidate)
                            candidates_created += 1
        
        db.commit()
        print(f"Scanning rule {rule_id}: Completed successfully, created {candidates_created} candidates")
    
    except Exception as e:
        db.rollback()
        print(f"Error scanning rule {rule_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@router.post("/scan", response_model=ScanResponse)
def scan_all_rules(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Scan all enabled rules"""
    rules = db.query(Rule).filter(Rule.enabled == True).all()
    
    if not rules:
        return ScanResponse(success=True, message="No enabled rules found", candidates_count=0)
    
    for rule in rules:
        background_tasks.add_task(scan_rule, rule.id)
    
    return ScanResponse(
        success=True,
        message=f"Scanning {len(rules)} rule(s) in background",
        candidates_count=0
    )


@router.post("/scan/{rule_id}", response_model=ScanResponse)
def scan_single_rule(rule_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Scan a single rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    background_tasks.add_task(scan_rule, rule_id)
    
    return ScanResponse(
        success=True,
        message=f"Scanning rule '{rule.name}' in background",
        candidates_count=0
    )

