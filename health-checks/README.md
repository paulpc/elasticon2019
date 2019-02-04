# ECE Health Checks
Scripts that have proven useful to continuously check our ECE instance. The will check:
1. successful auth to ECE cluster
2. you have more than 0 clusters
3. unhealthy clusters
    - due to shards
    - or something else
4. unhealthy instances
5. high memory pressure (JVM over 70% on number of configured instances)
6. succesfully able to index 5 documents - otherwise, there are pressure issues
7. successful health probe to the logging cluster

The script is designed to be deployed to AKS (see the yaml file in the AKS folder) and does some fun secrets gymnastics:
- kubernetes will hold the azureAD app details and the secret
- this app has access to an Azure KeyVault that stores the JSON configuration for the script as the secret
- the container will download and use the KeyVault secret value
- check out the secret-template.json for what the secret should look like
    - url: the ece url
    - username: readonly user for the cluster - please don't use root
    - password: you know...
    - logurl: logging cluster url (this is the cluster you care about)
    - teams: microsoft teams webhook to send messages
    - memtr: memory pressure threshold - number of nodes where it's acceptable to have a 70% and above JVM utilization.