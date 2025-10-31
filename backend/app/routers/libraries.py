"""
Libraries API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Library, SystemSettings
from app.schemas import LibraryResponse
from app.security import decrypt_token
from app.integrations.plex import PlexIntegration

router = APIRouter()


@router.get("", response_model=list[LibraryResponse])
def get_libraries(db: Session = Depends(get_db)):
    """Get all imported libraries"""
    libraries = db.query(Library).all()
    return libraries


@router.post("/import", response_model=list[LibraryResponse])
def import_libraries(db: Session = Depends(get_db)):
    """Import libraries from Plex"""
    settings = db.query(SystemSettings).first()
    if not settings or not settings.plex_url or not settings.plex_token_encrypted:
        raise HTTPException(status_code=400, detail="Plex not configured")
    
    try:
        plex_token = decrypt_token(settings.plex_token_encrypted)
        plex = PlexIntegration(settings.plex_url, plex_token)
        
        plex_libraries = plex.get_libraries()
        imported = []
        
        for plex_lib in plex_libraries:
            # Check if library already exists
            existing = db.query(Library).filter(Library.plex_id == plex_lib["plex_id"]).first()
            if existing:
                existing.title = plex_lib["title"]
                imported.append(existing)
            else:
                new_library = Library(
                    plex_id=plex_lib["plex_id"],
                    title=plex_lib["title"],
                    library_type=plex_lib["library_type"]
                )
                db.add(new_library)
                imported.append(new_library)
        
        db.commit()
        
        for lib in imported:
            db.refresh(lib)
        
        return imported
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

