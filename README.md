# Assignment 

This assignment is an application that runs in a Kubernetes pod, it'll be connected in a DB pod.  
The application can be accessed outside the cluster through an HTTP connection. If the load of CPU to be more than 20% will be scale until five pods.

## Directories
In this repository we have three directories:  
- app: Here there are Kubernetes manifest files to deploy the application environment. And there is the Dockerfile following the application code to build the application image.   
- db: Where is the Database Kubernetes manifest.
- metrics server: The manifests to install metrics-server in Kubernetes to use the HPA to automized the scaling. 

## Deploy
### 1 - Deploy Metrics-Server
I'm considering that there is a Kubernetes cluster installed and right configured.  
Said that, if in the cluster there isn't the metrics-server installed we'll install it first.  

In a terminal with kubectl installed and using allow credential to access a cluster, execute the bellow down command:  

```
kubectl apply -f metrics-server/*
```

The metrics-server manifest I took from the official repository. I just configure the parameter `--kubelet-insecure-tls` because I test my environment in a single node Kubeadmin installation.  

### 2 - Deploy Database
First thing is, choose one node in the cluster to be the Database node and create de follow label.  
```
kubectl label nodes <node_name> type_node=database
```
It'll create the label in the node because the node will receive the database pod that uses a PV (local volume) to persist data.  

After that execute the follow commands in that sequency:  
```
kubectl apply -f db/db_pv.yaml  
kubectl apply -f db/db_ns.yaml  
kubectl apply -f db/db_pvc.yaml  
kubectl create secret generic db-access --namespace=db --from-literal=password=<db_passwd_you_want> --from-literal=user=<db_user_you_want> 
kubectl apply -f db/db_deployment.yaml  
kubectl apply -f db/db_svc.yaml  
```
If you want, in the `db` dir there is db_secret.yaml file example to create a secret instead to use the imperative command. But remember the values to use in the manifest file have to be in the base64 encoded.  

### 3 - Deploy Application
For this step, the image used in deployment manifest file is stored in my docker hub repository(*reverson/my_app:latest*). It means that for now isn't necessary to build the image. But it is possible if you want. I'll describe more about the application further in this document.  

In the `app/app_configmap.yaml` there are some database parameters that the application used to connect to the database. I didn't consider that information as sensitive information. So, I kept in plain text in opposite of *user* and *password* information.  

Execute the follow commands in that sequency to deploy the application:  
```
kubectl apply -f app/app_ns.yaml  
kubectl apply -f app/app_configmap.yaml  
kubectl create secret generic db-app-access --namespace=app --from-literal=db-password=<db_passwd> --from-literal=db-user=<db_user>  
kubectl apply -f app/app_deployment.yaml  
kubectl apply -f app/app_hpa.yaml  
kubectl apply -f app/app_svc.yaml  
```
Like I said in `db` before, there is app_secret.yaml (**in `app` dir**) file example to create a secret instead to use the imperative command. But remember the values to use in the manifest file have to be in the base64 encoded.  

The application will be exposed on port `30080` to access outside of the Kubernetes cluster.   
The HPA controls the min and max number of pods and in our case, the minimum is 3 and the maximum is 5 pods. And the threshold to scale pods is *20% of load average*.  

## Test if the application works

The application is very simple.  
To test it, after the whole environment was deployed. Open a browser and access some node IP over HTTP protocol on port `30080`.  
It'll return a simple HTML page with some information like that:  
```
ID	Name	PhoneNumber	Company
1	John	(866) 490-3907	Company A  
2	Walsh	(831) 450-2422	Company B  
3	Walsh	(854) 481-3903	Company C  
```

If the page doesn't show that information, the application doesn't work well.  

## Application 

It is a python application (*python3.8*), it connect to a database when is started. When the application is started it'll check if the database configured in the manifests exist, also check if the table configures in the code (*mytable*) exist. If both don't exist they will be created and the database is populated with hard coded information.  
After http server is up, every access will querying the data in database and return the HTML page with those data.  