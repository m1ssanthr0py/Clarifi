#!/usr/bin/env python3

"""
Advanced syslog traffic generator with multiple patterns and scenarios
Supports UDP and TCP protocols
"""

import socket
import time
import random
import sys
from datetime import datetime

SYSLOG_SERVER = "syslog-server"
SYSLOG_PORT = 514
USE_TCP = False  # Set to True for TCP, False for UDP

# Syslog facilities
FACILITIES = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23
}

# Syslog severities
SEVERITIES = {
    'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}

# Simulated application scenarios
SCENARIOS = {
    'web_server': {
        'tag': 'nginx',
        'messages': [
            ('info', 'GET /api/users HTTP/1.1 200'),
            ('info', 'POST /api/login HTTP/1.1 200'),
            ('warning', 'Slow query detected: 2.5s'),
            ('err', 'Connection refused to backend server'),
            ('notice', 'SSL certificate will expire in 30 days'),
        ]
    },
    'database': {
        'tag': 'postgres',
        'messages': [
            ('info', 'Database checkpoint completed'),
            ('notice', 'Connection from client 192.168.1.100'),
            ('warning', 'Query execution time exceeded threshold'),
            ('err', 'Could not establish replication connection'),
            ('crit', 'Database disk space critically low'),
        ]
    },
    'security': {
        'tag': 'sshd',
        'messages': [
            ('info', 'Accepted publickey for admin from 10.0.1.50'),
            ('warning', 'Failed password attempt for user root'),
            ('notice', 'Session opened for user admin'),
            ('alert', 'Multiple failed login attempts detected'),
            ('err', 'Invalid user attempt from 192.168.1.200'),
        ]
    },
    'application': {
        'tag': 'myapp',
        'messages': [
            ('debug', 'Processing request ID: REQ-{}'),
            ('info', 'User session created: SESSION-{}'),
            ('notice', 'Cache miss for key: cache_key_{}'),
            ('warning', 'Deprecated API endpoint accessed'),
            ('err', 'Failed to process payment transaction'),
        ]
    }
}


def create_syslog_message(facility, severity, tag, message, hostname='syslog-client'):
    """Create a properly formatted syslog message (RFC 3164)"""
    priority = FACILITIES[facility] * 8 + SEVERITIES[severity]
    timestamp = datetime.now().strftime('%b %d %H:%M:%S')
    msg = f"<{priority}>{timestamp} {hostname} {tag}: {message}"
    return msg.encode('utf-8')


def send_syslog_udp(message):
    """Send syslog message via UDP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message, (SYSLOG_SERVER, SYSLOG_PORT))
    finally:
        sock.close()


def send_syslog_tcp(message):
    """Send syslog message via TCP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SYSLOG_SERVER, SYSLOG_PORT))
        sock.sendall(message + b'\n')
    finally:
        sock.close()


def generate_traffic(interval=2, scenario=None):
    """Generate continuous syslog traffic"""
    print(f"Starting advanced syslog traffic generator...")
    print(f"Target: {SYSLOG_SERVER}:{SYSLOG_PORT}")
    print(f"Protocol: {'TCP' if USE_TCP else 'UDP'}")
    print(f"Scenario: {scenario if scenario else 'ALL'}")
    print(f"Press Ctrl+C to stop\n")
    
    send_func = send_syslog_tcp if USE_TCP else send_syslog_udp
    count = 0
    
    try:
        while True:
            # Select scenario
            if scenario and scenario in SCENARIOS:
                selected_scenario = scenario
            else:
                selected_scenario = random.choice(list(SCENARIOS.keys()))
            
            scenario_data = SCENARIOS[selected_scenario]
            tag = scenario_data['tag']
            severity, message = random.choice(scenario_data['messages'])
            
            # Format message with random data if it contains placeholders
            if '{}' in message:
                message = message.format(random.randint(1000, 9999))
            
            # Random facility weighted towards local facilities
            facility = random.choice(['local0', 'local1', 'local2', 'local3', 
                                     'local4', 'local5', 'local6', 'local7',
                                     'daemon', 'user', 'auth'])
            
            # Create and send message
            syslog_msg = create_syslog_message(facility, severity, tag, message)
            send_func(syslog_msg)
            
            count += 1
            print(f"[{count}] {selected_scenario:12} | {facility}.{severity:7} | {tag:10} | {message}")
            
            time.sleep(interval + random.uniform(-0.5, 0.5))
            
    except KeyboardInterrupt:
        print(f"\nStopped. Total messages sent: {count}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    scenario = sys.argv[1] if len(sys.argv) > 1 else None
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    
    if scenario and scenario not in SCENARIOS and scenario != 'all':
        print(f"Unknown scenario: {scenario}")
        print(f"Available scenarios: {', '.join(SCENARIOS.keys())}, all")
        sys.exit(1)
    
    generate_traffic(interval, scenario if scenario != 'all' else None)
