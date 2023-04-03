# Created by Tasos Nikolakopoulos / tasosnikolakop@mail.ntua.gr
from flask import Flask
from flask import render_template
from flask import Response, request, jsonify, redirect, url_for
import datetime
import json
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

app = Flask(__name__)


@app.route('/')
def hello_world():
   return 'Processing & Filtering Software - First subcomponent of Data Abstraction & Virtualization'

@app.route('/initiate')
def initiate(name=None):
    ds = pd.read_csv('wds/greek_weather_data.csv', delimiter="\t", low_memory=False)
    #print the length of the dataset, as well as the columns where nan values exist
    print("Dataset length:", len(ds))
    print("NaN Values found:")
    print(ds.isna().sum())
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
    # the response to be returned
    resp = "Process complete. Dataset Preprocessed, Filtered & Cleaned. TIMESTAMP (Time Greece):", ct
    return jsonify(responser = resp)

@app.route('/testparse', methods=['GET', 'POST'])
def resetjson():
    defs = request.get_json()
    with open('testparsed.json', 'w') as f:
        json.dump(defs, f)
    return jsonify(responser = "received data")


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

if __name__ == '__main__':
   app.run(host="0.0.0.0", debug = True)
