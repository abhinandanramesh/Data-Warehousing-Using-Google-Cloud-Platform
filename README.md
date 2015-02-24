# Data-Warehousing-Using-Google-Cloud-Platform
Google-App-Engine back end for crowd sourcing the data

Receives and stores data about battery power consumption, scrapes the data about the energy consumption of various electronic devices from a remote server over HTTP post.

Hosted on Google app engine. 

Data is stored in nosql Google's datastore. The data is further loaded into Google's big query to perform convex optimization using big query API's and can also be extracted as CSV from the Google cloud storage.

MAp reduce jobs are written using Google's map reduce API's to perform parallel computation on various machines. (For this to work, the data centre should be equipped with a cluster of processors)

Follow the procedures at https://cloud.google.com/bigquery/articles/datastoretobigquery for environment set up. 

Google app engine SDK, python 3.0 or above, Google python API client library and map reduce library.

Enjoy posting data and run analysis using Panda or other data analysis frameworks using Google compute engine.
