import json
import time
import datetime
from flask import request, jsonify, render_template
from . import user
from .. import db
from ..models import User, Activity, Message
from ..auth import gen_openid, gen_3rd_session


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
    print(addActivity)
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
        # print(location)

        if registrationDDL == ":00":
            registrationDDL = startTime
        if descript == None: descript = ""
        
        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        initiator = db.session.query(User).filter(User.openid==openid).first()
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
        # db.session.commit()

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
        print('------limit: ', limit)
        print('third_session: ', third_session)
        print('openid: ', openid)
        print('------lastActivityTime: ', lastActivityTime)
        
        alist = []
        # TODO: also need location filtering
        if len(lastActivityTime) > 0:
            activities = Activity.query.filter(Activity.startTime < string_toDatetime(lastActivityTime)).order_by(Activity.startTime.desc()).limit(limit).all()
        else:
            activities = Activity.query.order_by(Activity.startTime.desc()).limit(limit).all()
            
        for a in activities:
            # TODO: update STATUS of activity before return

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
                'initiator': a.initiator_id,
                'participants': [bytes.decode(gen_3rd_session(u.openid)) for u in a.participants],
                
            }
            alist.append(a_dict)
            if len(lastActivityTime) == 0 or string_toDatetime(lastActivityTime) > a.startTime:
                lastActivityTime = datetime_toString(a.startTime)
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
        user = db.session.query(User).filter(User.openid==openid).first()

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
                res = db.session.query(Activity).filter(Activity.id == a.id).update({"status":a.status})
                # db.session.commit()
            
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
                'initiator': a.initiator_id,
                'participants': [bytes.decode(gen_3rd_session(u.openid)) for u in a.participants],
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



@user.route('/activityDisplayer', methods=['GET'])
def activityDisplay():
    return render_template('test.html')

@user.route('/activityDisplayer/discussion', methods=['GET', 'POST'])
def discuss():
    print(request.values)
    if request.method == 'POST':
        sourceid = int(json.loads(request.values.get('sourceid')))
        limited = int(json.loads(request.values.get('limited')))
        offset = int(json.loads(request.values.get('offset')))
        comments = Message.query.filter(Message.sourceid==sourceid).order_by(Message.createtime).all()
        clist = []
        cnt = 0

        limited += offset + 1
        # pick c in [offset, limited)
        for c in comments:
            cnt += 1
            if (cnt <= offset):
                continue
            if( cnt == limited):
                break

            poster = User.query.filter(User.openid==c.userId).first()
            replycomment = Message.query.filter(Message.id==c.replyCommentId).first()
            replyer = User.query.filter(User.openid==replycomment.userId)

            c_dict = {
                'sourceId': c.souceId,
                'createTime': c.createTime,
                'comment': c.comment,
                'replyCommentId': c.replyCommentId,
                'replyUserName': replyer.nickname,
                'third_session': gen_3rd_session(c.userId),
                'userPhoto': poster.avatar_url
            }
            clist.append(c_dict)

        jsonData = {}
        jsonData['clist'] = clist
        return json.dumps(jsonData, ensure_ascii=False)

    else:
        return '/activityDisplayer/discussion Hi here'

@user.route('/activityDisplayer/discussion/create', methods=['GET', 'POST'])
def create():

    if request.method == 'POST':
        sourceId = int(json.loads(request.values.get("sourceId")))
        comment = str(json.loads(request.values.get("comment")))
        replyCommentId = int(json.loads(request.values.get("replyCommentId")))

        # if cannot find replyCommentId in db
        replycomment = Message.query.filter(Message.id==replyCommentId).first()
        if(replycomment == []):
            return 'Message Created Fail: no such replyComment'

        third_session = str(json.loads(request.values.get("third_session")))
        userId = gen_openid(third_session)
        new_message = Message(comment=comment, replyCommentId=replyCommentId, userId=userId, sourceId=sourceId)
        db.session.add(new_message)
        db.session.commit()
        return 'Message Successfully Created'
    else:
        return '/activityDisplayer/discussion/create Hi here'

@user.route('/activityDisplayer/discussion/delete/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    message = Message.query.get_or_404(id)
    third_session = str(json.loads(request.values.get("third_session")))
    userId = gen_openid(third_session)
    if(message.userId != userId):
        return ''' Delete Fail: Cannot delete other's message '''
    else:
        db.session.delete(message)
        db.session.commit()
        return '/activityDisplayer/discussion/delete/<int:id> Hi here'

@user.route('/activityDisplayer/discussion/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    message = Message.query.get_or_404(id)
    if request.method == 'POST':
        third_session = str(json.loads(request.values.get("third_session")))
        userId = gen_openid(third_session)
        if(userId != message.userId):
            return ''' Edit Fail: Cannot edit other's message '''
        else:
            message.comment = str(json.loads(request.values.get("comment")))
            db.session.commit()
            return 'Edit Successfully'
    else:
        return '/activityDisplayer/discussion/edit/<int:id> Hi here'