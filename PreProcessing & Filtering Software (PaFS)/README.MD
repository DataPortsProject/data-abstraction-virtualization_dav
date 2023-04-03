## (Pre)Processing and Filtering Software (PaFS)
PaFS achieves the initial pre-processing (including cleaning and filtering) of the incoming datasets. It is a sub-component that receives data streams through a GET REST API. All kinds of data can be accepted, since PaFS (and DAV in general) has a generic nature, regarding the data it receives and deals with.

### About PaFS
In a few words, PaFS achieves the Preprocessing, Cleaning and Filtering of every incoming dataset. It preprocesses the dataset by the means of fully collecting it, transforming it into a Apache Spark / Python code – friendly format and taking care of proper column – row structure. It cleans the dataset by the means of detecting “dirty” values (such as NaNs, empty fields, outliers and wrong values). It filters the dataset by the means of eliminating all the dirty values found, either by replacing them, or by removing them (along with their rows in the dataset / dataframe).

### Getting started
Before any further information, it should be noted that PaFS is intended to function as an Apache Spark Job. Therefore, an Apache Spark Cluster should already be deployed. This implementation is tested in the Apache Spark Framework version 3.0.1.. * Also, the VDR subcomponent must be built first *. Inside this folder, there is one python file and several jar files. The file "pafsJob.py" is actually PaFS itself, as a Spark Job. The remaining jar files are needed to be in the same directory with "pafsJob.py", for PaFS to function properly. However, these files !must! be included in the Spark installation folder's jar directory as well.

### Installation
As stated before, PaFS is intended to function as an Apache Spark Job, which means that no actual installation is needed. ** Before moving any further, make sure that an Apache Spark Cluster is installed and deployed to your local machine. Then, all the jar files found in this folder must be copied and pasted to Spark's jar files directory. Furthermore, be certain that VDR subcomponent has already been built and deployed. VDR must be built first, for the rest of components to function properly **. If so, run the following command:
- /opt/spark/bin/spark-submit  --master spark://SPARK_MASTER_IP:7077 --executor-memory 4g --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1  pafsJob.py
- It should work now. PaFS will retrieve the dataset from the given Mongodb IP (complete with db's name and credentials) and proceed to store the cleaned set to the same infrastructure, but to the specified database name. Note that this implementation is made to meet the metadata standards of PCS Port Calls and Traceability datasets.

### Further Information
--
