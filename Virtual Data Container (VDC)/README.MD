## Virtual Data Container (VDC)
The Virtual Data Container is the layer between DAV and any potential data recipient.

### About VDC
VDC is the agent through which communication with data recipients is achieved, for data (stored in VDR) to be made available. Ιt is a generic (sub) component, the role of which is to further process and filter the data, by applying specific filtering rules defined by the data consumers via HTTP POST requests. Through these requests, the data consumer also defines the format in which he/she wants to receive the data (data transformation). Furthermore, VDC is responsible for exposing useful metadata (size, number of rows and variables, timestamp of last update etc.) for each one dataset that is stored in VDR. Those metadata are available via a RESTful API.

### Getting started
Before any further information, it should be noted that VDC is intended to function on a Nifi Cluster and on a Spark cluster. Also, the VDR and PaFS subcomponents must be built first *. For Nifi we provide a docker image (iccs/vdc:1.0) and a docker-compose.yml template file in order to make the installation as easy as possible.

#### Setting up the Nifi-VDC container
After setting all the desired parameters in the docker-compose.yml open a terminal in its directory and run the following command
```
  sudo docker-compose up -d
````
After a while a new vdc container will be created and the Nifi UI page will be available.

When this happens the system admin must log in using their credential at https://nifi_web_host:nifi_web_port/nifi/. By dragging and dropping from the template button on the menu bar they can instantiate any of the three preinstalled apis:
- vdc_metadata_api
- vdc_with_spark
- ack_vdc_api
Next comes the activation of the various controller services for each api. This can be done by selecting ''Configure'' on the api workflow when right clicking on them. On the controller services tab the admin must click the little thunder button to enable the service.

WARNING: Some controller services require secret credentials which must be set by the addmin in the properties of the service. Example of this type of controllers are the MongoDBControllerService which require the username and password of the MongoDB user.

Finally, by right clicking on each workflow api the admin may start or stop it.

### Installation
Creating Nifi components from already made templates is very easy. Instructions can be found here: https://nifi.apache.org/docs/nifi-docs/html/user-guide.html#templates. Nifi's powerful UI makes the installation process very straightforward.
