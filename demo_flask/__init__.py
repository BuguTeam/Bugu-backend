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

        print('Successfully Created')
        return 'Successfully Created'
    
    return render_template('addActivity.html')



@app.route('/getActivityList', methods=['GET', 'POST'])
def getActivityList():
    if request.method == 'POST':
        limit = int(json.loads(request.values.get("limit")))

        activities = db.get_db().execute(
            'SELECT id, title, createTime, startTime, registrationDDL, descript, maxParticipantNumber, currentParticipantNumber, stat, locationName, locationLongitude, locationLatitude, locationType'
            ' FROM activity'
            ' ORDER BY createTime DESC'
        ).fetchall()

        jsonData = []
        cnt = 0
        for row in activities:
            if cnt == limit:
                break
            cnt += 1

            result = {}
            result['id'] = str(row[0])
            result['name'] = str(row[1])
            result['createTime'] = row[2]
            result['startTime'] = row[3]
            result['registrationDDL'] = row[4]
            #result['startTime'] = datetime_toString(datetime.datetime.fromtimestamp(row[2]))
            #result['registrationDDL'] = datetime_toString(datetime.datetime.fromtimestamp(row[3]))
            result['description'] = str(row[5])
            result['maxParticipantNumber'] = row[6]
            result['currentParticipantNumber'] = row[7]
            result['status'] = str(row[8])
            location = {}
            location['name'] = str(row[9])
            location['longitude'] = row[10]
            location['latitude'] = row[11]
            location['type'] = str(row[12])
            result['location'] = location
            jsonData.append(result)

        print(jsonData)
        return json.dumps(jsonData, ensure_ascii=False)

    else:
        return render_template('getActivityList.html')