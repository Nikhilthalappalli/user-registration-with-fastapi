from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient


url_database = 'postgresql://postgres:123456@localhost:5432/api'

engine = create_engine(url_database)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

MONGO_DB_URL = "mongodb://localhost:27017/"
mongo_client = MongoClient(MONGO_DB_URL)
mongo_db = mongo_client["api"]
pic_collection = mongo_db['profile']