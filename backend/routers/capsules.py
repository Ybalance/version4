from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import schemas, crud, database, auth, utils
import shutil
import os
from services.visual_recognition import extract_and_save_features

router = APIRouter(prefix="/capsules", tags=["capsules"])

@router.post("/create", response_model=schemas.Capsule)
def create_capsule(
    capsule: schemas.CapsuleCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    new_capsule = crud.create_capsule(db=db, capsule=capsule, user_id=current_user.id)
    
    # --- Feature 2: Visual Recognition Integration ---
    # Automatically compute features for any uploaded images
    try:
        for media in new_capsule.media_items:
            if media.media_type == "image":
                # Path is relative like "/media/xyz.jpg"
                # Remove leading slash for local path
                local_path = media.file_path.lstrip("/")
                if os.path.exists(local_path):
                    with open(local_path, "rb") as f:
                        image_bytes = f.read()
                        extract_and_save_features(image_bytes, new_capsule.id)
    except Exception as e:
        print(f"Failed to extract features: {e}")
        
    return new_capsule

@router.put("/{capsule_id}", response_model=schemas.Capsule)
def update_capsule(
    capsule_id: int,
    capsule: schemas.CapsuleCreate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    updated_capsule = crud.update_capsule(db=db, capsule_id=capsule_id, capsule_update=capsule, user_id=current_user.id)
    if not updated_capsule:
        raise HTTPException(status_code=404, detail="Capsule not found or not authorized")
        
    # Re-extract features for any images (optional optimization: check if changed)
    # For now, just process all images again to be safe/simple
    try:
        for media in updated_capsule.media_items:
            if media.media_type == "image":
                local_path = media.file_path.lstrip("/")
                if os.path.exists(local_path):
                    with open(local_path, "rb") as f:
                        image_bytes = f.read()
                        extract_and_save_features(image_bytes, updated_capsule.id)
    except Exception as e:
        print(f"Failed to extract features during update: {e}")
        
    return updated_capsule

@router.get("/nearby", response_model=List[schemas.Capsule])
def get_nearby_capsules(
    lat: float, 
    lon: float, 
    radius: float = 5.0,
    db: Session = Depends(database.get_db),
    current_user: Optional[schemas.User] = Depends(auth.get_current_user) # Optional auth for public feed
):
    user_id = current_user.id if current_user else None
    return crud.get_nearby_capsules(db=db, lat=lat, lon=lon, radius_km=radius, user_id=user_id)

@router.get("/my", response_model=List[schemas.Capsule])
def get_my_capsules(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    return crud.get_user_capsules(db=db, user_id=current_user.id)

@router.get("/liked", response_model=List[schemas.Capsule])
def get_liked_capsules(
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    return crud.get_liked_capsules(db=db, user_id=current_user.id)

@router.post("/{capsule_id}/like")
def like_capsule(
    capsule_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    is_liked, count = crud.like_capsule(db=db, capsule_id=capsule_id, user_id=current_user.id)
    return {"liked": is_liked, "likes_count": count}

@router.delete("/{capsule_id}")
def delete_capsule(
    capsule_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    success = crud.delete_capsule(db=db, capsule_id=capsule_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized or not found")
    return {"status": "ok"}

@router.post("/process_image")
def process_image(file: UploadFile = File(...)):
    # Save temp file
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # In real app, we would convert file to base64 or upload to OSS and get URL
    # Here we just mock the Qwen response
    result = utils.analyze_image("base64_placeholder")
    
    # Cleanup
    os.remove(temp_file)
    
    return result
