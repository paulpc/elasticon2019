# Logstash in Azure Kubernetes Services

Should you want to deploy logstash to Azure Kubernetes Services, you'll need a couple of setup things:
1. if you're using ECE, it makes a lot of sense to set up a secret with the ECE details
2. The outbound-logstash.yml file has a vanilla deployment of the container
3. the outbound-logstash-enrichment-blob uses an azure storage account as a static volume to load the intel files. It also sets up a persistent volume for the blob plugin to use as a local cache area before uploading to Azure Blob Storage

If you're using the containers for an inbound cluster, make sure to set up the load balancer.