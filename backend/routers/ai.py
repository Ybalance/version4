from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from services.ai_generator import generate_capsule_details
from services.visual_recognition import find_best_match
import database, crud
import io

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/generate")
async def generate_content(
    file: UploadFile = File(...),
    description: str = Form("")
):
    try:
        contents = await file.read()
        result = generate_capsule_details(contents, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recognize")
async def recognize_image(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    try:
        contents = await file.read()
        # Find match using ORB
        match_id = find_best_match(contents)
        
        if match_id:
            # Verify existence in DB
            capsule = crud.get_capsule(db, match_id)
            if capsule:
                return {"match_found": True, "capsule_id": match_id}
            else:
                print(f"Match found for ID {match_id} but not in DB. Ignoring.")
                return {"match_found": False}
        else:
            return {"match_found": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
