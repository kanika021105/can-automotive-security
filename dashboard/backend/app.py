#!/usr/bin/env python3
"""
CAN Bus Dashboard Backend
Flask server with WebSocket for real-time CAN traffic
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import can
import threading
import time
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'can-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# CAN bus connection
bus = None
is_monitoring = False
message_count = 0
attack_count = 0

# Store recent messages
recent_messages = []
MAX_MESSAGES = 100

def init_can():
    """Initialize CAN bus connection"""
    global bus
    try:
        bus = can.interface.Bus(channel='vcan0', interface='socketcan')
        return True
    except Exception as e:
        print(f" CAN initialization failed: {e}")
        return False

def monitor_can():
    """Monitor CAN bus and send messages via WebSocket"""
    global bus, is_monitoring, message_count, attack_count, recent_messages
    
    if bus is None:
        return
    
    is_monitoring = True
    last_messages = []
    sequence_length = 4
    seen_sequences = {}
    
    print("📡 CAN Monitoring Started")
    
    while is_monitoring:
        try:
            msg = bus.recv(timeout=1.0)
            
            if msg is not None:
                message_count += 1
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                data_hex = ' '.join(f'{b:02X}' for b in msg.data)
                
                # Create message dict
                message_data = {
                    'id': message_count,
                    'timestamp': timestamp,
                    'can_id': hex(msg.arbitration_id),
                    'data': data_hex,
                    'length': len(msg.data)
                }
                
                # Store recent messages
                recent_messages.append(message_data)
                if len(recent_messages) > MAX_MESSAGES:
                    recent_messages.pop(0)
                
                # Check for replay attack (sequence detection)
                last_messages.append((msg.arbitration_id, bytes(msg.data)))
                if len(last_messages) > sequence_length:
                    last_messages.pop(0)
                
                if len(last_messages) == sequence_length:
                    sequence = tuple(last_messages)
                    if sequence in seen_sequences:
                        seen_sequences[sequence] += 1
                        if seen_sequences[sequence] >= 2:
                            attack_count += 1
                            # Send attack alert
                            socketio.emit('attack_alert', {
                                'message': message_data,
                                'attack_id': attack_count,
                                'sequence': str(sequence),
                                'repetitions': seen_sequences[sequence]
                            })
                    else:
                        seen_sequences[sequence] = 1
                
                # Send live message to frontend
                socketio.emit('can_message', message_data)
                
        except Exception as e:
            print(f"Error monitoring: {e}")
            break

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    return jsonify({
        'total_messages': message_count,
        'total_attacks': attack_count,
        'recent_messages': recent_messages[-10:]
    })

@app.route('/api/start')
def start_monitoring():
    """Start CAN monitoring"""
    global is_monitoring
    if not is_monitoring:
        thread = threading.Thread(target=monitor_can)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already running'})

@app.route('/api/stop')
def stop_monitoring():
    """Stop CAN monitoring"""
    global is_monitoring
    is_monitoring = False
    return jsonify({'status': 'stopped'})

@app.route('/api/clear')
def clear_stats():
    """Clear statistics"""
    global message_count, attack_count, recent_messages
    message_count = 0
    attack_count = 0
    recent_messages = []
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    print("CAN Bus Dashboard Backend Starting...")
    if init_can():
        print(" Connected to CAN bus")
        # Start monitoring automatically
        thread = threading.Thread(target=monitor_can)
        thread.daemon = True
        thread.start()
        print(" Monitoring started")
        print(" Open http://localhost:5000 in your browser")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        print(" Failed to connect to CAN bus")
