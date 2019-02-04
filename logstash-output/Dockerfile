FROM docker.elastic.co/logstash/logstash:6.5.4

COPY jvm.options /usr/share/logstash/config/jvm.options
COPY logstash-output-azure-1.0.4.gem /usr/share/logstash/

RUN /usr/share/logstash/bin/logstash-plugin install /usr/share/logstash/logstash-output-azure-1.0.4.gem
RUN /usr/share/logstash/bin/logstash-plugin install logstash-output-syslog