FROM python:3.6-alpine

# setting up the pip environment
RUN python3 -m pip install --upgrade pip
RUN apk add --no-cache g++ make libffi-dev openssl-dev
RUN python3 -m pip install azure-keyvault azure-common elasticsearch 

# setting up the user and the logging folder
RUN addgroup -S healthcheck && adduser -S -G healthcheck healthcheck 

COPY ece_check.py /opt/healthcheck/
COPY secret_helper.py /opt/healthcheck/
COPY alerts.py /opt/healthcheck/

COPY healthcheck_entry.sh /opt/healthcheck/
RUN chmod +xxx /opt/healthcheck/healthcheck_entry.sh

USER healthcheck

ENTRYPOINT ["/opt/healthcheck/healthcheck_entry.sh"]

CMD ["ece"] 