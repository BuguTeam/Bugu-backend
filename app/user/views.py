# coding=utf-8

import json
import time
import datetime
from flask import request, jsonify, render_template, redirect
import math
from . import user
from .. import db
from ..models import User, Activity
from ..auth import gen_openid


# 把1km(暂定)转换成纬度差
def dis_1kmToLatitude():
    return 1.0 / 111.0


# 把1km(暂定)转换成经度差
def dis_1kmToLongitude(curLatitude):
    return 1.0 / (111.0 * abs(math.cos(curLatitude / 180.0 * math.pi)))


# 把字符串转成datetime
def string_toDatetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


# 把datetime类型转成13位的时间戳形式
def datetime_toTimestamp(dateTime):
    return time.mktime(dateTime.timetuple()) * 1000.0 + (dateTime.microsecond / 1000.0)


# 把datetime类型转成string
def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# 检查openid对应的用户是否参与了act活动，act是数据库中的一个Activity对象
def checkIfParticipated(openid, act):
    return openid in [u.openid for u in act.participants]


# 检查openid对应的用户是否发起了act活动，act是数据库中的一个Activity对象
def checkIfInitiated(openid, act):
    return openid == act.initiator_id


@user.route('/addActivity', methods=['GET', 'POST'])
def addActivity():
    print(addActivity)
    if request.method == 'POST':
        title = str(json.loads(request.values.get("name")))
        startTime = str(json.loads(request.values.get("startTime"))) + ":00"
        registrationDDL = str(json.loads(request.values.get("registrationDDL"))) + ":00"
        descript = str(json.loads(request.values.get("description")))
        maxParticipantNumber = int(json.loads(request.values.get("maxParticipantNumber")))
        location = json.loads(request.values.get("location"))
        locationName = str(location["name"])
        locationLongitude = float(location["longitude"])
        locationLatitude = float(location["latitude"])
        locationType = str(location["type"])
        # print(location)

        if registrationDDL == ":00":
            registrationDDL = startTime
        if descript == None: descript = ""

        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        initiator = db.session.query(User).filter(User.openid == openid).first()
        # if initiator is None:

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
            locationType=locationType,
            initiator_id=openid)

        # act.participants.append(initiator)
        initiator.participated_activities.append(act)

        db.session.add(act)
        db.session.commit()
        print('created activity: id=', act.id, ' participants: ', [u.openid for u in act.participants])

        print('Successfully Created')
        return 'Successfully Created'

    return '''visiting /user/addActivity: Hi there! '''


@user.route('/getActivityList', methods=['GET', 'POST'])
def getActivityList():
    print(getActivityList)
    if request.method == 'POST':
        print(request.values)
        limit = int(json.loads(request.values.get('limit')))
        third_session = request.values.get('third_session')
        lastActivityTime = str(json.loads(request.values.get('lastActivityTime')))
        openid = gen_openid(third_session)

        user_longitude = float(json.loads(request.values.get('longitude')))
        user_latitude = float(json.loads(request.values.get('latitude')))
        print('------limit: ', limit)
        print('third_session: ', third_session)
        print('openid: ', openid)
        print('------lastActivityTime: ', lastActivityTime)
        print('------user_longitude: ', user_longitude)
        print('------user_latitude: ', user_latitude)

        alist = []

        print('------: ', dis_1kmToLatitude())
        print('------: ', dis_1kmToLongitude(user_latitude))

        '''
        temporary commented for testing
        # also need location filtering
        if len(lastActivityTime) > 0:
            activities_noLocation = Activity.query.filter(Activity.startTime < string_toDatetime(lastActivityTime), Activity.locationName == '\"不限定位置\"').all()
            activities_withinRange = Activity.query.filter(Activity.startTime < string_toDatetime(lastActivityTime), Activity.locationLongitude < user_longitude + dis_1kmToLongitude(user_latitude), Activity.locationLongitude > user_longitude - dis_1kmToLongitude(user_latitude), Activity.locationLatitude < user_latitude + dis_1kmToLatitude(), Activity.locationLatitude > user_latitude - dis_1kmToLatitude(), Activity.locationName != '\"不限定位置\"').all()
        else:
            activities_noLocation = Activity.query.filter(Activity.locationName == '\"不限定位置\"').all()
            activities_withinRange = Activity.query.filter(Activity.locationLongitude < user_longitude + dis_1kmToLongitude(user_latitude), Activity.locationLongitude > user_longitude - dis_1kmToLongitude(user_latitude), Activity.locationLatitude < user_latitude + dis_1kmToLatitude(), Activity.locationLatitude > user_latitude - dis_1kmToLatitude(), Activity.locationName != '\"不限定位置\"').all()

        activities = activities_noLocation + activities_withinRange
        '''

        if len(lastActivityTime) > 0:
            activities = Activity.query.filter(Activity.startTime < string_toDatetime(lastActivityTime)).all()
        else:
            activities = Activity.query.all()

        def getStartTime(a):
            return a.startTime

        activities.sort(key=getStartTime, reverse=True)
        # activities = activities[0:limit]

        cnt = 0

        for a in activities:
            # update STATUS of activity before return
            currentTime = datetime.datetime.now()
            update = False
            if a.status == "招募人员中":
                if a.registrationDDL <= currentTime:
                    a.status = "招募完毕，等待活动开始"
                    update = True
                if a.startTime <= currentTime:
                    a.status = "活动进行中"
                    update = True
            elif a.status == "招募完毕，等待活动开始":
                if a.startTime <= currentTime:
                    a.status = "活动进行中"
                    update = True

            if update:
                db.session.commit()

            print('  db results: ', a, a.status)

            if a.status != "招募人员中":
                continue

            cnt += 1

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
                    'type': a.locationType,
                },
                'status': a.status,
                'hasParticipated': checkIfParticipated(openid, a),
                'hasInitiated': checkIfInitiated(openid, a),
            }
            alist.append(a_dict)
            if len(lastActivityTime) == 0 or string_toDatetime(lastActivityTime) > a.startTime:
                lastActivityTime = datetime_toString(a.startTime)
            if cnt == limit:
                break

        jsonData = {}
        jsonData['alist'] = alist
        jsonData['lastActivityTime'] = lastActivityTime
        print('------returns actlist: ', jsonData)
        return json.dumps(jsonData, ensure_ascii=False)

    else:
        return '''visiting /user/getActivityList: Hi there! '''


@user.route('/UserActivityHistory', methods=['GET', 'POST'])
def UserActivityHistory():
    print(UserActivityHistory)
    if request.method == 'POST':
        print(request.values)
        character = str(json.loads(request.values.get('character')))
        status = str(json.loads(request.values.get('status')))
        limit = int(json.loads(request.values.get('limit')))
        third_session = request.values.get('third_session')
        lastActivityTime = str(json.loads(request.values.get('lastActivityTime')))
        openid = gen_openid(third_session)
        user = db.session.query(User).filter(User.openid == openid).first()

        print('------character: ', character)
        print('------status: ', status)
        print('------limit: ', limit)
        print('third_session: ', third_session)
        print('openid: ', openid)
        print('------lastActivityTime: ', lastActivityTime)

        activities = user.participated_activities.order_by(Activity.startTime.desc())

        cnt = 0
        alist = []
        ceilTime = lastActivityTime
        for a in activities:
            print('  db results: ', a)
            if len(ceilTime) > 0 and a.startTime >= string_toDatetime(ceilTime):
                continue

            if character == "initiator" and a.initiator_id != openid:
                continue
            if character == "participant" and a.initiator_id == openid:
                continue

            # update STATUS of activity before return
            # "招募人员中", "招募完毕，等待活动开始", "活动进行中", "活动已结束", "已取消", "全部"
            currentTime = datetime.datetime.now()
            update = False
            if a.status == "招募人员中":
                if a.registrationDDL <= currentTime:
                    a.status = "招募完毕，等待活动开始"
                    update = True
                if a.startTime <= currentTime:
                    a.status = "活动进行中"
                    update = True
            elif a.status == "招募完毕，等待活动开始":
                if a.startTime <= currentTime:
                    a.status = "活动进行中"
                    update = True

            if update:
                db.session.commit()

            if status != "全部" and status != a.status:
                continue

            cnt += 1

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
                    'type': a.locationType,
                },
                'status': a.status,
                'hasParticipated': checkIfParticipated(openid, a),
                'hasInitiated': checkIfInitiated(openid, a),
            }
            alist.append(a_dict)

            if len(lastActivityTime) == 0 or string_toDatetime(lastActivityTime) > a.startTime:
                lastActivityTime = datetime_toString(a.startTime)

            if cnt == limit:
                break

        jsonData = {}
        jsonData['alist'] = alist
        jsonData['lastActivityTime'] = lastActivityTime
        print('------returns actlist: ', jsonData)
        return json.dumps(jsonData, ensure_ascii=False)

    else:
        return '''visiting /user/UserActivityHistory: Hi there! '''


@user.route('/activityDisplayer', methods=['GET'])
def activityDisplay():
    return render_template('test.html')


@user.route('/joinActivity', methods=['GET', 'POST'])
def joinActivity():
    print(joinActivity)
    if request.method == 'POST':
        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        activity_id = int(json.loads(request.values.get("activity_id")))

        user = db.session.query(User).filter(User.openid == openid).first()
        activity = db.session.query(Activity).filter(Activity.id == activity_id).first()

        # Assume location filter already done in getActivityList
        # Check whether registration deadline has passed
        if activity.registrationDDL <= datetime.datetime.now():
            print('Fail to join')
            return 'Fail to join'
        # Check if maximum participant number has been met
        if activity.maxParticipantNumber != -1 and activity.maxParticipantNumber <= activity.currentParticipantNumber:
            print('Fail to join')
            return 'Fail to join'
        # Check the status of activity
        if activity.status != "招募人员中":
            print('Fail to join')
            return 'Fail to join'

        # All criteria met, add the user
        user.participated_activities.append(activity)
        activity.currentParticipantNumber += 1
        db.session.commit()
        print('Successfully join')
        return 'Successfully join'

    else:
        return '''visiting /user/joinActivity: Hi there! '''


@user.route('/exitfromActivity', methods=['GET', 'POST'])
def exitfromActivity():
    print(exitfromActivity)
    if request.method == 'POST':
        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        activity_id = int(json.loads(request.values.get("activity_id")))

        user = db.session.query(User).filter(User.openid == openid).first()
        activity = db.session.query(Activity).filter(Activity.id == activity_id).first()

        # initiator cancel an activity
        if activity.initiator_id == user.openid:
            activity.status = "已取消"
        # participant exit from an activity
        else:
            if activity.registrationDDL <= datetime.datetime.now():  # registration ddl reached, cannot exit
                print('Registration DDL reached, cannot exit!')
                return 'Registration DDL reached, cannot exit!'
            user.participated_activities.remove(activity)
            activity.currentParticipantNumber -= 1

        db.session.commit()

        print('Successfully exit')
        return 'Successfully exit'

    else:
        return '''visiting /user/exitfromActivity: Hi there! '''


@user.route('/finishActivity', methods=['GET', 'POST'])
def finishActivity():
    print(finishActivity)
    if request.method == 'POST':
        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        activity_id = int(json.loads(request.values.get("activity_id")))

        user = db.session.query(User).filter(User.openid == openid).first()
        activity = db.session.query(Activity).filter(Activity.id == activity_id).first()

        # initiator finish an activity
        if activity.initiator_id == user.openid:
            if activity.startTime > datetime.datetime.now():    # hasn't started
                print("Activity ", activity_id, "hasn't started, cannot be finished.")
                return "The activity hasn't started."
            activity.status = "活动已结束"
        # not initiator
        else:
            print("User(not initiator) ", openid, "tried to finish activity ", activity_id)
            return 'You are not the initiator. Fail to finish.'

        db.session.commit()

        print('Successfully finish')
        return 'Successfully finish'

    else:
        return '''visiting /user/finishActivity: Hi there! '''
