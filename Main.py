import requests
import json
import time
import random
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

class AAHANFacebookBot:
    def __init__(self):
        self.config_file = "aahan_config.json"
        self.load_config()
        self.session = requests.Session()
        self.setup_headers()
        
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print("✅ Configuration loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        self.config = {
            "cookies": [],
            "uid": "",
            "hater_name": "",
            "speed": 5,
            "max_actions": 10,
            "actions": {
                "like_posts": True,
                "comment_posts": False,
                "share_posts": False,
                "add_friends": False
            },
            "comments": [
                "Nice post! 👍",
                "Great content! 👏",
                "Awesome! 😊",
                "Good one! ✨",
                "Thanks for sharing! 🙏"
            ]
        }
        self.save_config()
        print("📝 Default configuration created. Please edit aahan_config.json")
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def setup_headers(self):
        """Setup request headers"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
        }
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--log-level=3")
            
            # Try to use chromedriver from PATH
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            print(f"❌ ChromeDriver error: {e}")
            print("🔧 Please install ChromeDriver or check installation")
            return None
    
    def add_cookies_to_driver(self, driver):
        """Add cookies to browser session"""
        try:
            driver.get("https://facebook.com")
            time.sleep(2)
            
            for cookie in self.config['cookies']:
                if 'domain' not in cookie:
                    cookie['domain'] = '.facebook.com'
                try:
                    driver.add_cookie(cookie)
                except:
                    continue
            
            driver.refresh()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Error adding cookies: {e}")
            return False
    
    def automate_likes(self, driver):
        """Automate liking posts"""
        print("🚀 Starting like automation...")
        
        try:
            # Scroll to load posts
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Find like buttons
            like_selectors = [
                "//div[@role='button' and contains(@aria-label, 'Like')]",
                "//span[text()='Like']",
                "//a[contains(@aria-label, 'Like')]"
            ]
            
            like_buttons = []
            for selector in like_selectors:
                like_buttons = driver.find_elements(By.XPATH, selector)
                if like_buttons:
                    break
            
            actions_performed = 0
            for i, button in enumerate(like_buttons[:self.config['max_actions']]):
                try:
                    driver.execute_script("arguments[0].click();", button)
                    print(f"✅ Liked post {i+1}")
                    actions_performed += 1
                    
                    # Random delay based on speed
                    delay = self.calculate_delay()
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"❌ Could not like post {i+1}: {e}")
            
            print(f"🎯 Total likes: {actions_performed}")
            return actions_performed
            
        except Exception as e:
            print(f"❌ Error in like automation: {e}")
            return 0
    
    def automate_comments(self, driver):
        """Automate commenting on posts"""
        if not self.config['actions']['comment_posts']:
            return 0
            
        print("💬 Starting comment automation...")
        
        try:
            comment_buttons = driver.find_elements(By.XPATH, "//div[@role='button' and contains(@aria-label, 'Comment')]")
            
            actions_performed = 0
            for i, button in enumerate(comment_buttons[:self.config['max_actions']//2]):
                try:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(2)
                    
                    # Find comment box
                    comment_boxes = driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
                    if comment_boxes:
                        comment_text = random.choice(self.config['comments'])
                        comment_boxes[-1].send_keys(comment_text)
                        time.sleep(1)
                        
                        # Find submit button
                        submit_buttons = driver.find_elements(By.XPATH, "//div[@role='button' and contains(@aria-label, 'Comment')]")
                        for btn in submit_buttons:
                            if 'Comment' in btn.get_attribute('innerHTML'):
                                driver.execute_script("arguments[0].click();", btn)
                                break
                        
                        print(f"✅ Commented on post {i+1}: {comment_text}")
                        actions_performed += 1
                        
                        delay = self.calculate_delay()
                        time.sleep(delay)
                    
                except Exception as e:
                    print(f"❌ Could not comment on post {i+1}: {e}")
            
            print(f"🎯 Total comments: {actions_performed}")
            return actions_performed
            
        except Exception as e:
            print(f"❌ Error in comment automation: {e}")
            return 0
    
    def calculate_delay(self):
        """Calculate random delay based on speed setting"""
        base_delay = 11 - self.config['speed']  # 1=10s, 10=1s
        random_variation = random.uniform(0.5, 2.0)
        return base_delay * random_variation
    
    def validate_cookies(self):
        """Validate if cookies are working"""
        if not self.config['cookies']:
            print("❌ No cookies found in configuration")
            return False
        
        print("🔍 Validating cookies...")
        driver = self.setup_driver()
        if not driver:
            return False
        
        try:
            if self.add_cookies_to_driver(driver):
                driver.get("https://facebook.com/me")
                time.sleep(3)
                
                if "facebook.com" in driver.current_url and "login" not in driver.current_url:
                    print("✅ Cookies are valid!")
                    driver.quit()
                    return True
                else:
                    print("❌ Cookies are invalid or expired")
                    driver.quit()
                    return False
            else:
                driver.quit()
                return False
                
        except Exception as e:
            print(f"❌ Error validating cookies: {e}")
            driver.quit()
            return False
    
    def run_automation(self):
        """Main automation runner"""
        print("\n" + "="*60)
        print("🎯 AAHAN FACEBOOK AUTOMATION STARTING")
        print("="*60)
        print(f"👤 Target: {self.config['hater_name']}")
        print(f"⚡ Speed: {self.config['speed']}/10")
        print(f"🆔 UID: {self.config['uid']}")
        print(f"📊 Max Actions: {self.config['max_actions']}")
        print("="*60)
        
        # Validate cookies first
        if not self.validate_cookies():
            print("❌ Cannot start automation. Please check your cookies.")
            return
        
        # Setup driver
        driver = self.setup_driver()
        if not driver:
            return
        
        try:
            # Add cookies and navigate
            if not self.add_cookies_to_driver(driver):
                print("❌ Failed to setup browser session")
                return
            
            total_actions = 0
            
            # Run enabled actions
            if self.config['actions']['like_posts']:
                total_actions += self.automate_likes(driver)
            
            if self.config['actions']['comment_posts']:
                total_actions += self.automate_comments(driver)
            
            print(f"\n🎉 AUTOMATION COMPLETED!")
            print(f"📈 Total Actions Performed: {total_actions}")
            
        except Exception as e:
            print(f"❌ Automation error: {e}")
        finally:
            driver.quit()

def interactive_setup():
    """Interactive configuration setup"""
    print("\n🛠️ AAHAN CONFIGURATION SETUP")
    print("-" * 40)
    
    config = {}
    
    # Basic info
    config['uid'] = input("Enter Facebook UID: ").strip() or "100000000000000"
    config['hater_name'] = input("Enter target name: ").strip() or "Target User"
    
    # Speed setting
    try:
        speed = int(input("Enter speed (1-10, 5=normal): ").strip() or "5")
        config['speed'] = max(1, min(10, speed))
    except:
        config['speed'] = 5
    
    # Max actions
    try:
        max_actions = int(input("Max actions per session (10-50): ").strip() or "10")
        config['max_actions'] = max(10, min(50, max_actions))
    except:
        config['max_actions'] = 10
    
    # Cookies input
    print("\n📋 Paste Facebook cookies (format: name=value):")
    print("Common cookies: c_user, xs, fr, datr")
    print("Press Enter twice when done:")
    
    cookies = []
    while True:
        cookie_input = input().strip()
        if not cookie_input:
            if len(cookies) >= 2:  # At least c_user and xs
                break
            else:
                print("Need at least 2 cookies (c_user and xs). Continue entering...")
                continue
        if '=' in cookie_input:
            name, value = cookie_input.split('=', 1)
            cookies.append({
                'name': name.strip(), 
                'value': value.strip(), 
                'domain': '.facebook.com'
            })
    
    config['cookies'] = cookies
    
    # Action preferences
    print("\n🎯 Select actions to automate:")
    config['actions'] = {
        'like_posts': input("Auto-like posts? (y/n): ").lower().startswith('y'),
        'comment_posts': input("Auto-comment posts? (y/n): ").lower().startswith('y'),
        'share_posts': input("Auto-share posts? (y/n): ").lower().startswith('n'),
        'add_friends': input("Auto-add friends? (y/n): ").lower().startswith('n')
    }
    
    # Save configuration
    with open('aahan_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("✅ Configuration saved to aahan_config.json")
    return config

def main_menu():
    """Main menu interface"""
    bot = AAHANFacebookBot()
    
    while True:
        print("\n" + "="*50)
        print("🤖 AAHAN FACEBOOK AUTOMATION")
        print("="*50)
        print("1. 🚀 Run Automation")
        print("2. ⚙️  Edit Configuration")
        print("3. 🔍 Validate Cookies")
        print("4. 📊 View Current Config")
        print("5. ❌ Exit")
        print("="*50)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice()
        
        if choice == '1':
            bot == '1':
            bot.run_automation()
       .run_automation()
        elif choice == '2':
 elif choice == '2':
            interactive_setup()
                       interactive_setup()
            bot = AAHANFacebookBot bot = AAHANFacebookBot()  #()  # Reload config
 Reload config
        elif        elif choice == '3 choice == '3':
            bot':
            bot.validate_c.validate_cookies()
        elif choice == '4':
            print("\ookies()
        elif choice == '4':
            print("\n📄n📄 Current Configuration:")
            Current Configuration:")
            print(json.dumps(bot.config, indent=2, ensure_ascii=False))
        elif choice == '5':
            print("👋 Thanks for using AAHAN Automation!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    print("""
    🚀 AAHAN FACEBOOK AUTOMATION TOOL
    Version 1.0 | Made with ❤️
    ⚠️  Use responsibly and comply with Facebook's ToS
    """)
    
    # Check if config exists, if not run setup
    if not os.path.exists('aahan_config.json'):
        print("📝 First-time setup required...")
        interactive_setup()
    
    print(json.dumps(bot.config, indent=2, ensure_ascii=False))
        elif choice == '5':
            print("👋 Thanks for using AAHAN Automation!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    print("""
    🚀 AAHAN FACEBOOK AUTOMATION TOOL
    Version 1.0 | Made with ❤️
    ⚠️  Use responsibly and comply with Facebook's ToS
    """)
    
    # Check if config exists, if not run setup
    if not os.path.exists('aahan_config.json'):
        print("📝 First-time setup required...")
        interactive_setup()
    
    main_menu()
