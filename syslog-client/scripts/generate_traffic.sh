#!/bin/bash

# Simple syslog traffic generator using logger command
# Sends random syslog messages to the remote syslog server

SYSLOG_SERVER=${SYSLOG_SERVER:-syslog-server}
SYSLOG_PORT=${SYSLOG_PORT:-514}

# Facility and severity arrays
facilities=("kern" "user" "mail" "daemon" "auth" "syslog" "lpr" "news" "uucp" "cron" "authpriv" "local0" "local1" "local2" "local3" "local4" "local5" "local6" "local7")
severities=("emerg" "alert" "crit" "err" "warning" "notice" "info" "debug")

# Sample messages
messages=(
    "Application started successfully"
    "User authentication successful"
    "Database connection established"
    "Configuration file loaded"
    "Service initialized"
    "Request processed successfully"
    "Cache updated"
    "Scheduled task completed"
    "Warning: High memory usage detected"
    "Error: Connection timeout"
    "Critical: Disk space low"
    "Info: Backup completed"
    "Debug: Processing request from client"
    "Notice: Configuration changed"
    "Alert: Security violation detected"
    "Emergency: System failure imminent"
)

echo "Starting basic syslog traffic generator..."
echo "Target: ${SYSLOG_SERVER}:${SYSLOG_PORT}"
echo "Press Ctrl+C to stop"
echo ""

count=0
while true; do
    # Select random facility, severity, and message
    facility=${facilities[$RANDOM % ${#facilities[@]}]}
    severity=${severities[$RANDOM % ${#severities[@]}]}
    message=${messages[$RANDOM % ${#messages[@]}]}
    
    # Send syslog message
    logger -n ${SYSLOG_SERVER} -P ${SYSLOG_PORT} -t "client-app[$$]" -p ${facility}.${severity} "${message}"
    
    count=$((count + 1))
    echo "[${count}] Sent: ${facility}.${severity} - ${message}"
    
    # Random delay between 1-5 seconds
    sleep $((1 + RANDOM % 5))
done
