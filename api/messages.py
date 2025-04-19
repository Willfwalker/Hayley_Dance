from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

# Path to the messages file
MESSAGES_FILE = os.path.join(os.path.dirname(__file__), '../messages.json')

def load_messages():
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading messages: {e}")
        return []

def save_messages(messages):
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving messages: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Check for password in query parameters
        query_components = {}
        query_string = self.path.split('?')
        if len(query_string) > 1:
            query_params = query_string[1].split('&')
            for param in query_params:
                if '=' in param:
                    name, value = param.split('=')
                    query_components[name] = value
        
        # Verify password
        if query_components.get('password') != 'HR1234':
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return
        
        # Return messages
        messages = load_messages()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(messages).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Add a new message
        messages = load_messages()
        messages.append({
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'subject': data.get('subject', ''),
            'message': data.get('message', ''),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        success = save_messages(messages)
        
        self.send_response(200 if success else 500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"success": success}
        self.wfile.write(json.dumps(response).encode())
