# mstakx
Things to do before executing:-

 * The cred_path below is the credentials file from GCP in order to access the project. Kindly make sure to provide owner access in IAM and download them in local directory. 
 
 * Create a cluster and project using the GUI in GCP and place it under the reqpective variable below. (I did not get time to create the cluster object as it had a lot of entries in json. An easy way is to create it in GUI as it has been preloaded with a template)
 
 * Provide GKE api access in order for the below script to work.
 
usage: playbookfile.py [-h] --project_id PROJECT_ID --cred_path CRED_PATH
                       --cluster_id CLUSTER_ID --zone ZONE [--pdb]

optional arguments:
  -h, --help            show this help message and exit
  --project_id PROJECT_ID
                        Project id
  --cred_path CRED_PATH
                        Location of the credential file
  --cluster_id CLUSTER_ID
                        name of the cluster
  --zone ZONE           Zone of the cluster
  --pdb                 To enable pdb


  

Q&A:
What was the node size chosen for the Kubernetes nodes? And why?
   <br /> Nodes chosed is 3 as per the guestbook application as there were many pods for it and already the kube-system had many other GCP related pods running. So inorder for sufficient CPU for each pod creation 3 Nodes were chosen. 

What method was chosen to install the demo application and ingress controller on the cluster, justify the
method used.
   <br /> A simple kubectl apply -f <filename> is used. This is been incorporated in the utils method of kubernetes. This is an easy go way to deploy as the changes are to be made only in the yaml file. You can also do it via individual functions like the one I had did for creating namespace, but that takes more time and code complexity. 
 
What would be your chosen solution to monitor the application on the cluster and why?What additional components / plugins would you install on the cluster to manage it better?

   <br /> Prometheus and heapster are the application that GKE provides by default and I feel these two are sufficient as it provides good features and supported by a big community. 
  
  
