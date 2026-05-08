"""
浏览器控制器 - 基础浏览器操作
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import json


class BrowserController:
    """Chrome 浏览器控制器"""
    
    def __init__(self, headless=False, user_data_dir=None, disable_automation=True):
        """
        初始化浏览器控制器
        
        Args:
            headless: 是否使用无头模式
            user_data_dir: 用户数据目录
            disable_automation: 是否禁用自动化特征检测
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.user_data_dir = user_data_dir
        self.disable_automation = disable_automation
        
    def start(self):
        """启动浏览器"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1920,1080')
        else:
            chrome_options.add_argument('--start-maximized')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 使用用户数据目录
        if self.user_data_dir:
            chrome_options.add_argument(f'--user-data-dir={self.user_data_dir}')
        
        # 设置 User-Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 启动驱动
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 禁用自动化特征
        if self.disable_automation:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        return self
    
    def stop(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def navigate(self, url, wait_load=True):
        """导航到指定 URL"""
        try:
            self.driver.get(url)
            if wait_load:
                self.wait_for_page_load()
            return {'success': True, 'url': url, 'title': self.driver.title}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def wait_for_page_load(self, timeout=30):
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except:
            return False
    
    def find_element(self, by, value, timeout=10):
        """查找单个元素"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def find_elements(self, by, value, timeout=10):
        """查找多个元素"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_all_elements_located((by, value)))
    
    def get_current_url(self):
        """获取当前 URL"""
        return self.driver.current_url
    
    def get_page_title(self):
        """获取页面标题"""
        return self.driver.title
    
    def get_page_source(self):
        """获取页面源码"""
        return self.driver.page_source
    
    def execute_script(self, script, *args):
        """执行 JavaScript"""
        return self.driver.execute_script(script, *args)
    
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.execute_script("window.scrollTo(0, 0);")
    
    def take_screenshot(self, filename=None):
        """截图"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        self.driver.save_screenshot(filename)
        return filename
    
    def get_cookies(self):
        """获取所有 cookies"""
        return self.driver.get_cookies()
    
    def add_cookie(self, cookie):
        """添加 cookie"""
        self.driver.add_cookie(cookie)
    
    def delete_all_cookies(self):
        """删除所有 cookies"""
        self.driver.delete_all_cookies()
    
    def save_cookies(self, filepath):
        """保存 cookies 到文件"""
        cookies = self.get_cookies()
        with open(filepath, 'w') as f:
            json.dump(cookies, f)
        return filepath
    
    def load_cookies(self, filepath, domain=None):
        """从文件加载 cookies"""
        with open(filepath, 'r') as f:
            cookies = json.load(f)
        
        # 先访问域名
        if domain:
            self.driver.get(domain)
        
        for cookie in cookies:
            if 'expiry' in cookie:
                cookie['expiry'] = int(cookie['expiry'])
            try:
                self.driver.add_cookie(cookie)
            except:
                pass
        
        if domain:
            self.driver.refresh()
        
        return True
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """等待元素出现"""
        try:
            return self.wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            return None
    
    def element_exists(self, selector, by=By.CSS_SELECTOR):
        """检查元素是否存在"""
        try:
            self.driver.find_element(by, selector)
            return True
        except:
            return False