import json
import time
from flask import request, jsonify
from . import user
from .. import db
from ..models import User, Activity
from ..auth import gen_openid


# 把字符串转成datetime
def string_toDatetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

# 把datetime类型转成时间戳形式
def datetime_toTimestamp(dateTime):
    return time.mktime(dateTime.timetuple())

# 把datetime类型转成string
def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

@user.route('/addActivity', methods=['GET', 'POST'])
def addActivity():
    
    if request.method == 'POST':
        title = str(json.loads(request.values.get("name")))
        startTime = str(json.loads(request.values.get("startTime")))+":00"
        registrationDDL = str(json.loads(request.values.get("registrationDDL")))+":00"
        descript = str(json.loads(request.values.get("description")))
        maxParticipantNumber = int(json.loads(request.values.get("maxParticipantNumber")))
        location = json.loads(request.values.get("location"))
        locationName = str(location["name"])
        locationLongitude = float(location["longitude"])
        locationLatitude = float(location["latitude"])
        locationType = str(location["type"])
        print(location)

        if registrationDDL == "":
            registrationDDL = startTime
        if descript == None: descript = ""
        
        act = Activity(
            title=title,
            startTime=startTime,
            registrationDDL=registrationDDL,
            descript=descript,
            maxParticipantNumber=maxParticipantNumber,
            currentParticipantNumber=1,
            locationName=locationName,
            locationLongitude=locationLongitude,
            locationLatitude=locationLatitude,
            locationType=locationType)
        db.session.add(act)
        db.session.commit()

        print('Successfully Created')
        return 'Successfully Created'
    
    return '''visiting /user/addActivity: Hi there! '''



@user.route('/getActivityList', methods=['GET', 'POST'])
def getActivityList():
    
    if request.method == 'POST':
        limit = int(json.loads(request.values.get('limit')))
        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        print('limit: ', limit)
        print('third_session: ', third_session)
        print('openid: ', openid)
        
        jsonData = []
        activities = Activity.query.order_by(Activity.startTime.desc()).limit(limit).all()
        for a in activities:
            a_dict = {
                'id': a.id,
                'name': a.title, 
                'startTime': datetime_toTimestamp(a.startTime), 
                'registrationDDL': datetime_toTimestamp(a.registrationDDL),
                'maxParticipantNumber': a.maxParticipantNumber,
                'currentParticipantNumber': a.currentParticipantNumber,
                'description': a.descript,
                'location': {
                    'name': a.locationName,
                    'longitude': a.locationLongitude,
                    'latitude': a.locationLatitude,
                },
                'password': "",
                
            }
            jsonData.append(a_dict)
        print(jsonData)
        return json.dumps(jsonData, ensure_ascii=False)

    else:
        return '''visiting /user/getActivityList: Hi there! '''
