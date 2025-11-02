from flask import Flask, render_template, request, jsonify
import requests
import time
import random
import threading
import os
import re
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'aahan-cookie-bot-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

tasks = {}

class FacebookMessageBot:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with cookies"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
        # Set cookies from config
        cookies = self.config.get('cookies', [])
        for cookie in cookies:
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                name = name.strip()
                value = value.strip()
                if name and value:
                    self.session.cookies.set(name, value, domain='.facebook.com')
    
    def parse_facebook_cookies(self, cookie_string):
        """Parse Facebook cookie string into individual cookies"""
        cookies = []
        # Split by semicolon and clean up
        cookie_pairs = cookie_string.split(';')
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                name = name.strip()
                value = value.strip()
                if name and value:
                    cookies.append({'name': name, 'value': value})
        return cookies
    
    def get_fb_dtsg(self):
        """Get fb_dtsg token from Facebook"""
        try:
            response = self.session.get('https://www.facebook.com/', timeout=10)
            if response.status_code == 200:
                patterns = [
                    r'name="fb_dtsg" value="([^"]+)"',
                    r'"token":"([^"]+)"',
                    r'fb_dtsg" value="([^"]+)"'
                ]
                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        return match.group(1)
            return "AQHXYZ"
        except Exception as e:
            print(f"Error getting fb_dtsg: {e}")
            return "AQHXYZ"
    
    def get_user_id(self, username):
        """Get user ID from username"""
        try:
            url = f"https://www.facebook.com/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                patterns = [
                    r'"userID":"(\d+)"',
                    r'{"id":"(\d+)"',
                    r'fbid:(\d+)',
                    r'content="fb://profile/(\d+)"',
                    r'"actorID":"(\d+)"'
                ]
                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        return match.group(1)
            
            # If can't find ID, use username as fallback
            return username
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return username
    
    def validate_session(self):
        """Validate if cookies are working"""
        try:
            response = self.session.get('https://www.facebook.com/me', timeout=10, allow_redirects=False)
            
            # Check if we're redirected to login page
            if response.status_code == 200 and "login" not in response.url:
                return True
            
            # Additional check for content
            if "c_user" in response.text or "fb_dtsg" in response.text:
                return True
                
            return False
        except Exception as e:
            print(f"Session validation error: {e}")
            return False
    
    def send_facebook_message(self, user_id, message, task_id):
        """Send message using Facebook's messaging API"""
        try:
            # Get required tokens
            fb_dtsg = self.get_fb_dtsg()
            if not fb_dtsg or fb_dtsg == "AQHXYZ":
                return False, "Could not get Facebook token"
            
            # Prepare message data
            message_data = {
                'action_type': 'ma-type:user-generated-message',
                'body': message,
                'ephemeral_ttl_mode': '0',
                'fb_dtsg': fb_dtsg,
                'has_attachment': 'false',
                'message_id': str(int(time.time() * 1000)),
                'offline_threading_id': str(int(time.time() * 1000)),
                'source': 'source:chat:web',
                'specific_to_list[0]': f'fbid:{user_id}',
                'timestamp': str(int(time.time() * 1000)),
                'ui_push_phase': 'C3',
                'waterfall_source': 'message'
            }
            
            # Send message
            send_url = "https://www.facebook.com/messaging/send/"
            response = self.session.post(send_url, data=message_data, timeout=15)
            
            if response.status_code == 200:
                # Check if message was actually sent
                if 'send_success' in response.text.lower() or 'success' in response.text.lower():
                    return True, "Message sent successfully"
                else:
                    return False, "Message might not have been delivered"
            else:
                return False, f"HTTP Error: {response.status_code}"
                
        except Exception as e:
            return False, f"Network error: {str(e)}"
    
    def run_messaging(self, task_id):
        """Main messaging function"""
        try:
            tasks[task_id] = {
                'status': 'running',
                'progress': 0,
                'message': 'Starting AAHAN Bot...',
                'logs': [],
                'sent': 0,
                'failed': 0,
                'total_messages': 0
            }
            
            # Get config
            uid = self.config.get('uid', '')
            hater_name = self.config.get('hater_name', '')
            speed_seconds = self.config.get('speed_seconds', 30)
            messages = self.config.get('messages', [])
            
            tasks[task_id]['logs'].append('🚀 AAHAN Facebook Bot Started')
            tasks[task_id]['logs'].append(f'🎯 Target: {hater_name}')
            tasks[task_id]['logs'].append(f'⏱️ Speed: {speed_seconds} seconds')
            tasks[task_id]['logs'].append(f'🆔 UID: {uid}')
            tasks[task_id]['logs'].append(f'💬 Messages loaded: {len(messages)}')
            
            # Validate cookies
            tasks[task_id]['progress'] = 10
            tasks[task_id]['message'] = 'Validating Facebook cookies...'
            
            if not self.validate_session():
                tasks[task_id]['status'] = 'error'
                tasks[task_id]['message'] = '❌ Invalid cookies! Facebook login failed.'
                tasks[task_id]['logs'].append('❌ Cookie validation failed - Please check your cookies')
                return
            
            tasks[task_id]['progress'] = 30
            tasks[task_id]['message'] = '✅ Cookies working! Getting user info...'
            tasks[task_id]['logs'].append('✅ Facebook cookies validated successfully')
            
            # Get user ID
            user_id = self.get_user_id(hater_name)
            tasks[task_id]['logs'].append(f'📞 User ID resolved: {user_id}')
            
            # Check messages
            if not messages:
                tasks[task_id]['status'] = 'error'
                tasks[task_id]['message'] = '❌ No messages found!'
                tasks[task_id]['logs'].append('❌ No messages loaded from file')
                return
            
            total_messages = len(messages)
            tasks[task_id]['total_messages'] = total_messages
            tasks[task_id]['logs'].append(f'📨 Ready to send {total_messages} messages...')
            
            # Send messages
            for i, message in enumerate(messages):
                try:
                    current_msg = i + 1
                    tasks[task_id]['message'] = f'Sending {current_msg}/{total_messages}'
                    
                    # Send message with retry logic
                    success, result = self.send_facebook_message(user_id, message, task_id)
                    
                    if success:
                        tasks[task_id]['logs'].append(f'✅ {current_msg}. Sent: {message}')
                        tasks[task_id]['sent'] += 1
                    else:
                        tasks[task_id]['logs'].append(f'❌ {current_msg}. Failed: {result}')
                        tasks[task_id]['failed'] += 1
                    
                    # Update progress
                    progress = 30 + (i * 65 / total_messages)
                    tasks[task_id]['progress'] = min(95, progress)
                    
                    # Random delay to avoid detection
                    delay = speed_seconds + random.randint(2, 8)
                    time.sleep(delay)
                    
                except Exception as e:
                    tasks[task_id]['logs'].append(f'⚠️ {i+1}. Error: {str(e)}')
                    tasks[task_id]['failed'] += 1
                    time.sleep(10)  # Longer delay on error
            
            # Complete
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['progress'] = 100
            success_rate = (tasks[task_id]['sent'] / total_messages) * 100
            tasks[task_id]['message'] = f'✅ Completed! {tasks[task_id]["sent"]}/{total_messages} sent ({success_rate:.1f}% success)'
            tasks[task_id]['logs'].append(f'🎉 Bot finished! Success rate: {success_rate:.1f}%')
            
        except Exception as e:
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['message'] = f'❌ Bot error: {str(e)}'
            tasks[task_id]['logs'].append(f'❌ Critical error: {str(e)}')

def parse_cookie_file(content):
    """Parse cookie content from file"""
    lines = []
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            lines.append(line)
    return lines

def parse_cookie_text(text):
    """Parse cookie content from text"""
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            lines.append(line)
    return lines

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_bot():
    try:
        # Get form data
        cookies_file = request.files.get('cookies_file')
        cookies_text = request.form.get('cookies_text', '')
        messages_file = request.files.get('messages_file')
        messages_text = request.form.get('messages_text', '')
        uid = request.form.get('uid', '')
        hater_name = request.form.get('hater_name', '')
        speed_seconds = int(request.form.get('speed_seconds', 30))
        
        # Parse cookies
        cookies = []
        if cookies_file and cookies_file.filename:
            file_content = cookies_file.read()
            cookies = parse_cookie_file(file_content)
        elif cookies_text:
            cookies = parse_cookie_text(cookies_text)
        
        # Parse messages
        messages = []
        if messages_file and messages_file.filename:
            file_content = messages_file.read()
            messages = parse_cookie_file(file_content)
        elif messages_text:
            messages = parse_cookie_text(messages_text)
        
        # Validate inputs
        if not cookies:
            return jsonify({'error': 'No cookies provided! Please upload cookies file or paste cookies.'}), 400
        
        if not messages:
            return jsonify({'error': 'No messages provided! Please upload messages file or paste messages.'}), 400
            
        if not uid:
            return jsonify({'error': 'Facebook UID is required!'}), 400
            
        if not hater_name:
            return jsonify({'error': 'Target username is required!'}), 400
        
        # Generate task ID
        task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create config
        config = {
            'cookies': cookies,
            'messages': messages,
            'uid': uid,
            'hater_name': hater_name,
            'speed_seconds': speed_seconds
        }
        
        # Start bot
        bot = FacebookMessageBot(config)
        thread = threading.Thread(target=bot.run_messaging, args=(task_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Bot started successfully! Processing...'
        })
        
    except Exception as e:
        return jsonify({'error': f'Start error: {str(e)}'}), 500

@app.route('/api/status/<task_id>')
def get_status(task_id):
    status = tasks.get(task_id, {
        'status': 'not_found',
        'progress': 0,
        'message': 'Task not found',
        'logs': [],
        'sent': 0,
        'failed': 0,
        'total_messages': 0
    })
    return jsonify(status)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'AAHAN Facebook Bot',
        'timestamp': time.time(),
        'active_tasks': len([t for t in tasks.values() if t.get('status') == 'running'])
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
