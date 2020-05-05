# app/models.py

import datetime
from app import db

class User(db.Model):
    """
    Create a user table
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) #id
    open_id = db.Column(db.Integer, index=True, unique=True) #open_id
    username = db.Column(db.String(60), index=True)
    avatar_url = db.Column(db.String(128))
    
    is_admin = db.Column(db.Boolean, default=False)


class Activity(db.Model):
    __tablename__ = 'activities'
    
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(60)) 
    startTime = db.Column(db.TIMESTAMP, nullable=False) 
    registrationDDL = db.Column(db.TIMESTAMP, nullable=False) 
    createtime = db.Column(db.TIMESTAMP(True), nullable=False, default=datetime.datetime.now)
    descript = db.Column(db.String(200))
    
    maxParticipantNumber = db.Column(db.Integer)
    currentParticipantNumber = db.Column(db.Integer, default=1)
    locationName = db.Column(db.String(60))
    locationLongitude = db.Column(db.Float())
    locationLatitude = db.Column(db.Float())
    locationType = db.Column(db.String(10))
    
    
