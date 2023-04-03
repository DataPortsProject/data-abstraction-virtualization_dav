# import the libraries and tools necessary
from pyspark.sql import SparkSession
from datetime import datetime
import time
from pyspark import SparkConf
from pyspark.sql import SparkSession
import pyspark.sql.window as psw
import pyspark.sql.functions as psf
import pyspark.sql.functions as F
from pyspark.sql.functions import udf, col, explode
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, ArrayType
import requests
import json
from pyspark.sql import Row
# explicitly declare round() (function for rounding values) cause of overlapings with pyspark's functions
import builtins
round = getattr(builtins, "round")

import findspark
findspark.add_packages('org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')

def changeColTypes(ds, dicter, marked):
    for colu in ds.columns:
        ds = ds.withColumn(colu,col(colu).cast("string"))
    for colu, type in dicter.items():
        if(type == "timestamp"):
            #ds = ds.withColumn(colu,to_utc_timestamp(col(colu), "CET"))
            #ds = ds.withColumn(colu,to_timestamp(col(colu)))
            # SPECIFIC TO THE FORMAT OF PCS PORT CALLS STRING DATES (the 'format' parameter specifies the exisitng form>
            if(marked == 1):
                ds = ds.withColumn(colu, to_timestamp(colu, format='yyyy-MM-dd HH:mm:ss.SSS').cast(TimestampType()))
            else:
                ds = ds.withColumn(colu, to_timestamp(colu, format='MM/dd/yyyy, HH:mm:ss').cast(TimestampType()))
            #ds = ds.withColumn(colu, F.date_format( F.coalesce( F.to_timestamp(col(colu)), F.to_timestamp(col(colu), '>
        else:
            ds = ds.withColumn(colu,col(colu).cast(type))
    return ds

# function to remove whitespaces from the cells of all alphanumeric columns
def removeWhiteSpaces(ds):
    for item in ds.dtypes:
        if(item[1] == "string"):
            # remove whitespaces and merge strings inside the cell
            ds = ds.withColumn(item[0], regexp_replace(col(item[0]), " ", ""))
            ds = ds.withColumn(item[0], trim(col(item[0])))
    return ds

# function to replace cells containing no or 'NULL' values, with the alphanumeric 'nan'
def removeEmptyNulls(ds):
    ds = ds.replace("NULL", 'nan')
    ds = ds.replace(" ", 'nan')
    ds = ds.replace("", 'nan')
    # use the native dataframe.na.fill() command,
    # even if the three commands above already do the trick
    ds = ds.na.fill(value='nan')
    return ds

# TIMESTAMP FORMAT CONVERSION HAPPENS AUTOMATICALLY DURING TIMESTAMP TYPE CASTING
# function to convert timestamp columns to the given datetime format
# Furthermore, remove rows with empty datetime cells
def convertCleanDatetime(ds):
    for item in ds.dtypes:
        if(item[1] == "timestamp"):
            # convert to Datetime format, based on metadata's given input
            # it creates string columns
            ds = ds.withColumn(item[0], F.date_format( F.coalesce( F.to_timestamp(col(item[0])), F.to_timestamp(col(item[0]), 'MM-dd-yyyy HH:mm:ss')), "yyyy-MM-dd HH:mm:ss.SSS'Z'"))
            # then the columns are re-converted to timestamps. Since the line above adds the 'Z' in the timestamp's end, the re-conversion
            # takes the values as UTC ones (Z stands for UTC in ISODate formats). So, it adds hours to match the local machine. In Greek data,
            # it adds 3 hours. However, when these are stored in Mongo, they are re-converted to UTC, with the three hours removed, which is
            # what we want!
            ds = ds.withColumn(item[0], col(item[0]).cast("timestamp"))
    return ds

# function to convert timestamp columns to the CET's UTC time
def convertUTC(ds):
    for item in ds.dtypes:
        if(item[1] == "timestamp"):
            # convert to UTC time, based on CET given values
            # this should work, but it goes 2 hours back. Conflicts with mongo data make it understand its Greek time and discard 'CET'
            # it works when applying to datasets outside mongo
            #ds = ds.withColumn(item[0],to_utc_timestamp(col(item[0]), "CET"))
            # workaround, subtracting one hour (OR TWO HOURS IF IT IS SUMMER TIME) from current timestamp columns.
            # This way, we create UTC timestamps from CET, meaning Valencia, Spain time data.
            # WINTER TIME
            #ds = ds.withColumn(item[0], col(item[0]) - F.expr('INTERVAL 1 HOURS'))
            # SUMMER TIME
            ds = ds.withColumn(item[0], col(item[0]) - F.expr('INTERVAL 2 HOURS'))
            # remove empty timestamp values
            ds = ds.na.drop(subset=[item[0]])
    return ds

def executeApi(dColl):
    print("Attempt to delete Cygnus DB with POST request...")
    url = "*****************/notify"
    headers = {
      'content-type': "application/json"
    }
    body = json.dumps({
      "db":"db_default","coll":dColl
    })
    res = None
    try:
      res = requests.post(url, data=body, headers=headers)
    except Exception as e:
      print(e)
    responser = ""
    if res != None and res.status_code == 200:
      print("Success with Status Code:", res.status_code)
      print("Response:")
      responser = json.loads(res.text)
    return responser


# initialize an active spark session, along with a Context
print("Starting Mongo Connnection...")

#we take the incomming dataset's id by the REST POST request from the DataInjectionAgent.
#It is the second argument, the first being this code's path, so we will use argv[1] instead of argv[0]
#The cygnus collection name is the third argument
import sys
datasetId = sys.argv[1]
cygnuscoll = sys.argv[2]
print("What I got from the Data Injection Agent:")
print("Dataset ID:" + datasetId)
print("Dataset Collection to read from:" + cygnuscoll)

readMongodbHost = ""
db = ""
collection = cygnuscoll

writeMongodbHost = ""
writedb=""
writecoll=datasetId
writeusr = ""
writepwd = ""
spark = SparkSession \
    .builder \
    .appName("pafsJob") \
    .config("spark.mongodb.input.uri", "mongodb://" + readMongodbHost + "/" + db + "." + collection + "?readPreference=primary") \
    .config("spark.mongodb.output.uri", "mongodb://" + writeusr + ":" + writepwd + "@" + writeMongodbHost + "/" + writedb + "." + writecoll + "?authSource=admin") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1') \
    .getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

# alternative connection method, instead of .config addition above - NOT FULLY TESTED
#df = spark.read.format("mongo").option("uri", "mongodb://147.102.19.18/dirtyMongo.pcsPorts").load()

print("Mongo Connection Successfull.")

print("Initiang PaFS!")
start = time.time()

nameToWrite = "clean" + collection
nameToWriteExtra = "clean" + collection + "-extra"

# METADATA: COLUMNS AND THEIR DATA TYPES
customsColtypes = {
  "container": "string",
  "countryTransportMode": "int",
  "year": "int",
  "countryCurrency": "string",
  "unitNumber": "int",
  "invoiceValue": "int",
  "transportRegime": "string",
  "customDocumentDestinationCountry": "string",
  "customsProvince": "int",
  "deliveryCondition": "string",
  "additionalCodes": "string",
  "customDocumentOriginCountry": "string",
  "exchangeZone": "string",
  "customsDocumentType": "string",
  "customsRegimeRequested": "int",
  "vesselFreight": "int",
  "transportModeOnBorder": "int",
  "precedingRegimeRequested": "int",
  "TARIC": "string",
  "transportNationality": "string",
  "fiscalAddressProvince": "int",
  "statisticalValue": "int",
  "originExpeditionCountry": "string",
  "customsDocumentAdmissionDate": "date",
  "contingent": "int",
  "customsRegime": "string",
  "customDocumentDestinationProvince": "int",
  "customDocumentOriginProvince": "int",
  "tariffPreference": "int",
  "transactionNature": "int",
  "month": "int",
  "customsDocumentGrossWeight": "int"
}

portcallColtypes = {
  "vessel_shipName": "string",
  "voyageCode": "string",
  "arrivalDate": "timestamp",
  "departureDate": "timestamp",
  "UNLOCODE": "string",
  "terminal": "string",
  "vesselAgent": "string",
  "regularLine": "string",
  "status": "string"
}

vpfTradeColtypes = {
  "customsProcedureID": "string",
  "TARIC": "int",
  "containerDeliveryPlaceCode": "string",
  "containerType": "string",
  "fullEmpty": "string",
  "containerGrossWeight": "int",
  "executionDate": "timestamp",
  "unitNumber": "int",
  "customsRegime": "string",
  "customDocumentDestinationProvince": "string",
  "customDocumentOriginProvince": "string",
  "customDocumentDestinationCountry": "string",
  "packageType": "string",
  "portCallReference": "long",
  "isVGM": "boolean",
  "containerNumber": "string",
  "containerNextPrevLoadDischargePortCode": "string",
  "customDocumentOriginCountry": "string",
  "customsDocumentType": "string",
  "customsDocumentGrossWeight": "int",
  "containerOperationType": "string",
  "containerDischargePortCode": "string",
  "packageQuantity": "string",
  "customsStatus": "string"
}

# FORCED SOLUTION
dss = spark.read.format("mongo").option("sampleSize", 300000).load()
print("SCHEMA:")
dss.printSchema()

print("Repartitioning...")
dss = dss.repartition(10)
print("Repartition complete")
#dss = dss.limit(1000)

print("REMOVE TWO COLUMNS...")
dss = dss.drop("_id")
dss = dss.drop("recvTime")

# SAVE THE INCOMMING DATASET'S COLUMN TYPES TO A GENERIC VARIABLE
columTypes = {}
# TAKE CASES FOR EACH DATASET
splitter = datasetId.split(":")
didd = ""
marked = 0

if("VPF" in splitter):
    if ("PortCall" in splitter):
        didd = "PortCall"
        columnTypes = portcallColtypes
        print("CONVERT NESTED TO UN-NESTED...")
        # for now we only have vessel.shipName
        dss = dss.withColumn("vessel_shipName", col('vessel.shipName.value'))
        # now we can remove vessel column
        dss = dss.drop("vessel")
    else:
        # IT IS THE VPF TRADE CUSTOMS
        didd = "Customs"
        marked = 1
        columnTypes = vpfTradeColtypes
elif ("ITI" in splitter):
    didd = "Customs"
    columnTypes = customsColtypes
    print(customsColtypes)
    print("NOW:")
    print(columnTypes)
else:
    print("")

print("REMOVE DUPLICATES...")
dss = dss.distinct()

#print("CHECKING NEW DATAFRAME:")
#rows = dss.count()
#print("ROWS:", rows)
#dss.show(n=10)
#dss.printSchema()

# Write DataFrame data to JSON file -- JUST FOR NOW
# dss.toPandas().to_json('pcsDirtyPorts.json', orient='records', force_ascii=False, lines=True)

#print("Before Column Type Change:")
#dss.select(col('arrivalDate')).show()

print("Giving columns the proper data types...")
dss = changeColTypes(dss, columnTypes, marked)
#dss = changeColTypes(dss, tracecoltypes)
print("Column data type correction completed. Final schema:")
dss.printSchema()
#dss.show(n=10)

print("Removing whitespaces from all string rows...")
dss = removeWhiteSpaces(dss)
print("Whitespaces removed.")

print("Replacing empty values and NULLs with 'nan'...")
dss = removeEmptyNulls(dss)
print("Replacing completed.")

print("Converting datetime columns to UTC...")
dss = convertUTC(dss)
print("Conversion successfull.")

#print("Right After UTC Conversion:")
#dss.select(col('arrivalDate')).show()

print("Converting datetime columns to proper timestamp format...")
dss = convertCleanDatetime(dss)
print("Success.")

print("Final:")
dss.printSchema()
#dss.show(n=10)

#TEMPORARY STEP ---- REMEMBER TO DELETE THIS STEP AFTERWARDS
#writecoll = "CHECKING"+writecoll

#dss.toPandas().to_json('ANOTHER2.json', orient='records', force_ascii=False, lines=True)

# how many columns exist
#variables = len(dss.columns)
# how many rows exist - TAKES TIME AND MIGHT FAIL IN BIG DATASETS
#rows = dss.count()

# NOT SHOWING CAUSE OF ABOVE
#print("TOTAL COLUMNS FOUND IN", collection, "COLLECTION:", variables)
#print("TOTAL ROWS FOUND IN", collection, "COLLECTION:","")

# CHANGE 'overwrite' TO 'append', DEPENDING ON THE USAGE
print("Initiating connection with VDR. Passing dataset...")
print("Causion! Proccess will take some time for big datasets...")

if (marked == 1):
    print("In1")
    dss.write.format("mongo").partitionBy("originExpeditionCountry").mode("append").option("database", writedb).option("collection", writecoll).save()
else:
    print("In2")
    dss.write.format("mongo").mode("overwrite").option("database", writedb).option("collection", writecoll).save()
print("Passing successfull. PaFS Terminating.")

#Execute the POST to request Cygnus DB cleaning
#makeit = executeApi(cygnuscoll)
# it prints the response
# print(makeit)

end = time.time()
time_elapsed = end - start
minutes = time_elapsed / 60
rounded = round(minutes, 2)
print("Time Elapsed:", rounded, "mins.")

#finish
spark.stop()
