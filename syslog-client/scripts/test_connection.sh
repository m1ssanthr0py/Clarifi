#!/bin/bash

# Send a single test message to verify syslog connectivity

SYSLOG_SERVER=${SYSLOG_SERVER:-syslog-server}
SYSLOG_PORT=${SYSLOG_PORT:-514}

echo "Sending test message to ${SYSLOG_SERVER}:${SYSLOG_PORT}..."

logger -n ${SYSLOG_SERVER} -P ${SYSLOG_PORT} \
       -t "test[$$]" \
       -p local0.info \
       "TEST MESSAGE: This is a test syslog message from syslog-client at $(date)"

echo "Test message sent!"
echo ""
echo "To verify, run on the server:"
echo "  docker exec syslog-server tail /var/log/remote/all-remote.log"
