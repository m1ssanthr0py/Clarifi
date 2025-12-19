#!/bin/bash

# Burst traffic generator - sends lots of messages quickly
# Useful for testing syslog server performance

SYSLOG_SERVER=${SYSLOG_SERVER:-syslog-server}
SYSLOG_PORT=${SYSLOG_PORT:-514}
BURST_SIZE=${1:-100}  # Number of messages per burst
BURST_INTERVAL=${2:-10}  # Seconds between bursts

facilities=("local0" "local1" "local2" "local3" "local4" "local5" "local6" "local7")
severities=("info" "notice" "warning" "err")

echo "Starting burst syslog traffic generator..."
echo "Target: ${SYSLOG_SERVER}:${SYSLOG_PORT}"
echo "Burst size: ${BURST_SIZE} messages"
echo "Burst interval: ${BURST_INTERVAL} seconds"
echo "Press Ctrl+C to stop"
echo ""

burst_count=0
while true; do
    burst_count=$((burst_count + 1))
    echo "=== Burst #${burst_count} - Sending ${BURST_SIZE} messages ==="
    
    for i in $(seq 1 ${BURST_SIZE}); do
        facility=${facilities[$RANDOM % ${#facilities[@]}]}
        severity=${severities[$RANDOM % ${#severities[@]}]}
        
        logger -n ${SYSLOG_SERVER} -P ${SYSLOG_PORT} \
               -t "burst-test[$$]" \
               -p ${facility}.${severity} \
               "Burst ${burst_count} - Message ${i}/${BURST_SIZE} - Random data: ${RANDOM}"
        
        # Show progress every 10 messages
        if [ $((i % 10)) -eq 0 ]; then
            echo "  Progress: ${i}/${BURST_SIZE} messages sent"
        fi
    done
    
    echo "Burst #${burst_count} completed. Waiting ${BURST_INTERVAL} seconds..."
    sleep ${BURST_INTERVAL}
done
