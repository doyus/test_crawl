#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：devtool.py
@IDE     ：PyCharm 
@INFO     ： 工具函数
@Author  ：BGSPIDER
@Date    ：29/12/2023 下午2:01 
'''
import requests,re,jsonpath,copy,socket,hashlib
import logging
from lxml import etree
from urllib.parse import urlparse
import datetime,time,json
from devtool.util import *
from uuid import uuid4
from dateutil import parser as date_string_parser
from config import *
import requests, scrapy
from scrapy.http import HtmlResponse
from utils.user_agent import *
area_dict ={"北京":1,"上海":2,"天津":3,"重庆":4,"河北":5,"山西":6,"内蒙":7,"内蒙古":7,"辽宁":8,"吉林":9,
"吉林":9,"黑龙江":10,"黑龙江省":10,"江苏":11,"浙江":12,"安徽":13,"福建":14,"江西":15,"山东":16,"河南":17,
"湖北":18,"湖南":19,"广东":20,"广西":21,"海南":22,"贵州":23,"云南":24,"西藏":25,"陕西":26,"四川":27,
"甘肃":28,"青海":29,"新疆":30,"宁夏":31,"香港":32,"澳门":33,"台湾":34,"跨省":36,
"亚洲":43,"欧洲":44,"非洲":45,"北美洲":46,"南美洲":47,"大洋洲":48,"中美洲":49,"加勒比":50,
"北京市":1,"上海市":2,"天津市":3,"重庆市":4,"河北省":5,"山西省":6,"辽宁省":8,"吉林省":9,
"黑龙江省":10,"江苏省":11,"浙江省":12,"安徽省":13,"福建省":14,"江西省":15,"山东省":16,
"河南省":17,"湖北省":18,"湖南省":19,"广东省":20,"海南省":22,"贵州省":23,"云南省":24,
"陕西省":26,"四川省":27,"甘肃省":28,"青海省":29,"香港特区":32,"香港特别行政区":32,"澳门特区":33,"台湾省":34,
"广西自治区":21,"新疆自治区":30,"宁夏自治区":31,"内蒙古自治区":7,"西藏自治区":25,"广西壮族自治区":21,"新疆维吾尔自治区":30,"宁夏回族自治区":31,"内蒙古自治区":7}

cate_dict = {
    "1":"交通运输",
    "2":"网络通讯计算机",
    "3":"市政房地产建筑",
    "4":"水利桥梁",
    "5":"机械电子电器",
    "6":"环保",
    "8":"医疗卫生",
    "9":"科技文教旅游",
    "10":"冶金矿产原材料",
    "11":"出版印刷",
    "12":"轻工纺织食品",
    "13":"农林牧渔",
    "14":"商业服务",
    "15":"其它",
    "16":"园林绿化",
    "17":"能源",
    "18":"化工",
    "":"未知"
}

cate_inv = {
    "园林绿化": "16",
    "商业服务": "14",
    "能源": "17",
    "冶金矿产原材料": "10",
    "农林牧渔": "13",
    "机械电子电器": "5",
    "医疗卫生": "8",
    "科技文教旅游": "9",
    "其它": "15",
    "轻工纺织食品": "12",
    "环保": "6",
    "市政房地产建筑": "3",
    "出版印刷": "11",
    "网络通讯计算机": "2",
    "交通运输": "1",
    "未知": "",
    "化工": "18",
    "水利桥梁": "4",
    "房屋建筑": "3",
    "市政": "3",
    "信息电子": "2",
    "广电通信": "2",
    "科教文卫": "9",
    "石油石化": "17",
    "能源电力": "17",
    "化学工业": "18",
    "水运": "1",
    "铁路": "1",
    "公路": "1",
    "民航": "1",
    "航空航天": "1",
    "港口航道": "1",
    "机械设备": "5",
    "保险金融": "14",
    "水利水电": "17",
    "矿产冶金": "10",
    "生态环保": "6",
    "生物医药": "8",
    "其他": "15",
    "纺织轻工": "12"
}

def trade(categorys):
    trade = ""
    category_list = categorys.split(",")
    for category_id in category_list:
        if category_id != "":
            category = cate_dict[category_id]
            if trade:
                trade += ',' + category
            else:
                trade = category
    return trade

def trade_inv(categorys):
    trade = ""
    category_list = categorys.split(",")
    for category_id in category_list:
        if category_id == "能源电力":
            category_id = "能源"
        if category_id != "":
            if category_id in cate_inv:
                category = cate_inv[category_id]
                if trade:
                    trade += ','+category
                else:
                    trade=category
            else:
                category = ""
    return trade
def identify_industry(title, content):
    keyword_map = {
        "1": ["交通", "运输", "物流", "货运", "航空", "航海", "铁路", "公路", "城市交通","汽车","航运"],
        "2": ["网络", "通讯", "计算机", "信息传输", "互联网", "数字", "IT", "电子信息", "软件", "硬件", "通信"],
        "3": ["市政", "房地产", "建筑", "城市规划", "工程", "基础设施", "房屋", "建筑材料"],
        "4": ["水利", "桥梁", "水电", "河流", "水坝", "水务", "水利工程","发电","光热","国网","电力"],
        "5": ["机械", "电子", "电器", "制造", "自动化", "仪器仪表", "设备", "装备"],
        "6": ["环保", "生态", "绿色", "节能", "可再生能源", "环境治理", "污染防治"],
        "8": ["医疗", "卫生", "健康", "医药", "医院", "药品", "医疗器械"],
        "9": ["科技", "文教", "旅游", "科学", "研究", "教育", "培训", "文化", "休闲", "旅行", "景区"],
        "10": ["冶金", "矿产", "原材料", "采矿", "金属", "矿业", "资源"],
        "11": ["出版", "印刷", "编辑", "传媒", "图书", "杂志", "报纸"],
        "12": ["轻工", "纺织", "食品", "日用品", "服装", "鞋帽", "家用电器", "食品饮料"],
        "13": ["农林", "牧渔", "种植", "养殖", "农产品", "林业", "渔业"],
        "14": ["商业", "服务", "贸易", "零售", "批发", "金融", "保险", "咨询", "广告"],
        "16": ["园林", "绿化", "园艺", "景观", "花卉", "绿地"],
        "17": ["能源", "电力", "煤炭", "石油", "天然气", "新能源",'煤矿', '煤气'],
        "18": ["化工", "化学", "材料", "涂料", "塑料", "橡胶"]
    }
    for industry_id, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in title or keyword in content:
                return industry_id,cate_dict[industry_id]
    return '15','其它'
def get_area_local(str):
    str = str.replace('晋能控股', '山西省').replace('北京时间', '')
    for area in area_dict.keys():
        if area in str:
            return area
class TimeCheckError(Exception):

    def __init__(self, *args):

        super(TimeCheckError, self).__init__(*args)
def parse_re_list(rule: str, response: list):
    """
    解析re规则
    """
    _value = []
    for _ in response:
        x = re.finditer(rule.strip(), _,re.S)
        for _x in x:
            _value.append(_x.group())
    return _value
from urllib.parse import quote, unquote
def form_data_loop(data,page):
    '''
    翻页循环data
    '''
    try:
        reqs = []
        old_data = re.findall('(\${i\.toInt\(\).*?})', data)[0]
        eval_str = old_data.replace('${i.toInt()', '{' + str(page))
        start_url = eval(f"f'{eval_str}'")
        datas = data.replace(old_data, start_url)
        return datas
    except Exception as e:
        return data

def format_str_to_dict(str_t):
    """
    将一行data转为data
    :param str_t:
    :return:
    """
    try:
        new_dict = {}
        if '&' in str_t:
            str_t=unquote(str_t)
            _ = str_t.split('&')
            for _x in _:
                new_dict[_x.split('=')[0]] = _x.split('=')[1]
            return 'data',new_dict
        elif '=' in str_t:
            _x=unquote(str_t)
            new_dict[_x.split('=')[0]] = _x.split('=')[1]
            return 'data',new_dict

        try:
            new_dict=json.loads(str_t)
            return 'json',new_dict
        except Exception as e:
            return 'error',str_t
    except Exception as e:
        return 'data',str_t
def get_random(spider=None):
    for x in range(3):
        try:
            headers = {
                'token': 'aab5385fbb7a419783b1cddbd6443e26'
            }
            url = 'http://39.105.227.135:3001/random'
            proxies = requests.get(url, headers=headers).json()
            if proxies:
                return proxies
            else:
                continue
        except Exception as e:
            print(e)
    return {}
def format_json(detail_json, _len):
    """
    重新格式化整体数据样式,列表页包装
    """
    len_number = []
    for num in range(_len):
        _dict = {}
        for x in range(len(detail_json)):
            if 'spiderValue' in detail_json[x]:
                if len(detail_json[x]['spiderValue'])==1:
                    _dict[detail_json[x]['fieldName']] = detail_json[x]['spiderValue'][0]
                else:
                    _dict[detail_json[x]['fieldName']] = detail_json[x]['spiderValue'][num]
            if 'CONSTANT' in detail_json[x]:
                _dict[detail_json[x]['fieldName']] = detail_json[x]['CONSTANT']
        len_number.append(_dict)
    return len_number

def parse_xpath_json_list(rule: str, response,_rules):
    """
    解析xpath规则和json
    """
    try:
        if rule=='/':
            return [response.text]
        if get_response_type(response) == 'text':
            if rule=='/':
                _value=response.text
            else:
                # bs_brokenhtml
                completed_html=bs_brokenhtml(response.text)
                if rule[0]!='/':
                    rule='/'+rule
                if '/dl/' in rule:
                    completed_html_dl=completed_html.replace('<dl>','<dl_handdddd>').replace('</dl>','<dl_handdddd>')
                    rule_dl=rule.replace('/dl/','/dl_handdddd/')
                    _value =etree.HTML(completed_html_dl).xpath(rule_dl)
                    if not _value:
                        _value = etree.HTML(completed_html).xpath(rule)
                else:
                    _value =etree.HTML(completed_html).xpath(rule)
                if not _value and 'table/tbody' in rule:
                    rule_table=rule.replace('table/tbody','table')
                    _value=etree.HTML(completed_html).xpath(rule_table)
        else:
            xml_tree=json_to_xml(response.json())
            titles = xml_tree.findall(rule
                                      )
            _value=[]
            # if not titles:
            #     rule=rule.replace('//','/').replace('/','//')
            #     titles = xml_tree.findall(rule)
            for title in titles:
                _value.append(ET.tostring(title, encoding='unicode'))
            # rule = rule.replace('//', '$..')
            # _value = jsonpath.jsonpath(response.json(), rule)
        return _value
    except Exception as e:
        _value = []
    return _value
def html_to_str(htmls:str):
    """
    html转为纯文本
    """
    _tree=etree.HTML(str(htmls))
    _str=''.join(_tree.xpath('//text()'))
    return _str

def get_domain(url:str):
    """
    获取url的地址
    """
    result = urlparse(url)
    return result.netloc

def check_time(string, time_format="%Y-%m-%d %H:%M:%S"):
    if not string:
        return ''
    if string.strip()=='ABC':
        string=str(datetime.datetime.now())
    if isinstance(string, (int, float)):
        string = str(int(string))
    if not isinstance(string, str):
        raise TimeCheckError(f"时间格式化失败 {str(string)}")
    if string.isdigit():
        if len(string) == 13:
            return time.strftime(time_format, time.localtime(int(string)/1000))
        elif len(string) == 10:
            return time.strftime(time_format, time.localtime(int(string)))
        else:
            raise TimeCheckError(f"时间格式化失败 {str(string)}")
    string = string.strip()
    if len(string.split('-')[0])==2:
        string='20'+string
    if '年' in string and '月' in string and '日' in string:
        string = string.split("日")[0]
        if "年" in time_format or '月' in time_format or '日' in time_format:
            t_format = time_format
        else:
            t_format = "%Y年%m月%d"
        try:
            d = datetime.datetime.strptime(string, t_format)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败 {string} -- {str(e)}")
    elif '年' in string and '月' in string:
        string = string.split(" ")[0]
        if "年" in time_format or '月' in time_format:
            t_format = time_format
        else:
            t_format = "%Y年%m月%d"
        try:
            d = datetime.datetime.strptime(string, t_format)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败 {string} -- {str(e)}")
    else:
        try:
            d = date_string_parser.parse(string)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败 {string} {str(e)}")
    n_year_later = datetime.datetime.now().replace(year=datetime.datetime.now().year + 1)
    if d.tzinfo:
        d=d.replace(tzinfo=None)
    if d > n_year_later:
        raise TimeCheckError(f"格式化后时间大于一年后时间 {str(d)}")
    return d.strftime(time_format)

def get_response_type(response):
    """
    判断返回体是不是Json
    """
    try:
        _=response.json()
        return 'json'
    except Exception as e:
        return 'text'
import xml.etree.ElementTree as ET
def json_to_xml(json_data):
    root = ET.Element("root")  # 根节点

    def _to_xml(parent, data):
        if isinstance(data, dict):  # 字典处理
            for key, value in data.items():
                element = ET.SubElement(parent, key)
                _to_xml(element, value)
        elif isinstance(data, list):
            # 列表处理
            for item in data:
                array_element = ET.SubElement(parent, 'array')
                _to_xml(array_element, item)
        else:
            parent.text = str(data)

    _to_xml(root, json_data)
    return ET.ElementTree(root)
def parse_and_validate_date(content, days=30):
    limit_date_ago = datetime.datetime.now() - datetime.timedelta(days=days)
    patterns = [
        (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M:%S'),
        (r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2})', '%Y-%m-%d %H:%M'),
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'(\d{4})/(\d{1,2})/(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})', '%Y/%m/%d %H:%M:%S'),
        (r'(\d{4})/(\d{1,2})/(\d{1,2}) (\d{1,2}):(\d{1,2})', '%Y/%m/%d %H:%M'),
        (r'(\d{4})/(\d{1,2})/(\d{1,2})', '%Y/%m/%d'),
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})', '%Y.%m.%d %H:%M:%S'),
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2}) (\d{1,2}):(\d{1,2})', '%Y.%m.%d %H:%M'),
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', '%Y.%m.%d'),
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
        (r'(\d{2})年(\d{1,2})月(\d{1,2})日', '%y年%m月%d日'),
        (r'(\d{1,2})月(\d{1,2})日', '%m月%d日'),
        (r'(\d{1,2})-(\d{1,2})-(\d{2})', '%m-%d-%y'),
        (r'(\d{4})(\d{2})(\d{2})', '%Y%m%d')
    ]

    for pattern, fmt in patterns:
        match = re.search(pattern, content)
        if match:
            groups = match.groups()
            try:
                date_string = '-'.join(groups)
                date_string = date_string.replace('/', '-').replace('.', '-')

                if '年' in fmt:
                    date_string = date_string.replace('年', '-').replace('月', '-').replace('日', '')

                if fmt == '%m月%d日':
                    current_year = datetime.datetime.now().year
                    date_string = f"{current_year}-{date_string.replace('月', '-').replace('日', '')}"

                if fmt == '%m-%d-%y':
                    year = int(groups[2])
                    year = 2000 + year if year < 50 else 1900 + year
                    date_string = f"{year}-{groups[0]}-{groups[1]}"

                if fmt == '%Y%m%d':
                    date_string = f"{groups[0]}-{groups[1]}-{groups[2]}"
                date = datetime.datetime.strptime(date_string, '%Y-%m-%d' if len(groups) <= 3 else '%Y-%m-%d %H:%M:%S')
                # if date <= limit_date_ago:
                #     infostr = f"【时间错误】信息过期{date.strftime('%Y-%m-%d 00:00:00')}"
                #     raise Exception(infostr)  # 如果没有匹配到任何格式,返回None
                return date.strftime('%Y-%m-%d 00:00:00')
            except ValueError:
                continue
    infostr = f"【时间错误】没有匹配到任何格式, {content}"
    raise Exception(infostr) # 如果没有匹配到任何格式,返回None
def get_machine_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    res = {"name":socket.gethostname(),"ip":local_ip}
    return res
def get_current_or_future_date(date_str):
    # 如果发布日期大于今天则默认为今天
    from datetime import datetime
    input_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if len(date_str.split(' ')) > 1 else datetime.strptime(date_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    today = datetime.now()
    return today.strftime('%Y-%m-%d') if input_date > today else input_date.strftime('%Y-%m-%d')
def find_name_by_initials(initials):
    name_to_initials = {
        "董宇鹏": "DYP",
        "龚芈俟": "GMQ",
        "康炎朔": "KYS",
        "孔超": "KC",
        "佟旭": "TX",
        "徐斌杰": "XBJ",
        "荀晓帆": "XXF",
        "张靖松": "ZJS",
        "张文松": "ZWS",
        "赵思宇": "ZSY",
        "杨勇":"YY",
        "王磊":"WL",
        "李子阳":"LZY",
        "汤靖博": "TJB",
        "张越然": "ZYR",
        "赵云泽": "ZYZ"
    }
    for name, initials_key in name_to_initials.items():
        if initials_key.lower() in initials.lower():
            return name
    return "SUPER"
def get_name_smail(name):
    name_to_initials = {
        "董宇鹏": "DYP",
        "龚芈俟": "GMQ",
        "康炎朔": "KYS",
        "孔超": "KC",
        "佟旭": "TX",
        "徐斌杰": "XBJ",
        "荀晓帆": "XXF",
        "张靖松": "ZJS",
        "张文松": "ZWS",
        "赵思宇": "ZSY",
        "杨勇":"YY",
        "王磊":"WL",
        "李子阳":"LZY",
        "汤靖博": "TJB",
       "张越然": "ZYR",
      "赵云泽": "ZYZ"
    }
    return name_to_initials[name]

def check_table_name2(data,config):
    """
    判断栏目类型
    """
    for _ in config:
        if _['text'] in data.meta['detail'][_['fieldName']]:
            return _['channelCode']['text']
def check_title_for_keywords(table_name):
    if '招标' in table_name:
        return 'ZBGG'
    elif '中标' in table_name:
        return 'ZBGS'
def filters_field_name(data,config_list:list):
    if not config_list:
        return False
    for fig in config_list:
        if fig['fieldName'] not in data.keys():
            return False
    return True
def calculate_md5(*args):
    '''md5 计算'''
    combined_str = ''.join(map(str, args))
    md5_hash = hashlib.md5(combined_str.encode()).hexdigest()
    return md5_hash
class IdWorker(object):
    """
     SnowFlake 算法,结合机器ID和数据中心ID,以及毫秒内序列号
    生成全局唯一ID
    """
    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        初始化
        :param datacenter_id: 数据中心(机器区域)ID
        :param worker_id: 机器ID
        :param sequence: 毫秒内序列号
        """
        # 校验数据中心ID和机器ID是否超过最大值
        if datacenter_id > MAX_DATACENTER_ID or worker_id > MAX_WORKER_ID:
            raise ValueError('数据中心ID或机器ID超过最大值')

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence

        self.last_timestamp = -1  # 上次计算的时间戳

    def _gen_timestamp(self):
        """
        生成整数时间戳
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def get_id(self):
        """
        获取新ID
        :return:
        """
        timestamp = self._gen_timestamp()

        # 如果上次计算的时间戳与新产生的时间戳相等,在毫秒内序列号加一,为了保证在毫秒内不会产生重复
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # 移位并通过或运算拼到一起组成64位的ID
        new_id = ((timestamp - TWEPOCH) << (WORKER_ID_BITS + DATACENTER_ID_BITS + SEQUENCE_BITS)) | \
                 (self.datacenter_id << (WORKER_ID_BITS + SEQUENCE_BITS)) | \
                 (self.worker_id << SEQUENCE_BITS) | self.sequence
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        等到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp
def get_id():
    worker = IdWorker(1, 2, 0)
    return worker.get_id()
def fromat_cms_data(data1):
    data1['title']=data1['TITLE']
    data1['content']=data1['CONTENT']
    data1['publish_date']=check_time(data1['PUBLISH_DATE'])
    data1['comments']=data1['SOURCE_URL']['source_url']
    title = data1['title']
    data1["description"]=data1["content"]
    # data1['publish_date'] =data1['publish_date']
    # try:
    #     data1['publish_date'] = get_current_or_future_date(data1['publish_date'])
    # except Exception as e:
    #     logging.error("日期转化失败get_current_or_future_date")
    data1["classd_id"] = "二手"
    if data1.get('detail_url'):
        content_to_add = f'<br><a href="{data1["detail_url"]}">点击查看原文</a>'
    else:
        content_to_add = f'<br><a href="{data1["comments"]}">点击查看原文</a>'
    data1["description"] = data1["content"] + content_to_add
    if len( data1["content"]) < 20:
        logging.error(f"内容字段长度异常，低于20个字符:{data1['description']}")
        raise Exception("内容字段长度异常，低于20个字符______________________________-----------------------------------")
    if len(data1['TITLE']) > 100:
        data1['title'] = data1['title'][:100] + "..."
        data1['description'] = f"<h2>{title}</h2" + data1['description']
    s_data = copy.deepcopy(data1)
    s_data['tablename'] = 'cms_crawl_data'
    s_data['source'] = '5'
    s_data['area']=get_area_local(data1['region'])
    s_data['area_id']=area_dict.get( s_data['area'])
    s_data["category_id"],s_data["category"] = identify_industry(s_data["title"], s_data["description"])
    s_data['main_host'] = urlparse(s_data['comments']).netloc
    s_data['deduct_md5'] = calculate_md5(s_data['comments'])
    s_data['classd_name'] = s_data["classd_name"] + "(bgspider_scrapy)"
    machine_res = get_machine_info()
    s_data['client_name'] = machine_res['name']
    s_data['client_ip'] = machine_res['ip']
    s_data['sync_status'] = 0
    s_data['program_source'] = "bgspider_scrapy"
    s_data['classd_id'] ='二手'
    s_data['ok_status'] = 'Y'
    s_data['table_name']= 'ZBXX'
    s_data['table_name2']= check_title_for_keywords(data1['channel'])
    s_data['original_id']=  get_id()
    s_data['is_deleted']= False
    s_data['responsible_person'] = find_name_by_initials(s_data['classd_name'])
    return s_data

def requests_bg(url: str = '', headers: dict = None, data: dict = None, try_number: int = 3,
                    json: json = None, params: dict = None,is_proxy=None):
        """
        请求封装
        :param url:请求url
        :param data:请求的data
        :param try_number:请求重试次数
        :return:
        """
        if not headers:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            }
        for i in range(try_number):
            try:
                if url:
                    if is_proxy:
                        proxy = get_random()
                    else:
                        proxy = None
                    if data:
                        res = requests.post(url=url, headers=headers, data=data, verify=False,proxies=proxy)
                        if res.status_code == 200:
                            return res
                    elif json:
                        res = requests.post(url=url, headers=headers, json=json, verify=False,proxies=proxy)
                        if res.status_code == 200:
                            return res
                    elif params:
                        res = requests.get(url=url, headers=headers, params=params, verify=False,proxies=proxy)
                        if res.status_code == 200:
                            return res
                    else:
                        res = requests.get(url=url, headers=headers, verify=False,proxies=proxy)
                        if res.status_code == 200:
                            return res
                else:
                    raise ValueError('url不存在')
            except Exception as e:
                pass

def build_response(req_data):
    """生成scrapy response对象，测试使用"""
    url=req_data.get('url')
    if not url:
        return {'mag':"没有请求url"}
    headers=req_data.get('headers')
    data=req_data.get('data')
    try_number=req_data.get('try_number',3)
    json=req_data.get('json')
    params=req_data.get('params')
    is_proxy=req_data.get('is_proxy')
    res=requests_bg(url=url,headers=headers,data=data,try_number=try_number,json=json,params=params,is_proxy=is_proxy)
    content_url=req_data.get('url')
    if res.status_code == 200:
        request = scrapy.Request(url=content_url)
        response = HtmlResponse(url=request.url, body=res.content, request=request, status=200)
        return response

