#!/usr/bin/env python

import cgi
import urllib
import webapp2
import datetime
import json
import wsgiref.handlers

from google.appengine.api import urlfetch
from google.appengine.ext import db
from Model import *

class DataHandle(webapp2.RequestHandler):					

	def storeCSSData(self, jj_id, device_name, time_stamp_unix, current_consumed, voltage_value, power_value, powerfactor_value):

		temp_time=float(time_stamp_unix)
		time_stamp = datetime.datetime.fromtimestamp(temp_time)

		if (not jj_id):
			jj_id = 'Nil'

		e = CSServerDB(JJ_ID = str(jj_id),
			       device = str(device_name),
	 	               timestamp = time_stamp,
	 	               current = str(current_consumed),
			       voltage = str(voltage_value),
			       apparent_power = str(power_value),
			       powerfactor = str(powerfactor_value),
			       unixtime = int(time_stamp_unix)) 
		e.put()

	def processCSSData(self, raw_content, time_max):

		lines = raw_content.splitlines()	

	        for line in lines:
		   	line=line.strip()
			parts = line.split(";")
			jj_id = parts[0]
			device_name = parts[1]
			time_stamp_unix = parts[2]
			current_consumed = parts[3]
			voltage_value = parts[4]
			power_value = parts[5]
			powerfactor_value = parts[6]

		        if int(time_stamp_unix) > time_max:
			    self.storeCSSData(jj_id,device_name,time_stamp_unix,current_consumed,voltage_value,power_value,powerfactor_value)

	def fetchCSSData(self, url, devicelist, time_max):

		result = urlfetch.fetch(url)
		device_data_out = db.GqlQuery("SELECT unixtime FROM CSServerDB WHERE device IN :1 ORDER BY timestamp DESC LIMIT 1",
                                	  devicelist)

		for b in device_data_out:
			time_max = b.unixtime

		if (not time_max):
			time_max = 1

		if result.status_code == 200: 
	   		self.processCSSData(result.content,time_max)
		else:
	   		self.redirect('/cs')

        
	def storeBatteryData(self, time_stamp, voltage, temperature, status, kind, source, unique_id, level, health):

		temp_time = datetime.datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S")

		e = BatteryInfoDB(Timestamp = temp_time,
				  Voltage = str(voltage),
				  Temperature = str(temperature),
	 	            	  Status = str(status),
	 	            	  Type = str(kind),
				  Plugged = str(source),
				  IMEI = str(unique_id),
				  Level = str(level),
				  Health = str(health)) 
		e.put()

	def processBatteryData(self, data):
		battery_data = json.loads(data)

		status = battery_data['Status']
		voltage = battery_data['Voltage']
		temperature = battery_data['Temperature']
		time_stamp = battery_data['Timestamp']
		kind = battery_data['Type']
		source = battery_data['Plugged']
		unique_id = battery_data['IMEI']
		level = battery_data['Level']
		health = battery_data['Health']

		self.storeBatteryData(time_stamp, voltage, temperature, status, kind, source, unique_id, level, health)

	def storeSDCardData(self, device_name, time_stamp_unix, current_consumed, voltage_value, power_value, powerfactor_value):

		time_stamp = datetime.datetime.fromtimestamp(float(time_stamp_unix))

		jj_id = 'Nil'

		e = SDCardDB(JJ_ID = str(jj_id),
			     device = str(device_name),
	 	             timestamp = time_stamp,
	 	             current = str(current_consumed),
		 	     voltage = str(voltage_value),
			     apparent_power = str(power_value),
			     powerfactor = str(powerfactor_value),
			     unixtime = int(time_stamp_unix)) 
		e.put()

	def processSDCardData(self, raw_content, time_max):

                raw_content = json.loads(raw_content)

		if (not time_max):
			time_max = 1

                for Data in raw_content:
	                Data = Data.split(';')[1:-1]
        	        device_name = Data[0]
        	        time_stamp_unix = Data[1]
        	        current_consumed = Data[2]
        	        voltage_value = Data[3]
        	        power_value = Data[4]
        	        powerfactor_value = Data[5]
		        self.storeSDCardData(device_name,time_stamp_unix,current_consumed,voltage_value,power_value,powerfactor_value)


class BatteryDataReceive(DataHandle):
	def post(self):
		data = self.request.body
		self.processBatteryData(data)	

class SDCardDataReceive(DataHandle):
	def post(self):
		time_max = 1
		jjData = self.request.body
		self.processSDCardData(jjData, time_max)

class CSServerDataHandle(DataHandle):
    	def get(self):
		time_max = 1
		
		url = "http://www.commonsensenet.in/JJdata/UPSOUT.txt"

		device_list_out = ["UPSOUT"]

		url_in = "http://www.commonsensenet.in/JJdata/UPSIN.txt"
	
		device_list_in = ["UPSIN"]

		self.fetchCSSData(url, device_list_out, time_max)
	
		self.fetchCSSData(url_in, device_list_in, time_max)

	
application = webapp2.WSGIApplication([
    (r'/cs', CSServerDataHandle),
    (r'/battery', BatteryDataReceive),
    (r'/sdcard', SDCardDataReceive),
], debug=True)
