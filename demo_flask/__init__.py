import os
from flask import Flask,render_template,request,json
from . import db
import datetime
import time

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'demo_flask.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)

# 下面三个方法没有用到
# 把字符串转成datetime
def string_toDatetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

# 把datetime类型转成时间戳形式
def datetime_toTimestamp(dateTime):
    return time.mktime(dateTime.timetuple())

# 把datetime类型转成string
def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@app.route('/addActivity', methods=['GET', 'POST'])
def addActivity():
    if request.method == 'POST':
        title = request.form["title"]
        startTime = request.form["startTime"]
        registrationDDL = request.form["registrationDDL"]
        #startTime = datetime_toTimestamp(string_toDatetime(request.form["startTime"]))
        #registrationDDL = request.form["registrationDDL"]
        #if registrationDDL != "":
        #    registrationDDL = datetime_toTimestamp(string_toDatetime(registrationDDL))
        descript = request.form["description"]
        maxParticipantNumber = int(request.form["maxParticipantNumber"])

        locationName = request.form["locationName"]
        locationLongitude = float(request.form["locationLongitude"])
        locationLatitude = float(request.form["locationLatitude"])
        locationType = request.form["locationType"]

        # json格式request的处理：
        #data = json.loads(request.get_data(as_text=True))
        #title = data["name"]
        #startTime = datetime_toTimestamp(string_toDatetime(data["startTime"]))
        #registrationDDL = data["registrationDDL"]
        #if registrationDDL != "":
            #registrationDDL = datetime_toTimestamp(string_toDatetime(registrationDDL))
        #descript = data["description"]
        #maxParticipantNumber = int(data["maxParticipantNumber"])
        #location = data["location"]
        #locationName = location["name"]
        #locationLongitude = float(location["locationLongitude"])
        #locationLatitude = float(location["locationLatitude"])
        #locationType = location["locationType"]

        database = db.get_db()
        if registrationDDL != "":
            database.execute(
                'INSERT INTO activity (title, startTime, registrationDDL, descript, maxParticipantNumber, locationName, locationLongitude, locationLatitude, locationType)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (title, startTime, registrationDDL, descript, maxParticipantNumber, locationName, locationLongitude, locationLatitude, locationType)
            )
        else:
            database.execute(
                'INSERT INTO activity (title, startTime, descript, maxParticipantNumber, locationName, locationLongitude, locationLatitude, locationType)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (title, startTime, descript, maxParticipantNumber, locationName, locationLongitude, locationLatitude, locationType)
            )
        database.commit()
    
    return render_template('addActivity.html')



@app.route('/getActivityList', methods=['GET', 'POST'])
def getActivityList():
    if request.method == 'POST':
        limit = int(request.form["limit"])
        time = request.form["time"]

        # json格式request的处理：
        #data = json.loads(request.get_data(as_text=True))
        #limit = int(data["limit"])
        #time = data["time"]

        activities = db.get_db().execute(
            'SELECT title, createTime, startTime, registrationDDL, descript, maxParticipantNumber, currentParticipantNumber, stat, locationName, locationLongitude, locationLatitude, locationType'
            ' FROM activity'
            ' WHERE createTime < ?'
            ' ORDER BY createTime DESC',
            (time,)
        ).fetchall()

        jsonData = []
        cnt = 0
        for row in activities:
            if cnt == limit:
                break
            cnt += 1

            result = {} 
            result['name'] = str(row[0])
            result['createTime'] = row[1]
            result['startTime'] = row[2]
            result['registrationDDL'] = row[3]
            #result['startTime'] = datetime_toString(datetime.datetime.fromtimestamp(row[2]))
            #result['registrationDDL'] = datetime_toString(datetime.datetime.fromtimestamp(row[3]))
            result['description'] = str(row[4])
            result['maxParticipantNumber'] = row[5]
            result['currentParticipantNumber'] = row[6]
            result['status'] = str(row[7])
            location = {}
            location['locationName'] = str(row[8])
            location['locationLongitude'] = row[9]
            location['locationLatitude'] = row[10]
            location['locationType'] = str(row[11])
            result['location'] = location
            jsonData.append(result)

        return render_template('activities.html', data=jsonData)

    else:
        return render_template('getActivityList.html')