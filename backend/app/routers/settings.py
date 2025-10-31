"""
Settings API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SystemSettings
from app.schemas import SystemSettingsBase, SystemSettingsResponse, TestConnectionRequest, TestConnectionResponse
from app.security import encrypt_token, decrypt_token, hash_password
from app.integrations.plex import PlexIntegration
from app.integrations.radarr import RadarrIntegration
from app.integrations.sonarr import SonarrIntegration

router = APIRouter()


@router.get("", response_model=SystemSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get system settings"""
    settings = db.query(SystemSettings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings


@router.post("", response_model=SystemSettingsResponse)
def update_settings(settings_data: SystemSettingsBase, db: Session = Depends(get_db)):
    """Update system settings"""
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
    
    if settings_data.plex_url is not None:
        settings.plex_url = settings_data.plex_url
    if settings_data.plex_token is not None and settings_data.plex_token:
        settings.plex_token_encrypted = encrypt_token(settings_data.plex_token)
    if settings_data.radarr_url is not None:
        settings.radarr_url = settings_data.radarr_url
    if settings_data.radarr_api_key is not None and settings_data.radarr_api_key:
        settings.radarr_api_key_encrypted = encrypt_token(settings_data.radarr_api_key)
    if settings_data.sonarr_url is not None:
        settings.sonarr_url = settings_data.sonarr_url
    if settings_data.sonarr_api_key is not None and settings_data.sonarr_api_key:
        settings.sonarr_api_key_encrypted = encrypt_token(settings_data.sonarr_api_key)
    if settings_data.language:
        settings.language = settings_data.language
    if settings_data.theme:
        settings.theme = settings_data.theme
    
    settings.auth_enabled = settings_data.auth_enabled
    if settings_data.auth_password:
        settings.auth_password_hash = hash_password(settings_data.auth_password)
    db.commit()
    db.refresh(settings)
    return settings


@router.post("/test", response_model=TestConnectionResponse)
def test_plex_connection(request: TestConnectionRequest, db: Session = Depends(get_db)):
    """Test Plex connection - uses stored token from database if token_or_key is empty/None"""
    try:
        settings = db.query(SystemSettings).first()
        
        # Use provided token, or fall back to stored token from database
        token_to_use = request.token_or_key
        if not token_to_use or token_to_use.strip() == '':
            if settings and settings.plex_token_encrypted:
                token_to_use = decrypt_token(settings.plex_token_encrypted)
            else:
                return TestConnectionResponse(success=False, message="No token provided and no token found in settings")
        
        # Use provided URL, or fall back to stored URL
        url_to_use = request.url
        if not url_to_use or url_to_use.strip() == '':
            if settings and settings.plex_url:
                url_to_use = settings.plex_url
            else:
                return TestConnectionResponse(success=False, message="No URL provided and no URL found in settings")
        
        plex = PlexIntegration(url_to_use, token_to_use)
        success, message = plex.test_connection()
        return TestConnectionResponse(success=success, message=message)
    except Exception as e:
        return TestConnectionResponse(success=False, message=str(e))


@router.post("/test_radarr", response_model=TestConnectionResponse)
def test_radarr_connection(request: TestConnectionRequest, db: Session = Depends(get_db)):
    """Test Radarr connection - uses stored API key from database if token_or_key is empty/None"""
    try:
        settings = db.query(SystemSettings).first()
        
        # Use provided API key, or fall back to stored key from database
        key_to_use = request.token_or_key
        if not key_to_use or key_to_use.strip() == '':
            if settings and settings.radarr_api_key_encrypted:
                key_to_use = decrypt_token(settings.radarr_api_key_encrypted)
            else:
                return TestConnectionResponse(success=False, message="No API key provided and no API key found in settings")
        
        # Use provided URL, or fall back to stored URL
        url_to_use = request.url
        if not url_to_use or url_to_use.strip() == '':
            if settings and settings.radarr_url:
                url_to_use = settings.radarr_url
            else:
                return TestConnectionResponse(success=False, message="No URL provided and no URL found in settings")
        
        radarr = RadarrIntegration(url_to_use, key_to_use)
        success, message = radarr.test_connection()
        return TestConnectionResponse(success=success, message=message)
    except Exception as e:
        return TestConnectionResponse(success=False, message=str(e))


@router.post("/test_sonarr", response_model=TestConnectionResponse)
def test_sonarr_connection(request: TestConnectionRequest, db: Session = Depends(get_db)):
    """Test Sonarr connection - uses stored API key from database if token_or_key is empty/None"""
    try:
        settings = db.query(SystemSettings).first()
        
        # Use provided API key, or fall back to stored key from database
        key_to_use = request.token_or_key
        if not key_to_use or key_to_use.strip() == '':
            if settings and settings.sonarr_api_key_encrypted:
                key_to_use = decrypt_token(settings.sonarr_api_key_encrypted)
            else:
                return TestConnectionResponse(success=False, message="No API key provided and no API key found in settings")
        
        # Use provided URL, or fall back to stored URL
        url_to_use = request.url
        if not url_to_use or url_to_use.strip() == '':
            if settings and settings.sonarr_url:
                url_to_use = settings.sonarr_url
            else:
                return TestConnectionResponse(success=False, message="No URL provided and no URL found in settings")
        
        sonarr = SonarrIntegration(url_to_use, key_to_use)
        success, message = sonarr.test_connection()
        return TestConnectionResponse(success=success, message=message)
    except Exception as e:
        return TestConnectionResponse(success=False, message=str(e))

