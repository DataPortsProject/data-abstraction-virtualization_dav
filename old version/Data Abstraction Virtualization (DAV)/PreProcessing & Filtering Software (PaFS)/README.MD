## (Pre)Processing and Filtering Software (PaFS)
PaFS achieves the initial pre-processing (including cleaning and filtering) of the incoming datasets. It is a sub-component that receives data streams through a GET REST API. All kinds of data can be accepted, since PaFS (and DAV in general) has a generic nature, regarding the data it receives and deals with.

### About PaFS
In a few words, PaFS achieves the Preprocessing, Cleaning and Filtering of every incoming dataset. It preprocesses the dataset by the means of fully collecting it, transforming it into a Python code – friendly format and taking care of proper column – row structure. It cleans the dataset by the means of detecting “dirty” values (such as NaNs, empty fields, outliers and wrong values). It filters the dataset by the means of eliminating all the dirty values found, either by replacing them, or by removing them (along with their rows in the dataset / dataframe).

### Getting started
Before any further information, it should be noted that PaFS is intended to function on a Kubernetes Cluster. Therefore, a Kube Cluster should already be deployed. * Also, the VDR subcomponent must be built first *. Inside this folder, there two other ones. The folder "GeneralCode" contains the iPynb files (PreprocFilterClean.ipynb and PassDataToMongo.ipynb) and the Python Flask application (with main file the "pafser.py"), to test PaFS's functionality in a local machine. The folder "PafsToKube" contains all the files necessary for PaFS to function in a Kubernetes cluster (with main file the "pafs.py").

### Installation
This section covers the installation process of the contents in the folder "PafsToKube". As stated before, the folder "GeneralCode" contains files for experimentation in a local machine. ** Before moving any further, make sure that VDR subcomponent has already been built and deployed. VDR must be built first, for the rest of components to function properly **. If so, complete the following steps:
- Make sure that you are inside the ‘dav’ namespace
- Also, make sure that you are in the "PafsToKube" file
- Run the following commands:
    - docker build -f Dockerfile -t pafs:latest .  (to create a docker image of PaFS)
    - docker image ls  (to check that PaFS image is ok)
    - kubectl apply -f deployment.yaml  (to deploy PaFS)
    - kubectl get pods  (check everything is alright, with PaFS pod running)
    - kubectl get services  (again, check everything is alright, with PaFS service running)
- It should work now. Run CLUSTER_MAIN_IP:30007/ and you should get “Processing & Filtering Software - First subcomponent of Data Abstraction & Virtualization” as a response in a browser, or through Postman. In order to try the process of preprocessing, cleaning & filtering of the Greek Weather dataset (which is inside the 'wds' folder), all you need to run (in a browser or through Postman) is CLUSTER_MAIN_IP:30007/initiate . The process will take some time, since the dataset needs to be properly cleaned and then stored to VDR. A confirmation message of success will be sent as a response.

### Further Information
Regarding the Greek Weather dataset, it has not been included in the files in this repository, due to its size. * PaFS will not function properly, unless you download the dataset and put it in the "wds" folder inside PafsToKube. * You will need to do the same in the "wds" folder of "GeneralCode", in case you want to experiment locally. The dataset is freely available and can be easily downloaded through this link: https://www.kaggle.com/spirospolitis/greek-weather-data
