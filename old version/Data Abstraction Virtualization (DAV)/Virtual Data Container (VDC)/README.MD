## Virtual Data Container (VDC)
The Virtual Data Container is the layer between DAV and any potential data recipient. It may further process the data, in order to extract helpful analytics. Moreover, upon the dataset request by a recipient, it transforms the data into the desired format, whilst making them available to him/her.

### About VDC
The Virtual Data Container (VDC) is the agent through which communication with data recipients is achieved, for data (stored in VDR) to be made available. Similar to PaFS, VDC is written in Python, as a Python Flask module. Moreover, it is a generic (sub) component, meaning that it can be slightly modified to match different kinds of needs. An instance of this generic software tool, “listens” to REST requests from potential data recipients, communicates with VDR to retrieve the queried data pond, it collects, prepares and finally converts it to a Parquet format, where it gets forwarded to the data recipient as a Parquet file.

### Getting started
Before any further information, it should be noted that VDC is intended to function on a Kubernetes Cluster. Therefore, a Kube Cluster should already be deployed. * Also, the VDR and PaFS subcomponents must be built first *. Inside this folder, there two other ones. The folder "GeneralCode" contains the Python Flask application (with main file the "vdcer.py"), to test VDC's functionality in a local machine. It also contains two sample .json files, which can be used for testing VDC locally. The folder "VdcToKube" contains all the files necessary for VDC to function in a Kubernetes cluster (with main file the "vdc.py").

### Installation
This section covers the installation process of the contents in the folder "VdcToKube". As stated before, the folder "GeneralCode" contains files for experimentation in a local machine. ** Before moving any further, make sure that VDR and PaFS subcomponents have already been built and deployed. VDR must be built first, and then PaFS, for all three components to function properly **. If so, complete the following steps:
- Make sure that you are inside the ‘dav’ namespace
- Also, make sure that you are in the "VdcToKube" file
- Run the following commands:
    - docker build -f Dockerfile -t vdc:latest .  (to create a docker image of VDC)
    - docker image ls  (to check that VDC image is ok)
    - kubectl apply -f deployment.yaml  (to deploy VDC)
    - kubectl get pods  (check everything is alright, with VDC pod running)
    - kubectl get services  (again, check everything is alright, with VDC service running)
- It should work now. Run CLUSTER_MAIN_IP:30009/ and you should get “Virtual Data Container - Third subcomponent of Data Abstraction & Virtualization” as a response in a browser, or through Postman.

### Further Information
At this point, DAV should be running as a complete component, with all three subcomponents so-operating smoothly. There are three example queries available, to test VDC's function and get a data pond in Parquet format:
- http://CLUSTER_MAIN_IP:30009/yearly?year=2010 -> It shall return a parquet file, containing all data from the given year (in this case, its the year 2010. Accepted fields are 2006-2017, since the dataset contains data from that time period.)

- http://CLUSTER_MAIN_IP:30009/tempOver?temp=25 -> It shall return a parquet file, containing weather data with daily average temperature over 25 degrees Celsius (the value of 25 can be freely changed.)

- http://CLUSTER_MAIN_IP:30009/rainNwind?rain=0.8&wind=2 -> Once again, it shall return a parquet file, containing all weather data with the given rain & wind speed values (in this case, these values are 0,8 and 2. They can be freely replaced for testing.)
