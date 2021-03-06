# tests.py

import os
import unittest
import json
import time
import datetime
from flask import abort, url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import User, Activity, Discussion


class TestBase(TestCase):

    def create_app(self):

        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql://buguadmin:bugu2020@localhost/bugubackend_test'
        )
        print('create_app done')
        return app

    def setUp(self):
        """
        Will be called before every test
        """

        db.create_all()

        # create test non-admin user
        user = User(
                openid="aaaopenid", 
                nickname="aaa",
                avatar_url="aaaurl",
                is_admin=False,
                )

        # save users to database
        db.session.add(user)
        db.session.commit()

        # create test non-admin bbb
        user = User(
            openid="bbbopenid",
            nickname="bbb",
            avatar_url="bbburl",
            is_admin=False,
        )

        # save users to database
        db.session.add(user)
        db.session.commit()
        print('setup done')

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()
        print('tearDown done')


class TestViews(TestBase):

    def test_addActivity_view(self):
        """
        Test addActivity
        """

        # test1: normal request
        self.assertEqual(Activity.query.count(), 0)
        self.assertEqual(User.query.count(), 2)

        response = self.client.post(url_for('user.addActivity'),
                                    data={
                                        'third_session': 'aaasession',
                                        'name': json.dumps('act1'),
                                        'startTime': json.dumps('2020-05-20 15:13'),
                                        'registrationDDL': json.dumps('2020-05-19 15:13'),
                                        'description': json.dumps('this is act1.'),
                                        'maxParticipantNumber': json.dumps('5'),
                                        'location': json.dumps({
                                            'name': 'loc1',
                                            'longitude': '1.1',
                                            'latitude': '2.2',
                                            'type': 'wsg64'
                                        })
                                    }
                                   )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Successfully Created')
        
        db.session.commit() # commit changes conducted in /user/addActivity
        self.assertEqual(Activity.query.count(), 1)
        act1 = Activity.query.all()
        assert act1[0].createtime is not None
        assert act1[0].currentParticipantNumber == 1
        assert act1[0].status == "招募人员中"
        assert act1[0].initiator_id == 'aaaopenid'

        # test2: registrationDDL == ""
        response = self.client.post(url_for('user.addActivity'),
                                    data={
                                        'third_session': 'aaasession',
                                        'name': json.dumps('act2'),
                                        'startTime': json.dumps('2020-05-20 15:13'),
                                        'registrationDDL': json.dumps(''),
                                        'description': json.dumps('this is act2.'),
                                        'maxParticipantNumber': json.dumps('3'),
                                        'location': json.dumps({
                                            'name': 'loc2',
                                            'longitude': '2.1',
                                            'latitude': '3.2',
                                            'type': 'wsg64'
                                        })
                                    }
                                   )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Successfully Created')
        
        db.session.commit() # commit changes conducted in /user/addActivity
        self.assertEqual(Activity.query.count(), 2)
        act2 = Activity.query.filter(Activity.title == 'act2').first()
        assert act2.createtime is not None
        assert act2.currentParticipantNumber == 1
        assert act2.status == "招募人员中"
        assert act2.initiator_id == 'aaaopenid'
        assert act2.registrationDDL == datetime.datetime.strptime("2020-05-20 15:13:00", "%Y-%m-%d %H:%M:%S")

        # test3: description == ""
        response = self.client.post(url_for('user.addActivity'),
                                    data={
                                        'third_session': 'aaasession',
                                        'name': json.dumps('act3'),
                                        'startTime': json.dumps('2020-05-19 17:13'),
                                        'registrationDDL': json.dumps('2020-05-19 15:13'),
                                        'description': json.dumps(''),
                                        'maxParticipantNumber': json.dumps('2'),
                                        'location': json.dumps({
                                            'name': 'loc3',
                                            'longitude': '3.1',
                                            'latitude': '4.2',
                                            'type': 'wsg64'
                                        })
                                    }
                                   )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Successfully Created')
        
        db.session.commit() # commit changes conducted in /user/addActivity
        self.assertEqual(Activity.query.count(), 3)
        act3 = Activity.query.filter(Activity.title == 'act3').first()
        assert act3.createtime is not None
        assert act3.currentParticipantNumber == 1
        assert act3.status == "招募人员中"
        assert act3.initiator_id == 'aaaopenid'
        assert act3.descript == ""

        # test4: registrationDDL == "" && description == ""
        response = self.client.post(url_for('user.addActivity'),
                                    data={
                                        'third_session': 'aaasession',
                                        'name': json.dumps('act4'),
                                        'startTime': json.dumps('2020-05-19 17:13'),
                                        'registrationDDL': json.dumps(''),
                                        'description': json.dumps(''),
                                        'maxParticipantNumber': json.dumps('7'),
                                        'location': json.dumps({
                                            'name': 'loc4',
                                            'longitude': '4.1',
                                            'latitude': '5.2',
                                            'type': 'wsg64'
                                        })
                                    }
                                   )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Successfully Created')
        
        db.session.commit() # commit changes conducted in /user/addActivity
        self.assertEqual(Activity.query.count(), 4)
        act4 = Activity.query.filter(Activity.title == 'act4').first()
        assert act4.createtime is not None
        assert act4.currentParticipantNumber == 1
        assert act4.status == "招募人员中"
        assert act4.initiator_id == 'aaaopenid'
        assert act4.descript == ""
        assert act4.registrationDDL == datetime.datetime.strptime("2020-05-19 17:13:00", "%Y-%m-%d %H:%M:%S")


    def test_UserActivityHistory_view(self):
        """
        Test UserActivityHistory
        """

        self.assertEqual(Activity.query.count(), 0)
        self.assertEqual(User.query.count(), 2)
        initiator = db.session.query(User).filter(User.openid=='aaaopenid').first()

        act1 = Activity(
            title='act1',
            startTime='2020-05-20 15:13:00',
            registrationDDL='2020-05-19 15:13:00',
            descript='this is act1.',
            maxParticipantNumber=5,
            currentParticipantNumber=1,
            locationName='loc1',
            locationLongitude=1.1,
            locationLatitude=2.2,
            locationType='wsg64',
            initiator_id='aaaopenid')

        initiator.participated_activities.append(act1)
        db.session.add(act1)

        act2 = Activity(
            title='act2',
            startTime='2020-05-20 15:13:00',
            registrationDDL='2020-05-20 15:13:00',
            descript='this is act2.',
            maxParticipantNumber=3,
            currentParticipantNumber=1,
            locationName='loc2',
            locationLongitude=2.1,
            locationLatitude=3.2,
            locationType='wsg64',
            initiator_id='aaaopenid')

        initiator.participated_activities.append(act2)
        db.session.add(act2)

        act3 = Activity(
            title='act3',
            startTime='2020-05-19 17:13:00',
            registrationDDL='2020-05-19 15:13:00',
            descript='',
            maxParticipantNumber=2,
            currentParticipantNumber=1,
            locationName='loc3',
            locationLongitude=3.1,
            locationLatitude=4.2,
            locationType='wsg64',
            initiator_id='aaaopenid')

        initiator.participated_activities.append(act3)
        db.session.add(act3)

        act4 = Activity(
            title='act4',
            startTime='2020-05-19 17:13:00',
            registrationDDL='2020-05-19 17:13:00',
            descript='',
            maxParticipantNumber=7,
            currentParticipantNumber=1,
            locationName='loc4',
            locationLongitude=4.1,
            locationLatitude=5.2,
            locationType='wsg64',
            initiator_id='aaaopenid')

        initiator.participated_activities.append(act4)
        db.session.add(act4)

        db.session.commit()

        # test1: normal request
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-21 17:13:00'),
                                        'status': json.dumps('全部'),
                                        'character': json.dumps('both'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)
        
        db.session.commit() # commit changes conducted in /user/UserActivityHistory

        # assert that status has been updated
        tmp4 = Activity.query.filter(Activity.title == 'act4').first()
        assert tmp4.status == "活动进行中"
        tmp3 = Activity.query.filter(Activity.title == 'act3').first()
        assert tmp3.status == "活动进行中"
        tmp2 = Activity.query.filter(Activity.title == 'act2').first()
        assert tmp2.status == "招募人员中"
        tmp1 = Activity.query.filter(Activity.title == 'act1').first()
        assert tmp1.status == "招募完毕，等待活动开始"

        data = json.loads(response.data)

        assert len(data['alist']) == 4
        assert data['alist'][0]['name'] == 'act1'
        assert data['alist'][1]['name'] == 'act2'
        assert data['alist'][2]['name'] == 'act3'
        assert data['alist'][3]['name'] == 'act4'
        assert data['lastActivityTime'] == '2020-05-19 17:13:00'

        # test2: limit < total cnt
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('1'),
                                        'lastActivityTime': json.dumps('2020-05-21 17:13:00'),
                                        'status': json.dumps('全部'),
                                        'character': json.dumps('both'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 1
        assert data['alist'][0]['name'] == 'act1'
        assert data['lastActivityTime'] == '2020-05-20 15:13:00'

        # test3: lastActivityTime < a particular activity
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-20 00:00:00'),
                                        'status': json.dumps('全部'),
                                        'character': json.dumps('both'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 2
        assert data['alist'][0]['name'] == 'act3'
        assert data['alist'][1]['name'] == 'act4'
        assert data['lastActivityTime'] == '2020-05-19 17:13:00'

        # test4: status == "招募人员中"
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-21 00:00:00'),
                                        'status': json.dumps('招募人员中'),
                                        'character': json.dumps('both'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 1
        assert data['alist'][0]['name'] == 'act2'
        assert data['lastActivityTime'] == '2020-05-20 15:13:00'

        # test5: status == "活动进行中"
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-21 00:00:00'),
                                        'status': json.dumps('活动进行中'),
                                        'character': json.dumps('both'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 2
        assert data['alist'][0]['name'] == 'act3'
        assert data['alist'][1]['name'] == 'act4'
        assert data['lastActivityTime'] == '2020-05-19 17:13:00'

        # test5: status == "招募完毕，等待活动开始"
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-21 00:00:00'),
                                        'status': json.dumps('招募完毕，等待活动开始'),
                                        'character': json.dumps('both'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 1
        assert data['alist'][0]['name'] == 'act1'
        assert data['lastActivityTime'] == '2020-05-20 15:13:00'

        # test6: character == "initiator"
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-21 00:00:00'),
                                        'status': json.dumps('全部'),
                                        'character': json.dumps('initiator'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 4

        # test7: character == "participant"
        response = self.client.post(url_for('user.UserActivityHistory'),
                                    data={
                                        'third_session': 'aaasession',
                                        'limit': json.dumps('4'),
                                        'lastActivityTime': json.dumps('2020-05-21 00:00:00'),
                                        'status': json.dumps('全部'),
                                        'character': json.dumps('participant'),
                                    }
                                   )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)

        assert len(data['alist']) == 0


    def test_discussion_create(self):
        self.assertEqual(Activity.query.count(), 0)
        self.assertEqual(User.query.count(), 2)
        initiator = db.session.query(User).filter(User.openid == 'aaaopenid').first()
        act1 = Activity(
            title='act1',
            startTime='2020-06-20 15:13:00',
            registrationDDL='2020-06-19 15:13:00',
            descript='this is act1.',
            maxParticipantNumber=5,
            currentParticipantNumber=1,
            locationName='loc1',
            locationLongitude=1.1,
            locationLatitude=2.2,
            locationType='wsg64',
            initiator_id='aaaopenid')

        initiator.participated_activities.append(act1)
        db.session.add(act1)

        act2 = Activity(
            title='act2',
            startTime='2020-06-20 15:13:00',
            registrationDDL='2020-06-20 15:13:00',
            descript='this is act2.',
            maxParticipantNumber=3,
            currentParticipantNumber=1,
            locationName='loc2',
            locationLongitude=2.1,
            locationLatitude=3.2,
            locationType='wsg64',
            initiator_id='aaaopenid')

        initiator.participated_activities.append(act2)
        db.session.add(act2)

        # test1: add message
        response = self.client.post(url_for('user.create'),
                                    data={
                                        'third_session': 'aaasession',
                                        'content': json.dumps('this is message1.'),
                                        'activity_id': json.dumps('1'),
                                        'is_img': json.dumps('false'),
                                    }
                                    )

        self.assertEqual(response.status_code, 200)

        db.session.commit()  # commit changes conducted in /user/addActivity
        self.assertEqual(Discussion.query.count(), 1)
        message1 = Discussion.query.all()
        assert message1[0].createtime is not None
        assert message1[0].id is not None
        assert message1[0].author_id == 'aaaopenid'

        # test2: add messages in different activities
        response = self.client.post(url_for('user.create'),
                                    data={
                                        'third_session': 'aaasession',
                                        'content': json.dumps('this is message2.'),
                                        'activity_id': json.dumps('2'),
                                        'is_img': json.dumps('false'),
                                    }
                                    )

        self.assertEqual(response.status_code, 200)

        db.session.commit()  # commit changes conducted in /user/addActivity
        self.assertEqual(Discussion.query.count(), 2)
        message2 = Discussion.query.filter(Discussion.content == 'this is message2.').first()
        assert message2.createtime is not None
        assert message2.id is not None
        assert message2.author_id == 'aaaopenid'

        # test3: cannot add messages in a non-exist activities
        response = self.client.post(url_for('user.create'),
                                    data={
                                        'third_session': 'aaasession',
                                        'content': json.dumps('this is message3.'),
                                        'activity_id': json.dumps('3'),
                                        'is_img': json.dumps('false'),
                                    }
                                    )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Create Failed: Activity_id not found')

        # test4: cannot add messages by a unknown user
        response = self.client.post(url_for('user.create'),
                                    data={
                                        'third_session': 'unknown',
                                        'content': json.dumps('this is message4.'),
                                        'activity_id': json.dumps('2'),
                                        'is_img': json.dumps('false'),
                                    }
                                    )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Create Fail: User not found')


    def test_discussion_display(self):

        self.assertEqual(Activity.query.count(), 0)
        self.assertEqual(User.query.count(), 2)
        initiator = db.session.query(User).filter(User.openid == 'aaaopenid').first()
        act1 = Activity(
            title='act1',
            startTime='2020-06-20 15:13:00',
            registrationDDL='2020-06-19 15:13:00',
            descript='this is act1.',
            maxParticipantNumber=5,
            currentParticipantNumber=1,
            locationName='loc1',
            locationLongitude=1.1,
            locationLatitude=2.2,
            locationType='wsg64',
            initiator_id='aaaopenid')
        initiator.participated_activities.append(act1)
        db.session.add(act1)
        act2 = Activity(
            title='act2',
            startTime='2020-06-20 15:13:00',
            registrationDDL='2020-06-20 15:13:00',
            descript='this is act2.',
            maxParticipantNumber=3,
            currentParticipantNumber=1,
            locationName='loc2',
            locationLongitude=2.1,
            locationLatitude=3.2,
            locationType='wsg64',
            initiator_id='aaaopenid')
        initiator.participated_activities.append(act2)
        db.session.add(act2)
        db.session.commit()
        message1 = Discussion(
            createtime='2020-06-19 15:13:00',
            content='this is message1.',
            is_img=False,
            author_id='aaaopenid',
            activity_id='1'
        )
        db.session.add(message1)
        message2 = Discussion(
            createtime='2020-06-21 15:13:00',
            content='this is message2.',
            is_img = False,
            author_id='aaaopenid',
            activity_id='2'
        )
        db.session.add(message2)
        message3 = Discussion(
            createtime='2020-06-20 15:13:00',
            content='this is message3.',
            is_img=False,
            author_id='aaaopenid',
            activity_id='1'
        )
        db.session.add(message3)
        message4 = Discussion(
            createtime='2020-06-18 15:13:00',
            content='this is message4.',
            is_img=False,
            author_id='bbbopenid',
            activity_id='1'
        )
        db.session.add(message4)
        db.session.commit()

        # test1: test the filter in specific activity
        response = self.client.post(url_for('user.discuss'),
                                    data={
                                        'third_session': 'aaasession',
                                        'activity_id': json.dumps('1')
                                    }
                                    )

        self.assertEqual(response.status_code, 200)
        all_posts = json.loads(response.data)
        assert len(all_posts) == 3

        # test2: test the list is ordered by createtime
        assert all_posts[0]['content'] == 'this is message4.'
        assert all_posts[1]['content'] == 'this is message1.'
        assert all_posts[2]['content'] == 'this is message3.'

        # test3: test the priorities in Discussion is correct
        assert all_posts[0]['myCommentFlag'] == False
        assert all_posts[1]['myCommentFlag'] == True
        assert all_posts[2]['myCommentFlag'] == True

        assert all_posts[0]['userName'] == "bbb"
        assert all_posts[1]['userName'] == "aaa"

        assert all_posts[0]['userAvatarUrl'] == "bbburl"
        assert all_posts[1]['userAvatarUrl'] == "aaaurl"

        # test4: show nothing if ask for a non-exist activity
        response = self.client.post(url_for('user.discuss'),
                                    data={
                                        'third_session': 'aaasession',
                                        'activity_id': json.dumps('3')
                                    }
                                    )

        self.assertEqual(response.status_code, 200)
        all_posts = json.loads(response.data)
        assert len(all_posts) == 0



if __name__ == '__main__':
    unittest.main()