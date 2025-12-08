@staticmethod
def page_count(self, doc):
    """
    基于你提供的HTML结构的翻页规则
    """
    # 规则1：从<div class="pages">中获取分页
    try:
        pages_div = doc.xpath('//div[@class="pages"]')
        if pages_div:
            # 获取所有页码链接
            page_links = pages_div[0].xpath('.//a[contains(@class, "page")]')
            if page_links:
                page_numbers = []
                for link in page_links:
                    text = ''.join(link.xpath('.//text()')).strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                
                if page_numbers:
                    return max(page_numbers)
    except:
        pass
    
    # 规则2：从pagebar类中获取
    try:
        pagebar = doc.xpath('//div[@class="pagebar"]')
        if pagebar:
            links = pagebar[0].xpath('.//a[not(contains(text(), "下一页"))]')
            last_page = 1
            for link in links:
                text = ''.join(link.xpath('.//text()')).strip()
                if text.isdigit():
                    page_num = int(text)
                    if page_num > last_page:
                        last_page = page_num
            return last_page if last_page > 1 else 9999
    except:
        pass
    
    # 规则3：通用方法，获取所有可能是页码的数字
    try:
        all_links = doc.xpath('//a[contains(@href, "/category/")]')
        page_numbers = []
        for link in all_links:
            href = ''.join(link.xpath('@href')).strip()
            text = ''.join(link.xpath('.//text()')).strip()
            
            # 从href中提取页码
            import re
            match = re.search(r'/category/[^/]+/(\d+)/', href)
            if match:
                page_numbers.append(int(match.group(1)))
            
            # 从文本中提取页码
            if text.isdigit():
                page_numbers.append(int(text))
        
        if page_numbers:
            return max(page_numbers)
    except:
        pass
    
    # 规则4：检查是否有下一页按钮
    try:
        # 查找"下一页"或next相关的元素
        next_elements = doc.xpath('//a[contains(text(), "下一页") or contains(@class, "next")]')
        if next_elements:
            return 9999  # 有下一页，但不知道总数，返回大数
    except:
        pass
    
    # 默认返回9999，让采集器无限翻页
    return 9999