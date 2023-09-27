from sqlalchemy import  Column, ForeignKey, Integer, String
from database import Base

    
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer,primary_key=True,index=True)
    full_name = Column(String,index=True)
    password = Column(String)
    phone = Column(String,index=True)
    email = Column(String,index=True)
    
class Profile(Base):
    __tablename__ = 'profile'
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    profile_pic = Column(String)
    