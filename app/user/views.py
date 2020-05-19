import json
import time
import datetime
from flask import request, jsonify, render_template, redirect
from . import user
from .. import db
from ..models import User, Activity, Discussion
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
        db.session.commit()

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

    if request.method == 'POST':
        post_activity = int(request.form['activity_id'])
        all_posts = Discussion.query.filter(Discussion.activity_id==post_activity).order_by(Discussion.createtime).all()
        return render_template('discussion.html', posts=all_posts)
    else:
        all_posts = Discussion.query.order_by(Discussion.createtime).all()
        return render_template('discussion.html', posts=all_posts)

@user.route('/activityDisplayer/discussion/create', methods=['GET', 'POST'])
def create():

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        post_activity = request.form['activity_id']
        new_post = Discussion(title=post_title, content=post_content, author=post_author, activity_id=int(post_activity))
        db.session.add(new_post)
        db.session.commit()
        return redirect('/user/activityDisplayer/discussion')
    else:
        return render_template('create.html')

@user.route('/activityDisplayer/discussion/delete/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    post = Discussion.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/user/activityDisplayer/discussion')

@user.route('/activityDisplayer/discussion/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Discussion.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.author = request.form['author']
        post.activity_id = int(request.form['activity_id'])
        db.session.commit()
        return redirect('/user/activityDisplayer/discussion')
    else:
        return render_template('edit.html', post=post)