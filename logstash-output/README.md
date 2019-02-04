# Logstash Outbound Container

Scripts to create your own logstash container with the syslog and outbound-blob plugin. If you want to pull my container, check it out at:

```docker pull p4ulpc/logstash-outbound:6.5.4```

Should you want to build it yourself, try out:

```docker build -t logstash-outbound:6.5.4 .```

Notice the local files that get uploaded
- jvm.options - overwriting the jvm options to have more memory. By default, you get 1GB
- logstash-output-azure - installing the custom plugin

The container does not use local plugins, but relies on ECE centrally managed ones. As such, you'll need the following OS variables:
- XPACK_MANAGEMENT_ENABLED
- XPACK_MANAGEMENT_PIPELINE_ID
- XPACK_MANAGEMENT_ELASTICSEARCH_URL
- XPACK_MONITORING_ELASTICSEARCH_URL
- XPACK_MANAGEMENT_ELASTICSEARCH_USERNAME
- XPACK_MONITORING_ELASTICSEARCH_USERNAME
- XPACK_MANAGEMENT_ELASTICSEARCH_PASSWORD
- XPACK_MONITORING_ELASTICSEARCH_PASSWORD

To run the container locally you can use a file for the parameters:

```docker run --env-file logstash.env -d p4ulpc/logstash-outbound:6.5.4```

If you are using cloud Elastic, you can use the cloud id in strad of all the monitoring / management options.

If you're using local pipelines, try out the stuff in the elastic docs: https://www.elastic.co/guide/en/logstash/current/docker-config.html
