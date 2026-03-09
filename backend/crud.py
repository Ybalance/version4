from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, auth
import os

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(phone=user.phone, hashed_password=hashed_password, nickname=user.nickname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Capsule CRUD
def get_capsule(db: Session, capsule_id: int):
    return db.query(models.Capsule).filter(models.Capsule.id == capsule_id).first()

def create_capsule(db: Session, capsule: schemas.CapsuleCreate, user_id: int):
    # Create Capsule
    db_capsule = models.Capsule(
        title=capsule.title,
        description=capsule.description,
        latitude=capsule.latitude,
        longitude=capsule.longitude,
        address=capsule.address,
        is_public=capsule.is_public,
        tags=capsule.tags,
        weblink=capsule.weblink,
        extension=capsule.extension,
        llm_analysis=capsule.llm_analysis,
        owner_id=user_id
    )
    db.add(db_capsule)
    db.commit()
    db.refresh(db_capsule)
    
    # Create Media Items
    for media in capsule.media_items:
        db_media = models.Media(
            capsule_id=db_capsule.id,
            media_type=media.media_type,
            file_path=media.file_path
        )
        db.add(db_media)
    
    db.commit()
    db.refresh(db_capsule)
    return db_capsule

def get_nearby_capsules(db: Session, lat: float, lon: float, radius_km: float = 5.0, user_id: int = None):
    # Simplified bounding box or distance calculation.
    # For SQLite/Prototype, we can just filter by basic lat/lon range or calculate distance in python (less efficient but works for small data)
    # 1 degree lat ~= 111km. 5km ~= 0.045 degrees.
    # Using 10000km radius logic as requested in previous turns for global visibility
    
    lat_min = lat - 90.0 # Wide range
    lat_max = lat + 90.0
    lon_min = lon - 180.0
    lon_max = lon + 180.0
    
    query = db.query(models.Capsule).filter(
        models.Capsule.is_public == True
    )
    
    capsules = query.all()
    # Populate extra fields
    for cap in capsules:
        cap.likes_count = len(cap.likes)
        cap.owner_nickname = cap.owner.nickname
        if user_id:
            cap.is_liked_by_me = any(like.user_id == user_id for like in cap.likes)
            
    return capsules

def get_user_capsules(db: Session, user_id: int):
    capsules = db.query(models.Capsule).filter(models.Capsule.owner_id == user_id).all()
    for cap in capsules:
        cap.likes_count = len(cap.likes)
        cap.owner_nickname = cap.owner.nickname
        cap.is_liked_by_me = any(like.user_id == user_id for like in cap.likes)
    return capsules

def get_liked_capsules(db: Session, user_id: int):
    liked_capsules = db.query(models.Capsule).join(models.Like).filter(models.Like.user_id == user_id).all()
    for cap in liked_capsules:
        cap.likes_count = len(cap.likes)
        cap.owner_nickname = cap.owner.nickname
        cap.is_liked_by_me = True
    return liked_capsules

def like_capsule(db: Session, capsule_id: int, user_id: int):
    # Check if already liked
    existing_like = db.query(models.Like).filter(models.Like.user_id == user_id, models.Like.capsule_id == capsule_id).first()
    is_liked = False
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        is_liked = False # Unliked
    else:
        new_like = models.Like(user_id=user_id, capsule_id=capsule_id)
        db.add(new_like)
        db.commit()
        is_liked = True # Liked
        
    # Get updated count
    count = db.query(models.Like).filter(models.Like.capsule_id == capsule_id).count()
    return is_liked, count

def delete_capsule(db: Session, capsule_id: int, user_id: int):
    capsule = db.query(models.Capsule).filter(models.Capsule.id == capsule_id).first()
    if not capsule:
        return False
    if capsule.owner_id != user_id:
        return False # Not authorized
    
    # Cleanup files
    try:
        # 1. Delete Media Files
        for media in capsule.media_items:
            try:
                # file_path in DB might be full URL or relative path.
                # If it's URL: http://host:port/media/filename.jpg -> we need local path.
                # If it starts with /media/, we strip leading slash.
                
                path_to_delete = media.file_path
                if "media/" in path_to_delete:
                    # Extract part after media/ including media/
                    # e.g. http://.../media/xyz.jpg -> media/xyz.jpg
                    idx = path_to_delete.find("media/")
                    path_to_delete = path_to_delete[idx:]
                
                # Now path_to_delete is likely "media/filename.ext"
                if os.path.exists(path_to_delete):
                    os.remove(path_to_delete)
                    print(f"Deleted file: {path_to_delete}")
                else:
                    print(f"File not found for deletion: {path_to_delete}")
                    
            except Exception as e:
                print(f"Error deleting file {media.file_path}: {e}")
        
        # 2. Delete Descriptor File
        descriptor_path = f"media/descriptors/{capsule_id}.npy"
        if os.path.exists(descriptor_path):
            os.remove(descriptor_path)
            print(f"Deleted descriptor: {descriptor_path}")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")

    db.delete(capsule)
    db.commit()
    return True

def update_capsule(db: Session, capsule_id: int, capsule_update: schemas.CapsuleCreate, user_id: int):
    db_capsule = db.query(models.Capsule).filter(models.Capsule.id == capsule_id).first()
    if not db_capsule:
        return None
    if db_capsule.owner_id != user_id:
        return None # Unauthorized
    
    # Update fields
    db_capsule.title = capsule_update.title
    db_capsule.description = capsule_update.description
    db_capsule.tags = capsule_update.tags
    db_capsule.is_public = capsule_update.is_public
    db_capsule.weblink = capsule_update.weblink
    db_capsule.extension = capsule_update.extension
    # We might not update llm_analysis if user didn't trigger AI again, or if frontend sends it back.
    if capsule_update.llm_analysis:
        db_capsule.llm_analysis = capsule_update.llm_analysis
        
    # Update Media
    # 1. Remove old media entries (DB only, files kept for now or we assume frontend sends all valid ones)
    db.query(models.Media).filter(models.Media.capsule_id == capsule_id).delete()
    
    # 2. Add new media entries
    for media in capsule_update.media_items:
        db_media = models.Media(
            capsule_id=db_capsule.id,
            media_type=media.media_type,
            file_path=media.file_path
        )
        db.add(db_media)
        
    db.commit()
    db.refresh(db_capsule)
    
    # Populate extra fields for response
    db_capsule.likes_count = len(db_capsule.likes)
    db_capsule.owner_nickname = db_capsule.owner.nickname
    db_capsule.is_liked_by_me = any(like.user_id == user_id for like in db_capsule.likes)
    
    return db_capsule
