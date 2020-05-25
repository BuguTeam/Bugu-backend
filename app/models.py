# app/models.py

import datetime
from app import db

user_activity = db.Table('user_activity',
                            db.Column('user_id', db.String(128), db.ForeignKey('users.openid'), primary_key=True),
                            db.Column('activity_id', db.Integer, db.ForeignKey('activities.id'), primary_key=True))

class User(db.Model):
    """
    Create a user table
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, autoincrement=True) #id
    openid = db.Column(db.String(128), index=True,  primary_key=True, unique=True) #openid
    nickname = db.Column(db.String(60), index=True)
    avatar_url = db.Column(db.String(128))
    
    is_admin = db.Column(db.Boolean, default=False)
    participated_activities = db.relationship('Activity', secondary=user_activity, backref='participants', lazy='dynamic')


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

    status = db.Column(db.String(20), nullable=False, default="招募人员中")
    
    initiator_id = db.Column(db.String(128), db.ForeignKey('users.openid'))

class Discussion(db.Model):
    __tablename__ = 'discussions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createtime = db.Column(db.TIMESTAMP(True), nullable=False, default=datetime.datetime.now)
    content = db.Column(db.Text, nullable=False)
    is_img = db.Column(db.Boolean, default=False)
    
    author_id = db.Column(db.String(128), db.ForeignKey('users.openid'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    def __repr__(self):
        return 'Discussion ' + str(self.id)


