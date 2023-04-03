# Created by Tasos Nikolakopoulos / tasosnikolakop@mail.ntua.gr
from flask import Flask
from flask import render_template
from flask import Response, request, jsonify, redirect, url_for
import datetime
import json
import pandas as pd
import numpy as np
import pymongo
from sklearn.impute import SimpleImputer

app = Flask(__name__)


@app.route('/')
def hello_world():
   return 'Processing & Filtering Software - First subcomponent of Data Abstraction & Virtualization'

@app.route('/initiate')
def initiate(name=None):
    ds = pd.read_csv('wds/greek_weather_data.csv', delimiter="\t", low_memory=False)
    # drop the 'Unnamed: 0' useless column
    ds.drop('Unnamed: 0', inplace=True, axis=1)
    #print the length of the dataset, as well as the columns where nan values exist
    print("Dataset length:", len(ds))
    print("NaN Values found:")
    print(ds.isna().sum())
    # apply the rules to the dataset
    ds = ruless(ds)
    # detect outliers in the dataset
    ds = outliered(ds)
    # replace nan values with the mean of each value's column. TAKES TIME
    cleaned = cleaner(ds)
    #validate that the length remains the same, as well as that the nan values have been eliminated
    print("Dataset length after cleaning:", len(cleaned))
    print("NaN Values found now:")
    print(cleaned.isna().sum())
    print("Dataset Now:")
    print(cleaned)
    ct = datetime.datetime.now()
    # Create a correlation matrix
    correlations = cleaned.corr()
    # save the new correlations dataset
    correlations.to_csv("correlations.csv")
    # pass data to MongoDB
    sizecoll = passToMongo(cleaned)
    # the response to be returned
    resp = "Process complete. Dataset Preprocessed, Filtered & Cleaned. TIMESTAMP:", ct, ". Data also passed to MongoDB. Mongo now has a total of", sizecoll, "data inserts."
    return jsonify(responser = resp)

@app.route('/testparse', methods=['GET', 'POST'])
def resetjson():
    defs = request.get_json()
    with open('testparsed.json', 'w') as f:
        json.dump(defs, f)
    return jsonify(responser = "received data")

# RULES
# metadata info: rules that each column's values must have
# function that applies the rules to the given dataset
def ruless(dss):
    print("Initial size before Rules application:",len(dss))
    # Temperatures must be between -100 and 55 degrees celsius
    dss = dss[dss['HIGH_TEMP'] < 55]
    dss = dss[dss['LOW_TEMP'] > -100]
    print("After Temperature Rule:", len(dss))
    # Rain must not be below 0
    dss = dss[dss['RAIN'] >= 0]
    print("After Rain Rule:", len(dss))
    # Highest wind speed must not be above 1000
    dss = dss[dss['HIGHEST_WIND_SPEED'] < 1000]
    print("After Wind Speed Rule:", len(dss))
    print("Final size after the Rules application:",len(dss))
    return dss

# metadata info: columns that will be parsed from outlier & wrong input detector
cols = ['MEAN_TEMP', 'HIGH_TEMP', 'LOW_TEMP', 'HEAT_DEG_DAYS', 'COOL_DEG_DAYS', 'RAIN', 'AVG_WIND_SPEED', 'HIGHEST_WIND_SPEED']

# search for outliers in the given columns
# function that detects outlier values in the given dataset
def outliered(dss):
    # a counter for the total outliers found
    totaloutliers = 0
    # begin parsing the given columns
    for cl in cols:
        # mean (average) calculation
        mean = dss[cl].mean()
        # standard deviation calculation
        std = dss[cl].std() 
        # the cut-off threshold, which in this case is 3 times the standard deviation
        anomaly_cut_off = std * 3
        # calculate the lower limit. Below that, all values will be considered as outliers
        lower_limit  = mean - anomaly_cut_off 
        # calculate the upper limit. Above that, all values will be considered as outliers
        upper_limit = mean + anomaly_cut_off
        # get a list where 'True' values will indicate outliers above the upper limit
        outliers1 = dss[cl] > upper_limit
        # get a list where 'True' values will indicate outliers below the upper limit
        outliers2 = dss[cl] < lower_limit
        # merge the two lists. We now want all outliers. Simply, if we compare each value pairs between them with '!=',
        # we will get 'True' for the outliers (True != False equals True) and 'False' for correct values (False != False equals False)
        outliersfin = (outliers1 != outliers2)
        # convert the boolean list to a string list of Trues and Falses
        booleanDictionary = {True: 'True', False: 'False'}
        outliersfin = outliersfin.map(booleanDictionary)
        # add the outlier locations list to the main dataframe
        name = cl+"_OUTLIER_LOCATION"
        dss[name] = outliersfin
        # search for the outliers
        for it in outliersfin:
            if it == "True":
                totaloutliers = totaloutliers + 1           
    print("Total outliers found:", totaloutliers)
    return dss

# function that cleans a given dataset, that is, it fills the empty numerical values with their columns' means,
# bypassing the empty categorical ones
def cleaner(dief):
    catcols = []
    numcols = []
    for c in dief.columns:
        #check if there are any strings in column
        if dief[c].map(type).eq(str).any():
            catcols.append(c)
        else:
            numcols.append(c)
    #create two DataFrames, one for each data type
    num = dief[numcols]
    cat = pd.DataFrame(dief[catcols])
    # create a num imputer for numerical valuees
    numimputer = SimpleImputer(missing_values=np.nan, strategy='mean')
    # we apply the numimputer only to numeric columns / values
    num = pd.DataFrame(numimputer.fit_transform(num), columns = num.columns)
    # create a cat imputer for categorical valuees
    catimputer = SimpleImputer(strategy='constant', fill_value="MISSING_VALUE")
    # we apply the catimputer only to categorical columns / values
    cat = pd.DataFrame(catimputer.fit_transform(cat), columns = cat.columns)
    #join the two dataframes back together
    newdief = pd.concat([cat, num], axis = 1)
    # return the cleaned dataset
    return newdief

def passToMongo(dief):
    myclient = pymongo.MongoClient("mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017")
    mydb = myclient["vdrDb"]
    mycoll = mydb["weatherdata"]
    # pass the dataframe to the database's collection
    mycoll.insert_many(dief.to_dict("records"))
    collsize = mydb.command("collstats", "weatherdata")['count']
    return collsize



if __name__ == '__main__':
   app.run(host="0.0.0.0", debug = True)
