#!/usr/bin/env python

__author__ = 'abhinandanramesh@gmail.com (Abhinandan Kelgere Ramesh)'

import cgi
import urllib
import webapp2
import datetime
import json
import wsgiref.handlers

from google.appengine.api import urlfetch
from google.appengine.ext import db
from Model import *
from joulejotter import *

import time
import calendar
import datetime
import httplib2

from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

#from mapreduce.lib import files
from mapreduce import base_handler
from mapreduce import mapreduce_pipeline

from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials

SCOPE = 'https://www.googleapis.com/auth/bigquery'
PROJECT_ID = 'batterystat'
BQ_DATASET_ID = 'datastore_battery_data'
GS_BUCKET = 'joulejotter-battery'
ENTITY_KIND = 'Model.BatteryInfoDB'

class DatastoreMapperPipeline(base_handler.PipelineBase):
  	def run(self, entity_type):
    		output = yield mapreduce_pipeline.MapperPipeline(
	      	"Datastore Mapper %s" % entity_type,
      		"joulejotter.datastore_map",
      		"mapreduce.input_readers.DatastoreInputReader",
      		output_writer_spec="mapreduce.output_writers.FileOutputWriter",
      		params={
        		  "input_reader":{
        		      "entity_kind": entity_type,
        		      },
        		  "output_writer":{
        		      "filesystem": "gs",
        		      "gs_bucket_name": GS_BUCKET,
        		      "output_sharding":"none",
        		      }
        		  },
        		  shards=12)
    		yield CloudStorageToBigQuery(output)


class CloudStorageToBigQuery(base_handler.PipelineBase):
	  def run(self, csv_output):

	    credentials = AppAssertionCredentials(scope=SCOPE)
	    http = credentials.authorize(httplib2.Http())
	    bigquery_service = build("bigquery", "v2", http=http)
   
	    jobs = bigquery_service.jobs()
	    table_name = 'datastore_data_battery'
	    files = [str(f.replace('/gs/', 'gs://')) for f in csv_output]
	    result = jobs.insert(projectId=PROJECT_ID,
        	                body=build_job_data(table_name,files))
    	    result.execute()


def build_job_data(table_name, files):
	  return {"projectId": PROJECT_ID,
	          "configuration":{
	              "load": {
	                  "sourceUris": files,
	                  "schema":{
	                      "fields":[
        	                  {
        	                      "name":"Voltage",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"Temperature",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"Status",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"Type",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"Plugged",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"IMEI",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"Timestamp",
        	                      "type":"INTEGER",
        	                  },
        	                  {
        	                      "name":"Level",
        	                      "type":"STRING",
        	                  },
        	                  {
        	                      "name":"Health",
        	                      "type":"STRING",
        	                  }
        	                  ]
        	              },
        	          "destinationTable":{
        	              "projectId": PROJECT_ID,
        	              "datasetId": BQ_DATASET_ID,
        	              "tableId": table_name,
        	              },
        	          "maxBadRecords": 0,
        	          }
        	      }
        	  }


def datastore_map(entity_type):
	  data = db.to_dict(entity_type)
	  resultlist = [data.get('Voltage'),
			data.get('Temperature'),
			data.get('Status'),
			data.get('Type'),
			data.get('Plugged'),
			data.get('IMEI'),
			data.get('Level'),
        	        timestamp_to_posix(data.get('Timestamp')),
        	        data.get('Health')]
	  result = ','.join(['"%s"' % field for field in resultlist])
	  yield("%s\n" % result)
  
  
def timestamp_to_posix(timestamp):
	  return int(time.mktime(timestamp.timetuple()))


class DatastoretoBigQueryStart(webapp.RequestHandler):
	  def get(self):
	    pipeline = DatastoreMapperPipeline(ENTITY_KIND)
	    pipeline.start()
	    path = pipeline.base_path + "/status?root=" + pipeline.pipeline_id
	    self.redirect(path)

   
class AddDataHandler(webapp.RequestHandler):
	  def get(self):
	    
	    self.response.out.write('<a href="/start">Click here</a> to start the Datastore to BigQuery pipeline.')
