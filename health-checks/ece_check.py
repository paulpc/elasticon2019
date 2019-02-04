#!/bin/python
import requests
from requests.auth import HTTPBasicAuth
import json
import logging
import os
import datetime
from secret_helper import SecretHelper
from elasticsearch import Elasticsearch
from alerts import alert, internal_teams_message

if __name__ == "__main__":
    """ece check scripts"""
    logging.basicConfig(level=logging.INFO)
    # parsing environmental variables for the vault specifics for this deployment
    if "APPID" in os.environ:
        appid = os.environ["APPID"]
    if "TENANT" in os.environ:
        tenant = os.environ["TENANT"]
    if "APPKEY" in os.environ:
        key = os.environ["APPKEY"]
    if "RESOURCE" in os.environ:
        resource = os.environ["RESOURCE"]
    else:
        resource = "https://vault.azure.net"
    if "VAULT" in os.environ:
        vbu = "https://%s.vault.azure.net" % os.environ["VAULT"]
    if "KEYVAULTSECRET" in os.environ:
        kvs = os.environ["KEYVAULTSECRET"]
    else:
        kvs = "ece-health-settings"

    if not(appid and tenant and key and vbu):
        logging.critical("[---] you need to have the right evironment variables; looking for APPID, APPKEY, TENANT, RESOURCE, VAULT")
        exit()
     # initializing the secret helper
    sh = SecretHelper(client_id=appid, secret=key, tenant=tenant, resource=resource)
    # domain and documentdb settings
    conf = json.loads(sh.get_secret(vbu, kvs).value)
    # set up connection to ES
    logging.info("set up connection to ES")
    es=Elasticsearch(hosts=conf['logurl'])

    try:
        response = requests.get(url=conf['url']+"/api/v1/clusters/elasticsearch", auth=HTTPBasicAuth(conf['username'], conf['password']), verify=False)
        if response.status_code == 200:
            logging.info("ece api seems to work; status code: %d" % response.status_code)
            resp_dict = response.json()
            if resp_dict['return_count'] == 0:
                internal_teams_message("we have somehow managed to misplaced all the ElasticSearch clusters - time to freak out","Elastic Cloud Enterprise",conf['teams'], "DC143C")
                logging.critical("we have somehow managed to misplaced all the ElasticSearch clusters - time to freak out")

            else:
                esproblem = False
                for cluster in resp_dict['elasticsearch_clusters']:
                    logging.info("%s - %s" % (str(cluster['cluster_name']), str(cluster['plan_info']['healthy'])))
                    if not cluster['plan_info']['healthy']:
                        # let's figure out why it is unhealthy
                        if not cluster['elasticsearch']['healthy']:
                            message = "cluster %s is unhealthy because of elasticsearch" % (cluster['cluster_name'])
                            logging.error(message)
                            message += "\nunavailable shards:\n"
                            for shard in cluster['elasticsearch']['shard_info']['unavailable_shards']:
                                logging.error("unavailable shard: %s" % (str(shard)))
                                message += "* %s\n" % (str(shard))
                            esproblem = True
                            internal_teams_message(message, "Elastic Search", conf['teams'], "FFD700")

                        else:
                            message="cluster %s is unhealthy for unknown reasons" % (cluster['cluster_name'])
                            logging.error("unhealthy cluster: %s" % (str(cluster['plan_info'])))
                            esproblem = True
                            internal_teams_message(message, "Elastic Search", conf['teams'], "FFD700")
                    else:
                        # checking memory pressure
                        mem_issues = {}
                        unhealthy_instances = []
                        for instance in cluster['topology']['instances']:
                            if not instance['healthy']:
                                # unhealthy instance alerts
                                unhealthy_instances.append(instance['instance_name'])
                            if instance['memory']['memory_pressure'] > 70:
                                mem_issues[instance['instance_name']] = instance['memory']['memory_pressure']
                        if unhealthy_instances:
                            message = "cluster %s is has unhealthy instances: %s" % (cluster['cluster_name'], ", ".join(unhealthy_instances))
                            logging.warn(message)
                            internal_teams_message(message, "Elastic Search Instance issues", conf['teams'], "FFD700")
                            esproblem = True
                        if len(mem_issues) >= conf['memtr']:
                            # more than ten instances are getting close to the 75% memory threshold, I should tell someone
                            message = "cluster %s is starting to have memory pressure: %s" % (cluster['cluster_name'], mem_issues)
                            esproblem = True
                            logging.warn(message)
                            internal_teams_message(message, "Elastic Search memory pressure", conf['teams'], "FFD700")
                # checking if we can index and retrieve information to in the logging cluster
                essuccess=0
                esfail=0
                for i in range(5):
                    try:
                        res = es.index(index='healthchecks', doc_type="doc", body={"timestamp":datetime.datetime.now().isoformat(),"status":"succes"})
                        logging.info("indexing document: %s" % (str(res['result'])))
                        if res['result'] == 'created':
                            essuccess +=1
                        else:
                            esfail+=1
                    except:
                        esfail+=1
                        logging.error("troubles indexing document: %s" % (str(res['result'])))
                if esfail > 0:
                    message="logging cluster is unhealthy %d/5 attempts at indexing failed" % (esfail)
                    internal_teams_message(message, "Elastic Search", conf['teams'], "FFD700")
                    esproblem = True
                logging.info("indexed %d documents" % (essuccess))
                
                try: 
                    es_res = requests.get(url=conf['logurl']+"_cluster/health", verify=False)
                    if es_res.status_code == 200:
                        erj = es_res.json()
                        msg = ""
                        for key in erj:
                            msg += "%s: %s<br>" % (key.replace("_"," "), erj[key])
                        if erj['status'] == 'green':
                            color = "33FF44"
                        elif erj['status'] == 'yellow':
                            color = "FFFC33"
                        else:
                            color = "FF3333"
                            esproblem = True
                        if esproblem:
                            internal_teams_message(msg, "Elastic Search Details", conf['teams'], color)
                        erj['timestamp'] = datetime.datetime.now().isoformat()
                    else:
                        logging.error("unable to get my info from the cluster due to http issues")
                        internal_teams_message("Unable to get additional information from the logging analytics cluster due to HTTP errors %s" % es_res.text, "Elastic Search", conf['teams'], "FF3333")
                except:
                    logging.error("unable to get any info from the cluster")
                    internal_teams_message("Unable to get additional information from the logging analytics cluster due to unknown errors", "Elastic Search", conf['teams'], "FF3333")

        elif response.status_code == 401:
            internal_teams_message("I cannot Authenticate to ECE - probably fix the json file","Elastic Cloud Enterprise", conf['teams'], "FFD700")
            logging.error("I cannot Authenticate to ECE - probably fix the json file")

        else:
            internal_teams_message("ECE is responding with an error message %s" % response.text,"Elastic Cloud Enterprise", conf['teams'], "DC143C")
            logging.error("ECE is responding with an error message %s" % response.text)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        internal_teams_message("ECE console is timing out", "Elastic Cloud Enterprise", conf['teams'], "DC143C")
        logging.error("ECE console is timing out")
    except Exception as inst:
        internal_teams_message("Some other error while hitting ECE", "Elastic Cloud Enterprise", conf['teams'], "DC143C")
        logging.error("Some other error while hitting ECE - %s " % str(inst))