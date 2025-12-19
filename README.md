# Syslog Docker Environment

This Docker environment contains a syslog server, client, and web-based log viewer for testing and monitoring syslog traffic.

## Architecture

- **syslog-server**: Ubuntu-based container running rsyslog, listening on UDP/TCP port 514 and RELP port 601
- **syslog-client**: Ubuntu-based container with traffic generation scripts
- **log-viewer**: Web UI for viewing and filtering syslog messages in real-time (accessible at http://localhost:3000)

## Quick Start

1. **Start the environment:**
   ```bash
   docker-compose up -d
   ```

2. **Access the web UI:**
   Open http://localhost:3000 in your browser to view logs in real-time

3. **Test connectivity:**
   ```bash
   docker exec syslog-client /scripts/test_connection.sh
   ```

4. **View logs:**
   - **Web UI** (recommended): http://localhost:3000
   - **Command line**: 
     ```bash
     docker exec syslog-server tail -f /var/log/remote/all-remote.log
     ```

## Web Log Viewer Features

The web UI at http://localhost:3000 provides:

- **Real-time log viewing** with auto-refresh every 5 seconds
- **Multi-file selection** - view different log files (all-remote.log or host-specific logs)
- **Filtering** by search term and severity level
- **Color-coded severity levels** (emergency, alert, critical, error, warning, notice, info, debug)
- **Adjustable line count** (50 to 1000 lines)
- **Statistics** showing total files, size, and log count
- **Responsive design** for desktop and mobile viewing

## Traffic Generation Scripts

All scripts are available in the client container at `/scripts/`:

### 1. Basic Traffic Generator (`generate_traffic.sh`)
Sends random syslog messages with varying facilities and severities.

```bash
docker exec syslog-client /scripts/generate_traffic.sh
```

### 2. Burst Traffic Generator (`burst_traffic.sh`)
Sends bursts of messages for performance testing.

```bash
# Send 100 messages every 10 seconds (default)
docker exec syslog-client /scripts/burst_traffic.sh

# Custom: Send 500 messages every 30 seconds
docker exec syslog-client /scripts/burst_traffic.sh 500 30
```

### 3. Advanced Traffic Generator (`advanced_traffic.py`)
Python script with realistic application scenarios.

```bash
# Generate traffic from all scenarios
docker exec syslog-client python3 /scripts/advanced_traffic.py

# Generate traffic from specific scenario
docker exec syslog-client python3 /scripts/advanced_traffic.py web_server

# Available scenarios: web_server, database, security, application, all

# Custom interval (in seconds)
docker exec syslog-client python3 /scripts/advanced_traffic.py web_server 1.5
```

### 4. Test Connection (`test_connection.sh`)
Sends a single test message to verify connectivity.

```bash
docker exec syslog-client /scripts/test_connection.sh
```

## Viewing Logs

### All remote logs:
```bash
docker exec syslog-server tail -f /var/log/remote/all-remote.log
```

### Logs organized by hostname:
```bash
docker exec syslog-server ls -la /var/log/remote/syslog-client/
docker exec syslog-server tail -f /var/log/remote/syslog-client/local0.log
```

### Follow logs in real-time:
```bash
docker exec syslog-server tail -f /var/log/remote/all-remote.log
```

## Interactive Access

### Access client container:
```bash
docker exec -it syslog-client bash
```

### Access server container:
```bash
docker exec -it syslog-server bash
```

## Log Storage

Logs are persisted in a Docker volume named `syslog-logs` and mounted at `/var/log/remote` on the server.

## Network Configuration

Both containers are on the `syslog-net` bridge network and can communicate using their service names:
- Server hostname: `syslog-server`
- Client hostname: `syslog-client`

## Protocols Supported

- **UDP**: Port 514 (default syslog)
- **TCP**: Port 514 (reliable syslog)
- **RELP**: Port 601 (reliable event logging protocol)

## Stopping the Environment

```bash
docker-compose down
```

To also remove the logs volume:
```bash
docker-compose down -v
```

## Customization

- **Server config**: Edit `syslog-server/rsyslog.conf`
- **Add more scripts**: Place them in `syslog-client/scripts/`
- **Environment variables**: Modify `docker-compose.yml`
