# Created by Tasos Nikolakopoulos / tasosnikolakop@mail.ntua.gr
from flask import Flask
from flask import render_template
from flask import Response, request, jsonify, redirect, url_for, send_file, send_from_directory
import datetime
import json
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import pyarrow
import fastparquet
import pymongo
import json
import pyarrow as pa
from pyarrow import json as pyjs
import pyarrow.parquet as pq


app = Flask(__name__)


@app.route('/')
def hello_world():
   return 'Virtual Data Container - Third and final subcomponent of Data Abstraction & Virtualization'

@app.route('/yearly') # it reads the parameter given in the 'year' value, after ?.
#Example request to work http://127.0.0.1:5000/yearly?year=2020
def yearer():
    # get the year parameter given
    year = request.args.get('year')
    # initialize a list where the mongo query response will be stored
    stringer = []
    # connect to mongo
    myclient = pymongo.MongoClient("mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017")
    mydb = myclient["vdrDb"]
    mycoll = mydb["weatherdata"]
    # query mongo and save response to the list
    for x in mycoll.find({"YEAR": { "$eq": int(year) }},{"_id": 0}):
        stringer.append(x)
    # save response as a dataframe
    framed = pd.DataFrame(stringer)
    # convert dataframe to table ready for parquet format
    table = pa.Table.from_pandas(framed)
    # save the table as a parquet file
    pq.write_table(table, f'files/year.parquet')
    # send the parequet file created as an attachment
    return send_file('files/year.parquet', as_attachment=True)

@app.route('/tempOver') # it reads the parameter given in the 'temp' value, after ?.
#Example request to work http://127.0.0.1:5000/tempOver?temp=15
def tempOverer(name=None):
    # get the temperature parameter given
    temp = request.args.get('temp')
    # initialize a list where the mongo query response will be stored
    stringer = []
    # connect to mongo
    myclient = pymongo.MongoClient("mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017")
    mydb = myclient["vdrDb"]
    mycoll = mydb["weatherdata"]
    # query mongo and save response to the list
    for x in mycoll.find({"MEAN_TEMP": { "$gt": float(temp) }},{"_id": 0}):
        stringer.append(x)
    # save response as a dataframe
    framed = pd.DataFrame(stringer)
    # convert dataframe to table ready for parquet format
    table = pa.Table.from_pandas(framed)
    # save the table as a parquet file
    pq.write_table(table, f'files/temp.parquet')
    # send the parequet file created as an attachment
    return send_file('files/temp.parquet', as_attachment=True)

@app.route('/rainNwind') # it reads the parameter given in the 'rain' and 'wind' values, after ?.
#Example request to work http://127.0.0.1:5000/rainNwind?rain=0.5&wind=2
def rainNwinder(name=None):
    # get the rain and wind parameters given
    rain = request.args.get('rain')
    wind = request.args.get('wind')
    # initialize a list where the mongo query response will be stored
    stringer = []
    # connect to mongo
    myclient = pymongo.MongoClient("mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017")
    mydb = myclient["vdrDb"]
    mycoll = mydb["weatherdata"]
    # query mongo and save response to the list
    for x in mycoll.find({"RAIN": { "$gt": float(rain) }, "AVG_WIND_SPEED": { "$gt": float(wind) }},{"_id": 0}):
        stringer.append(x)
    # save response as a dataframe
    framed = pd.DataFrame(stringer)
    # convert dataframe to table ready for parquet format
    table = pa.Table.from_pandas(framed)
    # save the table as a parquet file
    pq.write_table(table, f'files/rainWind.parquet')
    # send the parequet file created as an attachment
    return send_file('files/rainWind.parquet', as_attachment=True)

if __name__ == '__main__':
    #app.run(debug = True)
    app.run(host="0.0.0.0", debug = True)
