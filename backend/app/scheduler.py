"""
Scheduler for automated scans and delayed action execution
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Candidate, SystemSettings, ActionLog, Rule
from app.security import decrypt_token
from app.integrations.plex import PlexIntegration
from app.integrations.radarr import RadarrIntegration
from app.integrations.sonarr import SonarrIntegration
from app.rule_engine import RuleEngine
from datetime import datetime
import json

scheduler = BackgroundScheduler()


def get_integrations():
    """Get configured integrations"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).first()
        if not settings or not settings.plex_url or not settings.plex_token_encrypted:
            return None, None, None, None
        
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
        
        return db, plex, radarr, sonarr
    except Exception:
        return None, None, None, None


def execute_pending_candidates():
    """Execute delayed actions for candidates that are due"""
    db, plex, radarr, sonarr = get_integrations()
    if not db or not plex:
        return
    
    try:
        now = datetime.now()
        candidates = db.query(Candidate).filter(
            Candidate.scheduled_date <= now,
            Candidate.cancelled == False
        ).all()
        
        engine = RuleEngine(plex, radarr, sonarr)
        
        for candidate in candidates:
            actions = json.loads(candidate.actions_json)
            dry_run = candidate.rule.dry_run if candidate.rule else True
            
            for action in actions:
                result = engine.execute_delayed_action(
                    action,
                    candidate.plex_key,
                    candidate.item_title,
                    candidate.item_type,
                    dry_run
                )
                
                # Log the action
                log_entry = ActionLog(
                    rule_id=candidate.rule_id,
                    plex_key=candidate.plex_key,
                    item_type=candidate.item_type,
                    item_title=candidate.item_title,
                    action_type=result["action_type"],
                    action_status=result["status"],
                    details=result.get("message", "")
                )
                db.add(log_entry)
            
            # Mark candidate as executed (delete it)
            db.delete(candidate)
        
        db.commit()
    
    except Exception as e:
        print(f"Error executing pending candidates: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Run every hour to check for pending candidates
    scheduler.add_job(
        execute_pending_candidates,
        trigger=CronTrigger(minute=0),  # Every hour at minute 0
        id="execute_pending_candidates",
        name="Execute pending delayed actions",
        replace_existing=True
    )
    
    scheduler.start()


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()

