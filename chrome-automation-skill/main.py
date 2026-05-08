#!/usr/bin/env python3
"""
Chrome 自动化主脚本
用于 OpenClaw 和 Hermes 环境
"""

import sys
import json
import argparse
from browser_controller import BrowserController
from login_manager import LoginManager
from element_extractor import ElementExtractor


class ChromeAutomationSkill:
    """Chrome 自动化技能主类"""
    
    def __init__(self, headless=False, user_data_dir=None):
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.browser = None
        self.login_manager = None
        self.extractor = None
    
    def initialize(self):
        """初始化浏览器和组件"""
        self.browser = BrowserController(
            headless=self.headless,
            user_data_dir=self.user_data_dir
        )
        self.browser.start()
        self.login_manager = LoginManager(self.browser)
        self.extractor = ElementExtractor(self.browser)
        return self
    
    def execute(self, action, **params):
        """
        执行操作
        
        Args:
            action: 操作类型
            params: 操作参数
        """
        if action == 'navigate':
            url = params.get('url')
            return self.browser.navigate(url)
        
        elif action == 'extract':
            selectors = params.get('selectors', {})
            return self.extractor.extract_specific_data(selectors)
        
        elif action == 'extract_links':
            filter_pattern = params.get('filter')
            return self.extractor.extract_links(filter_pattern)
        
        elif action == 'extract_images':
            return self.extractor.extract_images()
        
        elif action == 'extract_tables':
            return self.extractor.extract_tables()
        
        elif action == 'extract_text':
            selector = params.get('selector')
            by = params.get('by', 'css')
            
            by_map = {
                'css': By.CSS_SELECTOR,
                'xpath': By.XPATH,
                'id': By.ID,
                'class': By.CLASS_NAME,
                'tag': By.TAG_NAME
            }
            
            return self.extractor.extract_text(selector, by_map.get(by, By.CSS_SELECTOR))
        
        elif action == 'login':
            login_type = params.get('type', 'password')
            
            if login_type == 'password':
                return self.login_manager.login_with_password(
                    login_url=params.get('url'),
                    username=params.get('username'),
                    password=params.get('password'),
                    username_selector=params.get('username_selector', '#username'),
                    password_selector=params.get('password_selector', '#password'),
                    submit_selector=params.get('submit_selector', '#submit'),
                    success_indicator=params.get('success_indicator')
                )
            elif login_type == 'cookies':
                return self.login_manager.login_with_cookies(
                    domain=params.get('domain'),
                    cookies_file=params.get('cookies_file')
                )
            elif login_type == 'auto':
                return self.login_manager.auto_login(
                    platform=params.get('platform'),
                    credentials={
                        'username': params.get('username'),
                        'password': params.get('password')
                    }
                )
        
        elif action == 'screenshot':
            filename = params.get('filename')
            return {'screenshot': self.browser.take_screenshot(filename)}
        
        elif action == 'get_page_info':
            return {
                'url': self.browser.get_current_url(),
                'title': self.browser.get_page_title()
            }
        
        elif action == 'scroll':
            position = params.get('position', 'bottom')
            if position == 'bottom':
                self.browser.scroll_to_bottom()
            elif position == 'top':
                self.browser.scroll_to_top()
            return {'success': True}
        
        elif action == 'wait':
            seconds = params.get('seconds', 3)
            import time
            time.sleep(seconds)
            return {'success': True}
        
        else:
            return {'error': f'不支持的操作: {action}'}
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.stop()


def main():
    """主函数 - 处理命令行调用"""
    parser = argparse.ArgumentParser(description='Chrome 自动化技能')
    parser.add_argument('--action', type=str, required=True, help='操作类型')
    parser.add_argument('--params', type=str, default='{}', help='参数 (JSON 格式)')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    parser.add_argument('--user-data-dir', type=str, help='用户数据目录')
    
    args = parser.parse_args()
    
    try:
        # 解析参数
        params = json.loads(args.params)
        
        # 创建并执行技能
        skill = ChromeAutomationSkill(
            headless=args.headless,
            user_data_dir=args.user_data_dir
        )
        skill.initialize()
        
        result = skill.execute(args.action, **params)
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        skill.close()
        
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == '__main__':
    main()