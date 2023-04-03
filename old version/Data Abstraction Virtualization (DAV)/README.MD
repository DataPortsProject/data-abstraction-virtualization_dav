## Data Abstraction Virtualization Component (DAV)
This repository houses the complete code for Data Abstraction & Virtualization (DAV) to function properly. Clear instructions are given in every subfolder.

### Repository contents
This repository contains three main subfolders, each for evey sub-component of DAV. One folder for the (Pre)Processing and Filtering Software (PaFS), one for the Virtual Data Repository (VDR) and one for the Virtual Data Container (VDC). Seach subfolder contains a README.md file with instructions of installation. Please note that, for the complete DAV to function, a Kubernetes Cluster must already be up and running. The instructions of a Kube Cluster deployment are not part of this repository.

### Getting started
Data Abstraction & Virtualization component is part of the "internal" DataPorts architecture. Therefore, no UI to use is being implemented. Each subfolder contains instructions of use.

### Installation
DAV consists of the three aforementioned subcomponents (located in the subfolders of the same name). Follow the installation instructions in each subfolder, in order to deploy each one.

### Further Information
When fully deployed and integrated with other components, DAV shall get incoming datasets from the Semantic Interoperability Layer / On-Demand Component. These datasets will be pre-processed and cleaned by PaFS and then stored to VDR. Through VDC, any potential data recipient will have access to the data, based on his/her queries to VDR. Such a recipient is the Data Analytics & AI Services' Automatic Models Training Engine.

### Credits
Achilleas Marinakis - achmarin@mail.ntua.gr
Anastasios (Tasos) Nikolakopoulos - tasosnikolakop@mail.ntua.gr

### License
Data Abstraction & Virtualization component is free software: you can redistribute it * and/or modify it under the terms of the GNU General Public License as * published by the Free Software Foundation, either version 3 of the License, * or (at your option) any later version.
