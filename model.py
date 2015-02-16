from google.appengine.ext import db

class BatteryInfoDB(db.Model):
	Voltage = db.StringProperty(required=True)
	Temperature = db.StringProperty(required=True)
  Timestamp = db.DateTimeProperty(required=True)
  Status = db.StringProperty(required=True)
	Type = db.StringProperty(required=True)
	Plugged = db.StringProperty(required=True)
	IMEI = db.StringProperty(required=True) 
	Level = db.StringProperty(required=True)
	Health = db.StringProperty(required=True)

class CSServerDB(db.Model):
	JJ_ID = db.StringProperty(required=True)
  device = db.StringProperty(required=True)
  timestamp = db.DateTimeProperty(required=True)
  current = db.StringProperty(required=True)
	voltage = db.StringProperty(required=True)
	apparent_power = db.StringProperty(required=True)
	powerfactor = db.StringProperty(required=True) 
	unixtime = db.IntegerProperty(required=True)

class SDCardDB(db.Model):
	JJ_ID = db.StringProperty(required=True)
  device = db.StringProperty(required=True)
  timestamp = db.DateTimeProperty(required=True)
  current = db.StringProperty(required=True)
	voltage = db.StringProperty(required=True)
	apparent_power = db.StringProperty(required=True)
	powerfactor = db.StringProperty(required=True)
	unixtime = db.IntegerProperty(required=True)
