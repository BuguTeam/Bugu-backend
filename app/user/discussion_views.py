import json
import time
import datetime
from flask import request, jsonify, render_template, redirect
import math
from . import user
from .. import db
from ..models import User, Activity, Discussion
from ..auth import gen_openid


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
    
def postToDict(post, requestOpenid):
    user = db.session.query(User).filter(User.openid==post.author_id).first()
    userName = user.nickname
    userAvatarUrl = user.avatar_url
    return {
        'id': post.id,
        'insertTime': datetime_toTimestamp(post.createtime),
        'content': post.content,
        'is_img': post.is_img,
        'myCommentFlag': (post.author_id == requestOpenid),
        'userName': userName,
        'userAvatarUrl': userAvatarUrl,
    }
def getAllPosts(activity_id, requestOpenid):
    all_posts = Discussion.query.filter(Discussion.activity_id==activity_id).order_by(Discussion.createtime).all()
    
    return [postToDict(p, requestOpenid) for p in all_posts]
    
@user.route('/activityDisplayer/discussion', methods=['GET', 'POST'])
def discuss():

    if request.method == 'POST':
        print(' /activityDisplayer/discussion' )
        print(request.values)
        third_session = request.values.get('third_session')
        openid = gen_openid(third_session)
        
        activity_id = int(json.loads(request.values.get('activity_id')))
        all_posts = getAllPosts(activity_id, openid)
        print('>>>  openid:   ', openid)
        print('>>>  activity_id:   ', activity_id)
        print('>>>  all_posts:   ', all_posts)
        return json.dumps(all_posts, ensure_ascii=False)
    else:
        all_posts = Discussion.query.order_by(Discussion.createtime).all()
        return render_template('discussion.html', posts=all_posts)

@user.route('/activityDisplayer/discussion/create', methods=['GET', 'POST'])
def create():

    if request.method == 'POST':
        third_session = request.values.get('third_session')
        activity_id = int(json.loads(request.values.get('activity_id')))
        content = str(json.loads(request.values.get('content')))
        is_img = bool(json.loads(request.values.get('is_img')))
        
        openid = gen_openid(third_session)
        user = db.session.query(User).filter(User.openid==openid).first()
        
        new_post = Discussion(
            content=content, 
            is_img=is_img,
            author_id=user.openid, 
            activity_id=activity_id
            )
        db.session.add(new_post)
        db.session.commit()
        return json.dumps(getAllPosts(activity_id, openid), ensure_ascii=False)
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
    