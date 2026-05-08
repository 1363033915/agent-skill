"""
登录管理器 - 处理各种登录场景
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json


class LoginManager:
    """登录管理器"""
    
    def __init__(self, browser_controller, cookies_dir="saved_cookies"):
        """
        初始化登录管理器
        
        Args:
            browser_controller: BrowserController 实例
            cookies_dir: cookies 保存目录
        """
        self.browser = browser_controller
        self.cookies_dir = cookies_dir
        
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
    
    def login_with_password(self, login_url, username, password, 
                           username_selector="#username",
                           password_selector="#password",
                           submit_selector="#submit",
                           success_indicator=None,
                           wait_after_submit=3):
        """
        使用账号密码登录
        
        Args:
            login_url: 登录页面 URL
            username: 用户名
            password: 密码
            username_selector: 用户名输入框选择器
            password_selector: 密码输入框选择器
            submit_selector: 提交按钮选择器
            success_indicator: 登录成功标志元素
            wait_after_submit: 提交后等待时间
        """
        try:
            # 打开登录页
            self.browser.navigate(login_url)
            time.sleep(2)
            
            # 输入用户名
            username_input = self.browser.find_element(By.CSS_SELECTOR, username_selector)
            username_input.clear()
            username_input.send_keys(username)
            
            # 输入密码
            password_input = self.browser.find_element(By.CSS_SELECTOR, password_selector)
            password_input.clear()
            password_input.send_keys(password)
            
            # 处理验证码
            if self.check_captcha():
                self.wait_for_manual("请手动完成验证码...", timeout=60)
            
            # 点击登录
            submit_btn = self.browser.find_element(By.CSS_SELECTOR, submit_selector)
            submit_btn.click()
            
            time.sleep(wait_after_submit)
            
            # 验证登录结果
            if success_indicator:
                if self.browser.element_exists(success_indicator):
                    # 保存 cookies
                    self.save_cookies_for_url(login_url)
                    return {'success': True, 'message': '登录成功'}
                else:
                    return {'success': False, 'message': '登录失败：未找到成功标志'}
            else:
                # 检查 URL 是否变化
                if self.browser.get_current_url() != login_url:
                    self.save_cookies_for_url(login_url)
                    return {'success': True, 'message': f'登录成功，重定向到 {self.browser.get_current_url()}'}
                else:
                    return {'success': False, 'message': '登录失败：URL 未变化'}
                    
        except Exception as e:
            return {'success': False, 'message': f'登录出错: {str(e)}'}
    
    def login_with_cookies(self, domain, cookies_file=None):
        """使用保存的 cookies 登录"""
        try:
            if not cookies_file:
                cookies_file = self.get_latest_cookies_file(domain)
            
            if not cookies_file or not os.path.exists(cookies_file):
                return {'success': False, 'message': '未找到 cookies 文件'}
            
            self.browser.load_cookies(cookies_file, domain)
            return {'success': True, 'message': 'Cookies 加载成功'}
            
        except Exception as e:
            return {'success': False, 'message': f'加载 cookies 失败: {str(e)}'}
    
    def save_cookies_for_url(self, url):
        """为指定 URL 保存 cookies"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        filename = f"{self.cookies_dir}/{domain}_cookies.json"
        self.browser.save_cookies(filename)
        return filename
    
    def get_latest_cookies_file(self, domain):
        """获取最新的 cookies 文件"""
        files = [f for f in os.listdir(self.cookies_dir) if domain in f and f.endswith('.json')]
        if not files:
            return None
        files = [os.path.join(self.cookies_dir, f) for f in files]
        return max(files, key=os.path.getctime)
    
    def check_captcha(self):
        """检查是否存在验证码"""
        captcha_keywords = ['captcha', '验证码', 'CAPTCHA', 'recaptcha', 'verification']
        page_source = self.browser.get_page_source().lower()
        for keyword in captcha_keywords:
            if keyword in page_source:
                return True
        return False
    
    def wait_for_manual(self, message, timeout=60):
        """等待手动操作"""
        print(f"\n⚠️ {message}")
        print(f"请在浏览器中完成操作，{timeout} 秒后继续...\n")
        
        for i in range(timeout, 0, -1):
            print(f"等待中... {i} 秒", end='\r')
            time.sleep(1)
        print("\n继续执行...")
    
    # 平台特定登录
    def login_github(self, username, password, two_factor=None):
        """GitHub 登录"""
        return self.login_with_password(
            login_url="https://github.com/login",
            username=username,
            password=password,
            username_selector="#login_field",
            password_selector="#password",
            submit_selector="input[name='commit']",
            success_indicator=".dashboard-sidebar"
        )
    
    def login_baidu(self, username, password):
        """百度登录"""
        return self.login_with_password(
            login_url="https://passport.baidu.com/v2/?login",
            username=username,
            password=password,
            username_selector="#TANGRAM__PSP_11__userName",
            password_selector="#TANGRAM__PSP_11__password",
            submit_selector="#TANGRAM__PSP_11__submit",
            success_indicator=".user-name"
        )
    
    def login_taobao(self, username, password):
        """淘宝登录"""
        return self.login_with_password(
            login_url="https://login.taobao.com",
            username=username,
            password=password,
            username_selector="#fm-login-id",
            password_selector="#fm-login-password",
            submit_selector=".password-login",
            success_indicator=".site-nav-user"
        )
    
    def auto_login(self, platform, credentials):
        """自动登录指定平台"""
        login_methods = {
            'github': self.login_github,
            'baidu': self.login_baidu,
            'taobao': self.login_taobao
        }
        
        if platform.lower() in login_methods:
            return login_methods[platform.lower()](
                credentials.get('username', ''),
                credentials.get('password', '')
            )
        else:
            return {'success': False, 'message': f'不支持的平台: {platform}'}