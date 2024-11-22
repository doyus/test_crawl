#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：spider_v9 
@File    ：aaa.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：5/9/2024 下午4:20 
'''
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：spider_v9 
@File    ：test_rule.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：5/9/2024 下午3:56 
'''
import re
from typing import List, Dict
from lxml import etree
from utils.tools import *
class DetailAction:
    """
    处理解析规则，对应v9的，正则，替换等规则
    """
    def __init__(self):

        self.json_object = None
    def execute(self, context, body:str,response,requests_info,base_dict,rules_keys):
        """
        context为规则对象，body为已经第一次处理完毕数据
        """
        if isinstance(body,int):
            self.text=str(body)
        elif '_Element' in str(type(body)) and '_ElementUnicodeResult' not in str(type(body)) :
            self.text = etree.tostring(body, encoding='unicode', method='html').replace('\xa0', '&nbsp;')
        else:
            self.text = body
        self.rules_keys=rules_keys
        self.json_object = context
        self.response = response
        self.base_dict=base_dict
        self.process_reg()
        #正则提取
        self.process_substr()
        #正输入租测试
        before_value = self.json_object.get("beforeValue")
        if before_value and self.text:
            #内容前加字符串
            self.text = before_value + self.text
        after_value = self.json_object.get("afterValue")
        if after_value and self.text:
            #内容后加字符串
            self.text += after_value
        #过滤全部属性
        self.process_filter_tags()
        self.process_filter_atts()
        self.process_filter_all_att()
        if self.json_object.get("sbcFlag"):
            #3全角转半角
            self.text = self.sbc2dbc(self.text)
        if self.json_object.get("plainFlag"):
            #转为纯文本
            self.text = PlainExtractor().process(self.text)
        if self.json_object.get("stripFlag"):
            #去除前后空格
            self.text = self.text.strip()
        if self.json_object.get("unicodeFlag"):
            #unicode处理
            self.text = self.unescape_java(self.text)
        #替换规则
        self.process_replace()
        if self.json_object['fieldName']=='SOURCE_URL':
            #补全url,使用requests_info,参数
            self.full_url(requests_info)
        return self.text
    def full_url(self,requestInfoes):
        start_url=self.text
        if self.base_dict['rule_data']['first_rules']['detailUrl']:
            if len(self.base_dict['rule_data']['first_rules']['detailUrl'].strip())>1:
                start_url=self.base_dict['rule_data']['first_rules']['detailUrl']
        req = {
            'source_url':self.text,
            'url': start_url
        }
        headers={}
        if requestInfoes:
            for infos in requestInfoes:
                if infos['requestType'] == 'HEADER':
                    headers[infos['name']] = infos['value'].strip()
                    req['headers'] = headers
                else:
                    if self.rules_keys=='list_rule':
                        post_type='detailPost'
                    # else:
                    #     post_type='detailPost'
                    if self.base_dict['rule_data']['first_rules'][post_type] == 1:
                        req['method'] = 'POST'
                        data = self.text
                        req['type'],req['data'] = format_str_to_dict(self.text)
                    else:
                        req['method'] = 'GET'
                        if '\\' in self.text:
                            self.text = self.text.replace('\\', '')
                        req['url']=self.response.urljoin(self.text)

        else:
            req['method'] = 'GET'
            if '\\' in self.text:
                self.text = self.text.replace('\\', '')
            req['url'] = self.response.urljoin(self.text)
            req['headers'] = headers
        if 'http' not in req['url']:
            if '\\' in self.text:
                self.text = self.text.replace('\\', '')
            req['url'] = self.response.urljoin(self.text)
        if 'method' not in req:
            req['method'] = 'GET'
        self.text=req
    # def urljoin(self,baseurl,url):
    #     """
    #     只拼接主url
    #     """
    #     base='https://www.baidu.com/aaaa/'
    #     url='/111/111'
    #     new_url='https://www.baidu.com/111/111'

    def process_substr(self):
        if 'response' in str(type(self.text)) :
            #为scrapy对象
            return
        _find=''
        start_index=0
        start_str = self.json_object.get("startStr").strip()
        containStart = self.json_object.get("containStart")
        if start_str:
            start_index=self.text.find(start_str)
            if containStart==1:
                start_index-=len(start_str)
        end_str = self.json_object.get("endStr").strip()
        end_index=-1
        containEnd = self.json_object.get("containEnd")
        if end_str:
            end_index=self.text.find(end_str)
            if containEnd==1:
                end_index+=len(end_str)
        if end_index==-1:
            self.text=self.text[start_index:]
        else:
            self.text=self.text[start_index:end_index]

    def process_reg(self):
        reg_value = self.json_object.get("regValue2")
        reg_value2_result = self.json_object.get("regValue2Result")
        if reg_value:
            matcher = re.compile(reg_value, re.IGNORECASE | re.DOTALL)
            match = matcher.search(self.text)
            if not match:
                self.text = ""
            elif reg_value2_result:
                self.text = reg_value2_result
                for i in range(match.re.groups + 1):
                    self.text = self.text.replace("${_" + str(i) + "}", match.group(i))
            else:
                self.text = match.group(0)

    def process_filter_tags(self):
        filter_tags = self.json_object.get("filterTags")
        if filter_tags:
            tags = filter_tags.split(',')
            for tag in tags:
                if tag.lower() == 'b':
                    self.text = re.sub(r"<[/]?b>", "", self.text, flags=re.IGNORECASE)
                else:
                    self.text = re.sub(r"<[/]?" + re.escape(tag) + r".*?[/]?>", "", self.text, flags=re.IGNORECASE)

    def process_filter_atts(self):
        filter_atts = self.json_object.get("filterAtts")
        if filter_atts:
            atts = filter_atts.split(',')
            for att in atts:
                self.text = re.sub(r"\s*" + re.escape(att) + r"\s*=\s*[\"'].+?[\"']", "", self.text, flags=re.IGNORECASE)

    def process_filter_all_att(self):
        if self.json_object.get("filterFlag"):
            buffer = []
            matcher = re.compile(r"<[a-z]+\s+(.*?)\s*/?>", flags=re.IGNORECASE | re.DOTALL)
            last_end = 0
            for match in matcher.finditer(self.text):
                buffer.append(self.text[last_end:match.start()])
                buffer.append(match.group().replace(match.group(1), ""))
                last_end = match.end()
            buffer.append(self.text[last_end:])
            self.text = "".join(buffer)

    def process_replace(self):
        replaces = self.json_object.get("replaces",[])
        for i in range(len(replaces)):
            replace_json_object = replaces[i]
            search_value = replace_json_object.get("searchValue")
            replace_value = replace_json_object.get("replaceValue")
            if '$' in replace_value:
                search_list=re.findall(search_value,self.text)
                if search_list:
                    search_list=search_list[0]
                    _replace=re.findall('(\$\d+)', replace_value)
                    for _ in _replace:
                        replace_value=replace_value.replace(_,search_list[int(_.replace('$',''))-1])
            if replace_value == "[EMPTY]":
                replace_value = ""
            search_flag = replace_json_object.get("searchFlag")
            replace_flag = replace_json_object.get("replaceFlag")
            if search_flag:
                if replace_flag:
                    self.text = re.sub(search_value, replace_value, self.text, flags=re.IGNORECASE | re.DOTALL)
                else:
                    self.text = re.sub(search_value, replace_value, self.text, count=1, flags=re.IGNORECASE | re.DOTALL)
            elif replace_flag:
                self.text = self.text.replace(search_value, replace_value)
            else:
                self.text = self.text.replace(search_value, replace_value, 1)

    @staticmethod
    def sbc2dbc(text):
        return text.translate(str.maketrans({
            '！': '!', '＠': '@', '＃': '#', '＄': '$', '％': '%', '＆': '&', '＊': '*', '（': '(',
            '）': ')', '－': '-', '＝': '=', '＋': '+', '＜': '<', '＞': '>', '｛': '{', '｝': '}',
            '［': '[', '］': ']', '｜': '|', '＼': '\\', '＾': '^', '～': '~', '∶': ':', '；': ';',
            '＂': '"', '｀': '`', '＜': '<', '＞': '>', '＿': '_', '～': '~', '？': '?', '！': '!',
            '＠': '@', '＃': '#', '＄': '$', '％': '%', '＆': '&', '＊': '*', '（': '(',
            '）': ')', '－': '-', '＝': '=', '＋': '+', '＜': '<', '＞': '>', '｛': '{', '｝': '}',
            '［': '[', '］': ']', '｜': '|', '＼': '\\', '＾': '^', '～': '~', '∶': ':', '；': ';',
            '＂': '"', '｀': '`'
        }))

    @staticmethod
    def unescape_java(text):
        return text.encode('utf-8').decode('unicode_escape')

class NodeVariable:
    def __init__(self, value):
        self.value = value

class PlainExtractor:
    def process(self, text):
        html=''.join(etree.HTML(text).xpath('.//text()'))
        return html.strip()

class IJsonObject:
    def __init__(self, data: Dict):
        self.data = data

    def get(self, key):
        return self.data.get(key, "")

    def get(self, key):
        return bool(self.data.get(key, False))

    def get(self, key):
        return self.data.get(key, [])

class IJsonArray:
    def __init__(self, data: List):
        self.data = data

    def size(self):
        return len(self.data)

    def get_json_object(self, index):
        return IJsonObject(self.data[index])
if __name__ == "__main__":
    demo=DetailAction()
    rule={'containEnd': 0, 'endStr': '', 'fieldName': 'SOURCE_URL', 'beforeValue': 'http://www.fsigc.com:6116', 'containStart': 0, 'unicodeFlag': 0, 'afterValue': '', 'xpath': '//*[@id="form1"]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/a/@href', 'startStr': '', 'visitFlag': 0, 'regValue2Result': '', 'id': 2135236, 'filterTags': '', 'plainFlag': 0, 'spiderValueType': 'XPATH', 'attFlag': 0, 'pageReg': None, 'stripFlag': 0, 'filterFlag': 0, 'replaces': [], 'startToBorder': 0, 'regValue2': '', 'endToBorder': 0, 'filterAtts': '', 'attPatterns': [], 'regValue': '', 'spiderPosType': 'LIST', 'sbcFlag': 0, 'constantValue': ''}
    text=''
    print(demo.execute(rule,text))

