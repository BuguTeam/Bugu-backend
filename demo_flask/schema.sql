DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS activity;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE activity (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  createTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  startTime TIMESTAMP NOT NULL,
  registrationDDL TIMESTAMP,
  descript TEXT,
  maxParticipantNumber INTEGER,
  currentParticipantNumber INTEGER NOT NULL DEFAULT 1,
  stat TEXT NOT NULL DEFAULT '招募人员中',
  locationName TEXT,
  locationLongitude REAL,
  locationLatitude REAL,
  locationType TEXT
);