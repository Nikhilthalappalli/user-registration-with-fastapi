from fastapi import FastAPI, File, Form, HTTPException, Depends, UploadFile
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal, pic_collection
from sqlalchemy.orm import Session
import uuid
import bcrypt 

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
    
class UserRegistration(BaseModel):
    full_name : str
    email : str
    phone : str
    password : str
    profile_pic : UploadFile
    
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependecy = Annotated[Session,Depends(get_db)]

#User registration with postgres and mongodb
@app.post("/new_user_reg/")
async def register_user_1(
    full_name : str,
    email : str,
    phone : str,
    password : str,
    profile_pic : UploadFile,
    db: db_dependecy
):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_email_exist = db.query(models.User).filter(models.User.email == email).first()
    if user_email_exist:
        raise HTTPException(status_code=400,detail="Email Alredy Exist")
    
    user_phone_exist = db.query(models.User).filter(models.User.phone == phone).first()
    if user_phone_exist:
        raise HTTPException(status_code=400,detail="Phone Number Alredy Exist")
    new_user = models.User(full_name=full_name,email=email,phone=phone,password=hashed_password.decode('utf-8'))
    db.add(new_user) 
    db.commit()
    db.refresh(new_user)
    
    image_path = f"{profile_pic.filename}"
    with open(image_path, "wb") as image_file:
        image_file.write(profile_pic.file.read())

    profile_data = {
        "user_id": new_user.id,
        "profile_picture": image_path
    }
    
    pic_collection.insert_one(profile_data)
    db.commit()
     
    return {"message": "User registered successfully"}

#Getting user details from both postgres and mongodb
@app.get("/get_user_details_mongo_postgress/{user_id}/")
async def get_user_mongo_postgress(user_id:int,db:db_dependecy):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_data = pic_collection.find_one({"user_id": user_id})
    if not profile_data:
        raise HTTPException(status_code=404,detail="No matching picture")
    
    return {
        "user_id": user.id,
        "first_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "profile_picture": profile_data["profile_picture"]
    }
    
#User registration with postgres only (diffrent tables)
@app.post("/register/")
async def register_user(
    full_name : str,
    email : str,
    phone : str,
    password : str,
    profile_pic : UploadFile,
    db: db_dependecy
):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_email_exist = db.query(models.User).filter(models.User.email == email).first()
    if user_email_exist:
        raise HTTPException(status_code=400,detail="Email Alredy Exist")
    
    user_phone_exist = db.query(models.User).filter(models.User.phone == phone).first()
    if user_phone_exist:
        raise HTTPException(status_code=400,detail="Phone Number Alredy Exist")
    new_user = models.User(full_name=full_name,email=email,phone=phone,password=hashed_password.decode('utf-8'))

    db.add(new_user) 
    db.commit()
    db.refresh(new_user)
    
    image_path = f"{profile_pic.filename}"
    with open(image_path, "wb") as image_file:
        image_file.write(profile_pic.file.read())

    db_profile = models.Profile(user_id=new_user.id, profile_pic=image_path)
    db.add(db_profile)
    db.commit()
     
    return {"message": "User registered successfully"}

#Getting data from postgres (both tables)
@app.get("/get_user/{user_id}/")
async def get_user(user_id:int,db: db_dependecy):
    current_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not current_user:
        raise HTTPException(status_code=404,detail="User does not exist")
    
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    
    if not profile:
        raise HTTPException(status_code=404,detail="Picture does not exist")
    
    user_data = {
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
    }

    response_data = {
        "user_data": user_data,
        "profile_picture": profile.profile_pic,
    }
    return response_data


