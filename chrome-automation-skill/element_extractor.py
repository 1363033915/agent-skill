"""
元素提取器 - 提取网页元素和数据
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


class ElementExtractor:
    """网页元素提取器"""
    
    def __init__(self, browser_controller):
        self.browser = browser_controller
    
    def extract_by_selector(self, selector, by=By.CSS_SELECTOR, multiple=False):
        """通过选择器提取元素"""
        try:
            if multiple:
                elements = self.browser.find_elements(by, selector)
                return [self._get_element_info(elem) for elem in elements]
            else:
                element = self.browser.find_element(by, selector)
                return self._get_element_info(element)
        except:
            return None if not multiple else []
    
    def _get_element_info(self, element):
        """获取元素详细信息"""
        return {
            'text': element.text,
            'tag': element.tag_name,
            'html': element.get_attribute('outerHTML'),
            'inner_html': element.get_attribute('innerHTML'),
            'attributes': self._get_attributes(element)
        }
    
    def _get_attributes(self, element):
        """获取元素属性"""
        attributes = {}
        attrs = ['id', 'class', 'name', 'href', 'src', 'alt', 'title', 'value', 'type']
        for attr in attrs:
            value = element.get_attribute(attr)
            if value:
                attributes[attr] = value
        return attributes
    
    def extract_text(self, selector, by=By.CSS_SELECTOR):
        """提取文本内容"""
        element = self.browser.find_element(by, selector)
        return element.text if element else None
    
    def extract_links(self, filter_pattern=None):
        """提取所有链接"""
        links = self.browser.find_elements(By.TAG_NAME, "a")
        result = []
        
        for link in links:
            href = link.get_attribute('href')
            text = link.text.strip()
            
            if href and (not filter_pattern or re.search(filter_pattern, href)):
                result.append({
                    'url': href,
                    'text': text,
                    'title': link.get_attribute('title')
                })
        
        return result
    
    def extract_images(self):
        """提取所有图片"""
        images = self.browser.find_elements(By.TAG_NAME, "img")
        result = []
        
        for img in images:
            src = img.get_attribute('src')
            alt = img.get_attribute('alt')
            if src:
                result.append({
                    'src': src,
                    'alt': alt,
                    'title': img.get_attribute('title')
                })
        
        return result
    
    def extract_metadata(self):
        """提取页面元数据"""
        metadata = {}
        
        # Title
        try:
            metadata['title'] = self.browser.get_page_title()
        except:
            metadata['title'] = ''
        
        # Meta tags
        meta_tags = self.browser.find_elements(By.TAG_NAME, "meta")
        for tag in meta_tags:
            name = tag.get_attribute('name') or tag.get_attribute('property')
            content = tag.get_attribute('content')
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def extract_tables(self):
        """提取表格数据"""
        tables = self.browser.find_elements(By.TAG_NAME, "table")
        result = []
        
        for table in tables:
            table_data = []
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                row_data = []
                cells = row.find_elements(By.TAG_NAME, "td")
                headers = row.find_elements(By.TAG_NAME, "th")
                
                for cell in cells + headers:
                    row_data.append(cell.text.strip())
                
                if row_data:
                    table_data.append(row_data)
            
            result.append(table_data)
        
        return result
    
    def extract_list_items(self, list_selector, item_selector="li"):
        """提取列表项"""
        container = self.browser.find_element(By.CSS_SELECTOR, list_selector)
        items = container.find_elements(By.CSS_SELECTOR, item_selector)
        
        return [item.text.strip() for item in items if item.text.strip()]
    
    def extract_form_data(self, form_selector):
        """提取表单数据"""
        form = self.browser.find_element(By.CSS_SELECTOR, form_selector)
        inputs = form.find_elements(By.TAG_NAME, "input")
        
        form_data = {}
        for inp in inputs:
            name = inp.get_attribute('name')
            value = inp.get_attribute('value')
            if name:
                form_data[name] = value
        
        return form_data
    
    def extract_by_regex(self, pattern, text=None):
        """使用正则表达式提取"""
        if not text:
            text = self.browser.get_page_source()
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches
    
    def extract_json_ld(self):
        """提取 JSON-LD 结构化数据"""
        scripts = self.browser.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
        import json
        
        data = []
        for script in scripts:
            try:
                content = script.get_attribute('innerHTML')
                parsed = json.loads(content)
                data.append(parsed)
            except:
                pass
        
        return data
    
    def extract_specific_data(self, selectors):
        """
        根据配置的选择器提取数据
        
        Args:
            selectors: 选择器配置字典，如 {'title': 'h1', 'content': '.article-body'}
        
        Returns:
            提取的数据字典
        """
        result = {}
        
        for key, selector in selectors.items():
            try:
                if isinstance(selector, dict):
                    # 复杂选择器配置
                    by = selector.get('by', By.CSS_SELECTOR)
                    value = selector.get('selector')
                    attribute = selector.get('attribute')
                    multiple = selector.get('multiple', False)
                    
                    if multiple:
                        elements = self.browser.find_elements(by, value)
                        if attribute:
                            result[key] = [elem.get_attribute(attribute) for elem in elements]
                        else:
                            result[key] = [elem.text for elem in elements]
                    else:
                        element = self.browser.find_element(by, value)
                        if attribute:
                            result[key] = element.get_attribute(attribute)
                        else:
                            result[key] = element.text
                else:
                    # 简单 CSS 选择器
                    element = self.browser.find_element(By.CSS_SELECTOR, selector)
                    result[key] = element.text
            except Exception as e:
                result[key] = None
        
        return result