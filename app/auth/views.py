# app/auth/views.py

import json
import requests
import traceback
from flask import request, current_app, jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import auth
from .. import db
from ..models import User

def gen_3rd_session(openid):
    '''
    Generate 3rd_session with openid
    '''
    s = Serializer(current_app.config['SECRET_KEY']) #expires_in?
    third_session = s.dumps({'openid': openid})
    return third_session

def gen_openid(third_session):
    return 'aaaopenid'
    #s = Serializer(current_app.config['SECRET_KEY'])
    #openid = s.loads(third_session)['openid']
    #return openid
    
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        # wx.login接口获得的临时登陆凭证jscode
        jscode = request.get_json()['code']
        secret = current_app.config['APP_SECRET']
        appid = current_app.config['APP_ID']
        
        print('received ', jscode, ' ' ,secret, ' ', appid)
        
        
        # ref: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
        res = requests.get('https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (appid, secret, jscode)).content
        res = json.loads(res)

        session_key = res['session_key']
        openid = res['openid']
        print('openid: ', openid)
        
        ret = {}
        ret['third_session'] = bytes.decode(gen_3rd_session(openid))
        print('returns: ', ret)
        return jsonify(ret)
        
    return '''visiting /auth/login: Hi there! '''

@auth.route('/register', methods=['GET', 'POST'])
def registerUserInfo():
    print('registerUserInfo')
    if request.method == 'POST':
        print('registerUserInfo')
        jsonData = request.get_json()
        third_session = jsonData['third_session']
        openid = gen_openid(third_session)
        
        print('receives userInfo ', jsonData)
        print('openid: ', openid)
        u = db.session.query(User).filter(User.openid==openid).first()
        print('user: ', u)
        if u is None:
            # Add user info.
            u = User(
                openid=openid, 
                nickname=jsonData['nickname'],
                avatar_url=jsonData['avatar_url'],
                is_admin=False,
                )
            try: 
                db.session.add(u)
                db.session.commit()
                print('successfully added a new user')
            except:
                traceback.print_exc()
        else:
            # Edit user info.
            u.nickname = jsonData['nickname']
            u.avatar_url = jsonData['avatar_url']
            
            db.session.commit()
            print('successfully edited user info')
        
        return 'Success'
        
    return '''visiting /auth/register: Hi there! '''


