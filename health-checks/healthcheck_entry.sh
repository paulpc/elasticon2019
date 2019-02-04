#!/bin/sh
if [ "$1" = 'ece' ]; then
        python3 /opt/healthcheck/ece_check.py
else
    exec "$@"
fi