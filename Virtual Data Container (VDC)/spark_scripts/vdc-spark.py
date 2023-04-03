#!/usr/bin/env python
# coding: utf-8

"""vdc-spark.py"""

import sys
import os
import logging
import shutil
import json
import numbers
import re
import datetime, time
from random import randint
import requests
import pysftp

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, to_date
from pyspark.sql.types import TimestampType


mongodbHost = ""
mongodb = ""
mongodbUsername=""
mongodbPassword=""
# ftp server info
ftpHost = ""
ftpPort = 21
ftpUsername = ""
ftpPassword = ""
ftpPath=""
# ack url
ack_url=""

# creating a log variable
log =  None


# a function that returns the the current time in string format
def timeNow():
    return datetime.datetime.now().strftime("%H:%M:%S")

DATETIME_ISO8601 = re.compile(
    r'^([0-9]{4})' r'-' r'([0-9]{1,2})' r'-' r'([0-9]{1,2})' # date
    r'([T\s][0-9]{1,2}:[0-9]{1,2}:?[0-9]{1,2}(\.[0-9]{1,6})?)?' # time
    r'((\+[0-9]{2}:[0-9]{2})| UTC| utc)?' # zone
)

# a function that returns whether the string can be interpreted as an ISO date
def datetime_iso(string):
    """ verify rule
    Mandatory is: 'yyyy-(m)m-(d)dT(h)h:(m)m'
    """
    string = string.strip()
    return bool(re.fullmatch(DATETIME_ISO8601, string))

# a function that returns whether the string can be interpreted as an ISO UTC date
def utc_timezone(datetime_string):
    datetime_string = datetime_string.strip()
    return datetime_string.endswith("00:00") or datetime_string.upper().endswith("UTC")

# a function to determine whether a value is numeric
def isNumber(val):
    return isinstance(val, numbers.Number)

# a function that returns whether the string can be interpreted as a UTC date
def isDate(string):
    return datetime_iso(string) and utc_timezone(string)

# a function that parses rules and creates filtering conditions in the correct format
def parseRule(subject_column, operator, objectField):
    # variables for the formated operator and object
    subject_column_formated = "`" + subject_column + "`"
    operator_formated = ""
    object_formated = ""
    # parse for the case of each operator and object data type (numeric, date, string)
    if operator == "==" and isNumber(objectField):
        operator_formated = "="
        object_formated = str(objectField)
    elif operator == "==":
        operator_formated = "="
        object_formated = "'" + objectField + "'"
    elif operator == "!=" and isNumber(objectField):
        operator_formated = "!="
        object_formated = str(objectField)
    elif operator == "!=":
        operator_formated = "!="
        object_formated = "'" + objectField + "'"
    elif operator == ">" and isNumber(objectField):
        operator_formated = ">"
        object_formated = str(objectField)
    elif operator == ">" and isDate(objectField):
        operator_formated = ">"
        object_formated = "'" + objectField + "'"
    elif operator == "<" and isNumber(objectField):
        operator_formated = "<"
        object_formated = str(objectField)
    elif operator == "<" and isDate(objectField):
        operator_formated = "<"
        object_formated = "'" + objectField + "'"
    elif operator == ">=" and isNumber(objectField):
        operator_formated = ">="
        object_formated = str(objectField)
    elif operator == ">=" and isDate(objectField):
        operator_formated = ">="
        object_formated = "'" + objectField + "'"
    elif operator == "<=" and isNumber(objectField):
        operator_formated = "<="
        object_formated = str(objectField)
    elif operator == "<=" and isDate(objectField):
        operator_formated = "<="
        object_formated = "'" + objectField + "'"
    elif operator == "or":
        or_sub_conditions = ["(" + parseRule(subject_column, sub_rule["operator"], sub_rule["object"]) + ")" for sub_rule in objectField]
        condition = ' or '.join(or_sub_conditions)
        return condition
    condition = subject_column_formated + " " + operator_formated + " " + object_formated
    return condition

# a function to get Spark Session
def getSparkSession(collection):
    log.info("Getting Spark Session")
    log.debug("Setting Spark properties: MongoDB url: mongodb://{}:{}@{}:27017/{}.{}?authSource=admin".format(mongodbUsername, "***password***", mongodbHost, mongodb, collection))
    # get Spark Session
    spark = SparkSession \
         .builder \
         .appName("VDC") \
         .config("spark.mongodb.input.uri", "mongodb://{}:{}@{}:27017/{}.{}?authSource=admin".format(mongodbUsername, mongodbPassword, mongodbHost, mongodb, collection)) \
         .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1') \
         .config("spark.mongodb.input.sampleSize", 300000) \
         .config('spark.sql.session.timeZone', 'UTC') \
         .getOrCreate()
    return spark

# a function to put files to an ftp server
def putFTP(results_dir, filename, fileFormat):
    log.debug("Creating a connection to the sftp server {} with the user {}".format(ftpHost, ftpUsername))
    # Accept any host key
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    log.debug("Connecting accepting any host key (not from known hosts)")
    sftp = pysftp.Connection(ftpHost, username=ftpUsername, password=ftpPassword, private_key=".ppk", cnopts=cnopts)
    # sftp = pysftp.Connection(ftpHost, username=ftpUsername, password=ftpPassword)
    log.debug("Checking if directory {} exists: {}".format(ftpPath, sftp.exists(ftpPath)))
    if (not sftp.exists(ftpPath)):
        log.debug("Creating directory {}".format(ftpPath))
        sftp.makedirs(ftpPath)
    log.debug("Changing directory to {}".format(ftpPath))
    sftp.chdir(ftpPath)

    file = [f for f in os.listdir(results_dir) if f.endswith(fileFormat)][0]
    log.debug("Sending data...")
    # get the generated file
    file_to_send = results_dir + '/' + file
    sftp.put(file_to_send, remotepath="{}/{}.{}".format(sftp.pwd, filename, fileFormat), preserve_mtime=True)
    log.debug("Transimition ended")
    log.debug("Listing the contents of the current directory: {}".format(sftp.listdir()))

# a function to send an ack message
def sendAck(status, path, filename, format):
    log.info("Ack server: {}".format(ack_url))
    headers = {'Content-Type' : 'application/json; charset=utf-8'}
    json_data = {'status': status,
                 'path': path,
                 'filename': filename + "." + format,
                 'format': format}
    log.info("Ack body: {}".format(json_data))
    resp = requests.post(ack_url, headers=headers, json=json_data)
    return resp

# the VDC implementation for the DAV component
def vdc(dataset_id, rules, fileFormat, datasetname = None):
    log.info("Starting VDC")

    # get Spark Session
    spark = getSparkSession(dataset_id)

    # load dataframe
    log.info("Reading dataset")
    log.debug("dataset_id: {}".format(dataset_id))
    df = spark.read.format("mongo").load()

    # drop mongoDB _id column
    log.debug("Dropping mongoDB _id column")
    df = df.drop("_id")

    # apply filtering rules
    log.info("Applying the rules")
    for r in rules:
        # get rules components: name, subject_column, operator, object
        log.info("- {}".format(r["name"]))
        subject_column = r["rule"]["subject_column"]
        operator = r["rule"]["operator"]
        objectField = r["rule"]["object"]
        # take cases for the event that the recipient wishes to keep or delete some columns
        if ((operator == "++") or (operator == "--")):
            # split the columns based on the agreed "|" symbol
            columns = objectField.split("|")
            # delete given columns
            if(operator == "--"):
                for col in columns:
                    # check if a column is empty by mistake
                    if(col != ""):
                        df = df.drop(col)
            # keep only given columns
            elif (operator == "++"):
                df = df.select(list(columns))
        else:
            # apply each rule on dataframe
            condition = parseRule(subject_column, operator, objectField)
            log.info("  Rule condition: {}".format(condition))
            df = df.filter(condition)

    # show the resulting dataframe
    # print(timeNow() + ":" + "Show the resulting dataframe")
    # df.show()

    # create a dir to save the results
    log.debug("Creating results dir")
    random_dir = str(spark.sparkContext.applicationId) + '-' + str(randint(1000000, 9999999))
    results_dir = "/PUT-YOUR-DIRECTORY-HERE/" + random_dir

    # save results on node
    log.info("Saving the results in {} on node".format(fileFormat))
    if fileFormat == "parquet":
        for c in df.columns:
            df = df.withColumnRenamed(c, c.replace(" ", "_"))
    if fileFormat == "csv":
        df.coalesce(1).write.mode("overwrite").save(results_dir ,format=fileFormat, header = 'true')
    else:
        df.coalesce(1).write.mode("overwrite").save(results_dir ,format=fileFormat)

    # send files to FTP server
    log.info("Sending results at ftp server")
    filename = dataset_id.replace(":", "_")
    putFTP(results_dir, filename, fileFormat)

    # send ack message to notify
    log.info("Sending ack message")
    resp = sendAck(status='Completed', path=ftpPath, filename=filename, format=fileFormat)
    log.info("Http response [ status code: {}, response body: {}]".format(resp.status_code, resp.text))
    if resp.status_code == 200:
        log.info("Ack sent succesfully")
    else:
        log.warning("Some error occured in sending ack message")
    log.debug("Http response [ status code: {}, response body: {}]".format(resp.status_code, resp.text))

    # delete dir and files
    log.debug("Deleting files")
    shutil.rmtree(results_dir)

    # finish
    log.info("Stopping Spark")
    spark.stop()
    log.info("Quitting VDC")

# a function to get a logger
# and set the logging level
# available values: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
def getLogger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        pass
    else:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

# the main function that gets invoked by the spark submit
if __name__ == '__main__':
    log = getLogger('my-logger', level=logging.INFO)

    rules_text = sys.argv[2]
    rules = json.loads(rules_text)

    vdc(dataset_id=sys.argv[1],
        rules=rules,
        fileFormat=sys.argv[3])
