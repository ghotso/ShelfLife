"""
Candidates API router
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Candidate
from app.schemas import CandidateResponse
from app.routers.tasks import get_integrations
import json

router = APIRouter()


@router.get("", response_model=list[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    """Get all candidates"""
    candidates = db.query(Candidate).filter(Candidate.cancelled == False).all()
    result = []
    for candidate in candidates:
        candidate_dict = {
            "id": candidate.id,
            "rule_id": candidate.rule_id,
            "plex_key": candidate.plex_key,
            "item_type": candidate.item_type,
            "item_title": candidate.item_title,
            "season_number": candidate.season_number,
            "show_title": candidate.show_title,
            "episode_count": candidate.episode_count,
            "last_watched_episode_title": candidate.last_watched_episode_title,
            "last_watched_episode_number": candidate.last_watched_episode_number,
            "last_watched_episode_date": candidate.last_watched_episode_date,
            "reason": candidate.reason,
            "actions": json.loads(candidate.actions_json),
            "scheduled_date": candidate.scheduled_date,
            "created_at": candidate.created_at,
            "updated_at": candidate.updated_at,
            "cancelled": candidate.cancelled,
            "rule": None
        }
        if candidate.rule:
            candidate_dict["rule"] = {
                "id": candidate.rule.id,
                "name": candidate.rule.name
            }
        result.append(CandidateResponse(**candidate_dict))
    return result


@router.post("/{candidate_id}/add-to-collection")
def add_candidate_to_collection(
    candidate_id: int,
    collection_name: str = Query(None, description="Collection name (defaults to 'Keep')"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Add a candidate to a Keep collection and trigger rule rescan"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.cancelled:
        raise HTTPException(status_code=400, detail="Candidate is already cancelled")
    
    # Get integrations
    plex, _, _ = get_integrations(db)
    if not plex:
        raise HTTPException(status_code=500, detail="Plex not configured")
    
    # Determine collection name - use provided one or default to first Keep collection
    if not collection_name:
        collection_name = "Keep"  # Default to "Keep"
    
    # Add to collection
    try:
        # For season candidates, add the SHOW to the collection (not the season)
        # For movie candidates, add the movie to the collection
        if candidate.item_type == "season":
            try:
                success = plex.add_show_to_collection(candidate.plex_key, collection_name)
            except ValueError as e:
                # ValueError contains user-friendly error message
                raise HTTPException(status_code=400, detail=str(e))
        else:
            success = plex.add_to_collection(candidate.plex_key, collection_name, candidate.item_type)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to add to collection {collection_name}")
        
        # Trigger rule rescan in background (this will remove the candidate if it now has Keep override)
        if background_tasks:
            from app.routers.tasks import scan_rule
            background_tasks.add_task(scan_rule, candidate.rule_id)
        
        return {
            "success": True,
            "message": f"Added to collection '{collection_name}' and triggered rule rescan",
            "collection_name": collection_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to collection: {str(e)}")

