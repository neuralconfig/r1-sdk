#!/usr/bin/env python3
"""
RUCKUS Companion API for iPhone AR app
Handles SSH connections and RSSI polling via HTTP API
"""

from flask import Flask, jsonify, request
import paramiko
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Global connection state
ssh_connections = {}
connection_lock = threading.Lock()

# Hard-coded RUCKUS AP configuration (for testing)
RUCKUS_CONFIG = {
    "host": "192.168.37.118",
    "username": "admin", 
    "password": "os.getenv("RUCKUS_PASSWORD", "REDACTED")",
    "port": 22
}

class RUCKUSConnection:
    def __init__(self, connection_id, config):
        self.connection_id = connection_id
        self.config = config
        self.client = None
        self.shell = None
        self.connected = False
        self.last_activity = time.time()
        
    def connect(self):
        """Establish SSH connection to RUCKUS AP"""
        try:
            print(f"🔵 Connecting to RUCKUS AP at {self.config['host']}")
            
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to RUCKUS - try keyboard-interactive first
            try:
                # Try keyboard-interactive auth (what RUCKUS likely expects)
                def auth_handler(title, instructions, prompt_list):
                    """Handle keyboard-interactive prompts"""
                    print(f"🔵 Auth handler called - title: {title}")
                    print(f"🔵 Instructions: {instructions}")
                    responses = []
                    for prompt, show_input in prompt_list:
                        print(f"🔵 Prompt: {prompt}")
                        if "password" in prompt.lower():
                            responses.append(self.config['password'])
                        else:
                            responses.append(self.config['username'])
                    return responses
                
                self.client.connect(
                    hostname=self.config['host'],
                    port=self.config['port'],
                    username=self.config['username'],
                    password=self.config['password'],  # Try normal password first
                    timeout=15,
                    allow_agent=False,
                    look_for_keys=False,
                    auth_timeout=15
                )
                print("🔵 Connected with password auth")
                
            except paramiko.AuthenticationException as e:
                print(f"🔵 Password auth failed: {e}, trying keyboard-interactive...")
                
                # Try keyboard-interactive
                transport = paramiko.Transport((self.config['host'], self.config['port']))
                transport.connect()
                
                try:
                    transport.auth_interactive(self.config['username'], auth_handler)
                    print("🔵 Keyboard-interactive auth successful")
                    
                    # Create client from transport
                    self.client = paramiko.SSHClient()
                    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    self.client._transport = transport
                    
                except Exception as e:
                    print(f"🔵 Keyboard-interactive failed: {e}, trying none auth...")
                    
                    try:
                        transport.auth_none(self.config['username'])
                        print("🔵 None auth successful")
                    except:
                        print("🔵 None auth failed, but continuing...")
                    
                    # Create client from transport anyway
                    self.client = paramiko.SSHClient()
                    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    self.client._transport = transport
            
            # Open shell for interactive commands
            self.shell = self.client.invoke_shell()
            self.shell.settimeout(10)
            
            # Handle RUCKUS login prompts
            if self._handle_ruckus_login():
                self.connected = True
                self.last_activity = time.time()
                print(f"🟢 Connected to RUCKUS AP and authenticated")
                return True
            else:
                print("🔴 RUCKUS authentication failed")
                self.cleanup()
                return False
            
        except Exception as e:
            print(f"🔴 Connection failed: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()
            return False
            
    def _handle_ruckus_login(self):
        """Handle RUCKUS interactive login prompts"""
        print("🔵 Handling RUCKUS login prompts")
        
        # Wait for initial output
        time.sleep(2)
        
        # Read any initial output
        output = ""
        while self.shell.recv_ready():
            output += self.shell.recv(1024).decode('utf-8', errors='ignore')
            
        print(f"🔵 Initial output: {repr(output[:100])}")
        
        # Handle login prompts
        max_attempts = 15
        username_sent = False
        password_sent = False
        
        for attempt in range(max_attempts):
            if "Please login:" in output and not username_sent:
                print(f"🔵 Sending username (attempt {attempt + 1})")
                self.shell.send(f"{self.config['username']}\n")
                username_sent = True
                time.sleep(1)
                
            elif "password:" in output.lower() and not password_sent:
                print(f"🔵 Sending password (attempt {attempt + 1})")
                self.shell.send(f"{self.config['password']}\n")
                password_sent = True
                time.sleep(2)
                
            elif "rkscli:" in output:
                print("🟢 Reached RUCKUS CLI prompt")
                return True
                
            elif "Invalid" in output or "denied" in output.lower():
                print("🔴 Authentication failed")
                return False
                
            # Read more output
            time.sleep(1)
            new_output = ""
            while self.shell.recv_ready():
                chunk = self.shell.recv(1024).decode('utf-8', errors='ignore')
                new_output += chunk
                
            if new_output:
                output += new_output
                print(f"🔵 Additional output: {repr(new_output[:50])}")
            
        print("🔴 Login timeout - did not reach CLI prompt")
        return False
        
    def execute_command(self, command):
        """Execute command on RUCKUS AP"""
        if not self.connected or not self.shell:
            return {"error": "Not connected"}
            
        try:
            print(f"🔵 Executing: {command}")
            
            # Clear any pending output
            while self.shell.recv_ready():
                self.shell.recv(1024)
                
            # Send command
            self.shell.send(f"{command}\n")
            time.sleep(1)
            
            # Collect response
            output = ""
            timeout_count = 0
            max_timeout = 10
            
            while timeout_count < max_timeout:
                if self.shell.recv_ready():
                    chunk = self.shell.recv(4096).decode('utf-8', errors='ignore')
                    output += chunk
                    timeout_count = 0
                    
                    # Check if we got the prompt back (command complete)
                    if "rkscli:" in chunk:
                        break
                else:
                    time.sleep(0.5)
                    timeout_count += 1
                    
            self.last_activity = time.time()
            print(f"🟢 Command completed, output length: {len(output)}")
            
            return {"output": output, "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            print(f"🔴 Command execution failed: {e}")
            return {"error": str(e)}
            
    def cleanup(self):
        """Clean up connection"""
        self.connected = False
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()
        print(f"🔵 Connection {self.connection_id} cleaned up")


@app.route('/api/connect', methods=['POST'])
def connect_to_ruckus():
    """Connect to RUCKUS AP"""
    try:
        # Generate connection ID
        connection_id = f"ruckus_{int(time.time())}"
        
        with connection_lock:
            # Create new connection
            connection = RUCKUSConnection(connection_id, RUCKUS_CONFIG)
            
            if connection.connect():
                ssh_connections[connection_id] = connection
                
                return jsonify({
                    "success": True,
                    "connection_id": connection_id,
                    "message": "Connected to RUCKUS AP",
                    "ap_info": {
                        "host": RUCKUS_CONFIG["host"],
                        "username": RUCKUS_CONFIG["username"]
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to connect to RUCKUS AP"
                }), 500
                
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/rssi/<connection_id>', methods=['GET'])
def get_rssi(connection_id):
    """Get RSSI data for a client MAC address"""
    try:
        # Get client MAC from query parameters
        client_mac = request.args.get('mac')
        if not client_mac:
            return jsonify({
                "success": False,
                "error": "Missing 'mac' parameter"
            }), 400
            
        with connection_lock:
            connection = ssh_connections.get(connection_id)
            if not connection or not connection.connected:
                return jsonify({
                    "success": False,
                    "error": "Connection not found or not connected"
                }), 404
                
            # Execute RUCKUS command to get station stats
            command = f"get station wlan33 stats {client_mac}"
            result = connection.execute_command(command)
            
            if "error" in result:
                return jsonify({
                    "success": False,
                    "error": result["error"]
                }), 500
                
            # Parse RSSI from output
            rssi_data = parse_rssi_output(result["output"])
            
            return jsonify({
                "success": True,
                "connection_id": connection_id,
                "client_mac": client_mac,
                "rssi_data": rssi_data,
                "timestamp": result["timestamp"],
                "raw_output": result["output"]
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/disconnect/<connection_id>', methods=['POST'])
def disconnect_from_ruckus(connection_id):
    """Disconnect from RUCKUS AP"""
    try:
        with connection_lock:
            connection = ssh_connections.get(connection_id)
            if connection:
                connection.cleanup()
                del ssh_connections[connection_id]
                
                return jsonify({
                    "success": True,
                    "message": f"Disconnected from {connection_id}"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Connection not found"
                }), 404
                
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get API status and active connections"""
    with connection_lock:
        active_connections = []
        for conn_id, conn in ssh_connections.items():
            active_connections.append({
                "connection_id": conn_id,
                "connected": conn.connected,
                "last_activity": datetime.fromtimestamp(conn.last_activity).isoformat(),
                "ap_host": conn.config["host"]
            })
            
    return jsonify({
        "success": True,
        "api_status": "running",
        "active_connections": len(ssh_connections),
        "connections": active_connections
    })


def parse_rssi_output(output):
    """Parse RSSI data from RUCKUS command output"""
    rssi_data = {
        "rssi_dbm": None,
        "signal_strength": None,
        "found": False
    }
    
    try:
        lines = output.split('\n')
        for line in lines:
            line = line.strip().lower()
            if 'rssi' in line:
                # Try to extract RSSI value
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'rssi' in part and i + 1 < len(parts):
                        try:
                            rssi_value = int(parts[i + 1])
                            rssi_data["rssi_dbm"] = rssi_value
                            rssi_data["found"] = True
                            
                            # Convert to signal strength percentage (rough approximation)
                            # RSSI typically ranges from -30 (excellent) to -90 (poor)
                            if rssi_value >= -30:
                                strength = 100
                            elif rssi_value <= -90:
                                strength = 0
                            else:
                                strength = int(((rssi_value + 90) / 60) * 100)
                                
                            rssi_data["signal_strength"] = max(0, min(100, strength))
                            break
                        except ValueError:
                            continue
                            
    except Exception as e:
        print(f"🔴 RSSI parsing error: {e}")
        
    return rssi_data


def cleanup_old_connections():
    """Clean up old inactive connections"""
    while True:
        time.sleep(300)  # Check every 5 minutes
        current_time = time.time()
        
        with connection_lock:
            to_remove = []
            for conn_id, connection in ssh_connections.items():
                if current_time - connection.last_activity > 1800:  # 30 minutes
                    print(f"🔵 Cleaning up inactive connection: {conn_id}")
                    connection.cleanup()
                    to_remove.append(conn_id)
                    
            for conn_id in to_remove:
                del ssh_connections[conn_id]


if __name__ == '__main__':
    print("🚀 Starting RUCKUS Companion API")
    print(f"🔵 Configured for RUCKUS AP: {RUCKUS_CONFIG['host']}")
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_connections, daemon=True)
    cleanup_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)