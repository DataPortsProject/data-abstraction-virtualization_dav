## Virtual Data Repository (VDR)
The Virtual Data Repository plays the role of the repository for all the existing datasets that have made their way in DAV, after being pre-processed by PaFS. It can be seen as a data lake, containing all the pre-processed datasets.

### About VDR
the Virtual Data Repository (VDR), this is the place where all the pre-processed, cleaned and filtered datasets, coming from PaFS, are saved. After a dataset has been passed through all its functions, it then gets stored in VDR (along with its columns’ correlation matrix). VDR consists of a MongoDB, carrying modifications and custom parameters, in order to comply with DAV’s efficiency standards. An important note is that the following construction / implementation steps are for a local cluster system, with physical machines / servers. This means that these steps are not for an NFS server, or any implementation of this kind.

### Getting started
It must be noted that * VDR is the subcomponent that has to be built first * . VDR is intended to function on a Kubernetes Cluster. Therefore, a Kube Cluster should already be deployed. This folder contains all the files necessary for the modified MongoDB (which actually is our Virtual Data Repository) to be deployed. This implementation consists of a storage class and already-defined persistent volumes. Let us move on to analyse the installation steps.

### Installation
Make sure that you are inside the "Virtual Data Repository (VDR)" folder. Then follow these steps:
- Create the storage class defined through the yaml file (you do that by typing the command: kubectl create -f storageclass.yaml)
- Create some persistent volumes (you do that by typing the command: kubectl create -f persvolumes.yaml). * First, you must have already created volumes at '/mnt/disk/'. Add 'vol1', 'vol2', 'vol3', etc volumes there. So you will have paths like '/mnt/disk/vol1', '/mnt/disk/vol4' and so on. A total of 10 persistent volumes would be good. * Make sure that the volume names created, are the same with the ones defined in the persvolumes.yaml file.
- Create a mongodb headless service (you do that by typing the command: kubectl create -f headless-service.yaml)
- Create a mongodb stateful set (you do that by typing the command: kubectl create -f mongodb-statefulset.yaml)
If everything works as planned (which should), then VDR's MongoDB has been properly deployed. Now, the initialization part remains. These are the steps that need to be followed:
- kubectl exec -it mongo-0 -- mongo  (to enter mongo shell living inside the pod)
Inside the Mongo Shell, type the following commands:
- rs.initiate()
- var cfg = rs.conf()
- cfg.members[0].host=“mongo-0.mongo:27017”  (first part - mongo-0 - here is the pod name, whilst the second part - mongo -  here is the service name)
- rs.reconfig(cfg)
- rs.status()  (that’s to check that everything works well. We should see "mongo-0.mongo:27017" in “members” section)
- rs.add(“mongo-1.mongo:27017”)  (to add second replica)
- EXECUTE THE SAME COMMAND  (rs.add(“mongo-X.mongo:27017”) FOR ALL THE REPLICAS THAT YOU HAVE
- rs.status()  (check that mongo replicas have been successfully added as members - all replicas apart from the first one should be labeled as “SECONDARY”. First replica should be labeled as “PRIMARY”)
Now exit the mongo shell. After these steps, VDR has been properly initialized. All that's left to do is test that it works as expected. Execute these two final commands in order to test that:
- kubectl run mongo --rm -it --image mongo -- sh  (run a temporary mongo shell inside the cluster)
- mongo mongodb://mongo-0.mongo:27017,mongo-1.mongo:27017  (you specify the two mongodb replicas and separate them with coma. In each replica, the first part - mongo-0  & mongo-1 - here is the pod name, whilst the second part - mongo -  here is the service name).
If the command above is successful and you enter the mongo shell, then you are all set! This is the IP / connection string to connect internally from the Kubernetes cluster.

### Further Information
Only after the initialization of VDR, PaFS (and therefore VDC) will function properly. The file "PVCexample.yaml" contains a deployment example of a Persistent Volume Claim. However, there is no need to create persistent volume claims (PVCs), since these will be created automatically by the stateful yaml.
