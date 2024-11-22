#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：v9_mysql.py
@IDE     ：PyCharm 
@INFO     ： 抓取v9接口到数据库
@Author  ：BGSPIDER
@Date    ：3/1/2024 下午4:26 
'''
import json
import time

import requests
from crawl.logger import logging
from crawl.spiders.parse_node import *
from mysql_db import *
from utils.tools import *

class V9:
    def __init__(self):
        self.user = ''
        self.password = ''
        self.headers = {
            "Origin": "https://spider.chinabidding.cn",
            "Referer": "https://spider.chinabidding.cn/login.do",
            "Mozilla/5.0": "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        }
        self.session = requests.session()

    def login(self):
        url = 'https://spider.chinabidding.cn/user.do?method=login'
        data = {
            "userName": self.user,
            "password": self.password,
            "locale": "zh_CN"
        }
        resp = self.session.post(url=url, data=data, headers=self.headers)

    def check_login(self):
        url = 'https://spider.chinabidding.cn/main.do'
        resp = self.session.get(url, headers=self.headers)
        if self.user in resp.text:
            return True
        else:
            return False

    def get_edit(self, id):
        url = 'https://spider.chinabidding.cn/spiderInfo.do?method=edit'
        data = {
            "id": id,
            "copy": ""
        }
        resp = self.session.post(url=url, data=data, headers=self.headers)
        count=self.get_count(resp.json()['data']['code'])
        return resp,count

    def get_list(self,page):
        url=f'https://spider.chinabidding.cn/spiderInfo.do'
        params = {
            'method': 'list',
            '_dc': '1731313870659',
            'name': '',
            'remark': '',
            'code': '',
            'url': '',
            'rank': '',
            'types': 'AUTO',
            'channelId': '',
            'siteId': '',
            'dataTypeId': '',
            'regionId': '',
            'singleFlag': '',
            'createUserName': '',
            'createTimeBegin': '',
            'createTimeEnd': '',
            'modifyUserName': '',
            'modifyTimeBegin': '',
            'modifyTimeEnd': '',
            'page': page,
            'start': (page-1)*20,
            'limit': 20,
            'sort': 'id',
            'dir': 'DESC',
        }
        resp = self.session.post(url=url,params=params, headers=self.headers)
        return resp
    def get_site(self,page):
        list_site=self.get_list(page).json()
        for si in list_site['data']:
            id=si['id']
            site_name=si['name'].split('-')[1]
            if self.exit_name(site_name):
                _config,count=self.get_edit(str(id))
                self.save_config(_config.json(),count)
            else:
                logging.debug('已经存在过这个站点')
    def exit_name(self,site_name):
        """
        判断已经存在网站名称的数量
        """
        sql='SELECT count(*) FROM bgspider_task WHERE website_name = %s'
        cursor.execute(sql, (site_name))
        data=cursor.fetchall()[0]['count(*)']
        if data>2:
            return False
        else:
            return True
    def exit_url(self,site_id):
        """
        判断id是否存在
        """
        sql='SELECT * FROM bgspider_task WHERE site_id_v9 = %s'
        cursor.execute(sql, (site_id))
        data=cursor.fetchall()
        if not data:
            return True
        else:
            return False
    def get_count(self,spiderInfoCode):
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            # 'cookie': 'gr_user_id=e26aa882-a0c4-402a-9507-8fed46dd1890; b5897e326c6777f3_gr_last_sent_cs1=300037206; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219047ba9ca01535-015a99cf8a021b6-4c657b58-1327104-19047ba9ca1140b%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkwNDdiYTljYTAxNTM1LTAxNWE5OWNmOGEwMjFiNi00YzY1N2I1OC0xMzI3MTA0LTE5MDQ3YmE5Y2ExMTQwYiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2219047ba9ca01535-015a99cf8a021b6-4c657b58-1327104-19047ba9ca1140b%22%7D; locale=zh_CN; userType=ADMIN; Hm_lvt_ebcee0764883fb81bcdd54df18970c94=1724896814; HMACCOUNT=F64227A2F5E2D8D6; ext-App.spiderInfo.ListPanel=o%3Acolumns%3Da%253Ao%25253Aid%25253Ds%2525253Ah22%255Eo%25253Aid%25253Ds%2525253Ah1%25255Ewidth%25253Dn%2525253A191%255Eo%25253Aid%25253Ds%2525253Ah2%25255Ewidth%25253Dn%2525253A379%255Eo%25253Aid%25253Ds%2525253Ah3%255Eo%25253Aid%25253Ds%2525253Ah4%255Eo%25253Aid%25253Ds%2525253Ah5%255Eo%25253Aid%25253Ds%2525253Ah6%255Eo%25253Aid%25253Ds%2525253Ah7%255Eo%25253Aid%25253Ds%2525253Ah8%255Eo%25253Aid%25253Ds%2525253Ah9%255Eo%25253Aid%25253Ds%2525253Ah10%255Eo%25253Aid%25253Ds%2525253Ah11%255Eo%25253Aid%25253Ds%2525253Ah12%255Eo%25253Aid%25253Ds%2525253Ah13%255Eo%25253Aid%25253Ds%2525253Ah14%255Eo%25253Aid%25253Ds%2525253Ah15%255Eo%25253Aid%25253Ds%2525253Ah16%255Eo%25253Aid%25253Ds%2525253Ah17%255Eo%25253Aid%25253Ds%2525253Ah18%255Eo%25253Aid%25253Ds%2525253Ah19%255Eo%25253Aid%25253Ds%2525253Ah20%255Eo%25253Aid%25253Ds%2525253Ah21%5Esort%3Do%253Aproperty%253Ds%25253Aid%255Edirection%253Ds%25253ADESC%255Eroot%253Ds%25253Adata; loginUserName=yuanbowang; session_id_czw=b1b0abcd-d90a-4858-b1c2-b28586ec0f39; userid=300037206; b5897e326c6777f3_gr_cs1=300037206; Hm_lpvt_ebcee0764883fb81bcdd54df18970c94=1727083761; sensorsdata2015jssdksession=%7B%22session_id%22%3A%22192231243fb96f07e97d81b880aa84c657b581327104192231243fce1d%22%2C%22first_session_time%22%3A1727165252599%2C%22latest_session_time%22%3A1727165253594%7D; JSESSIONID=34252248E3F0DD0DCD6CC998E308C1D7; acw_tc=2760820917273427519258945e1da9f27b801f0e5f38cbcbd7c05298395daf',
            'dnt': '1',
            'pragma': 'no-cache',
            'referer': 'https://spider.chinabidding.cn/main.do',
            'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
        }
        params = {
            'method': 'list',
            'channelId': '',
            'spiderInfoCode': spiderInfoCode,
            'infoMonitorId': '',
            '_dc': str(int(time.time()*1000)),
            'page': '1',
            'start': '0',
            'limit': '30',
            'sort': 'CREATE_TIME',
            'dir': 'DESC',
        }
        resp=self.session.get('https://spider.chinabidding.cn/info.do', params=params, headers=headers)
        return resp.json()['totalProperty']
    def save_config(self,old_json,count):
        if count==0:
            logging.info('没有数据')
            return
        new_config = v9_new_json(old_json)
        first=new_config['rule_data']['first_rules']
        site_id=first['id']
        site_name=first['name']
        site_desc=first['remark']
        logging.info(site_id)
        run_server=0
        create_time=datetime.datetime.strptime(first['createTime'], "%Y-%m-%d %H:%M:%S")
        update_time=datetime.datetime.strptime(first['createTime'], "%Y-%m-%d %H:%M:%S")
        site_config=json.dumps(new_config,ensure_ascii=False)
        site_level=0
        site_domain=get_domain(first['firstUrls'])
        run_type=3
        principal='V9'
        class_name=site_name.split(site_name.split('-')[1]+'-')[-1]
        website_name=site_name.split('-')[1]
        run_dp=1
        crawl_interval_type=1
        if self.exit_url(site_id):
            insert_query="INSERT INTO bgspider_task (site_id_v9, site_name, remark,config," \
                         "main_host,crawl_type,create_time,update_time,principal,class_name,website_name,run_dp,crawl_interval_type,v9_count" \
                           ") VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s,%s,%s,%s)"
            data_to_insert=(site_id, site_name, site_desc,site_config,site_domain,run_type,create_time,update_time,principal
                            ,class_name,website_name,run_dp,crawl_interval_type,count)
            cursor.execute(insert_query, data_to_insert)
            conn.commit()
            logging.info('保存成功')
        else:
            update_sql='UPDATE bgspider_task SET config = %s WHERE site_id_v9 = %s'
            data_to_update = (site_config, site_id)
            cursor.execute(update_sql, data_to_update)
            conn.commit()
            logging.info('已经存在,更新成功')
if __name__ == "__main__":
    demo = V9()
    demo.login()
    for x in range(1,212):
        logging.info(demo.get_site(x))

    # if '${'
    # # demo.login()
    # # cc=demo.check_login()
    # 2134439
    # 2134438
    # 2134437
    # 2134436
    # 2134435
    # 2134434
    # 2134433
    id=[
        # '2134439',
        '2137544',
    ]
    # for ii in id:
    #     cc1=demo.get_edit(ii)
    #     demo.save_config(cc1.json())
    #     print(cc1)
    # demo.save_config(cc1.json())
    # v9_new_json()
    pass
    # print(v9_new_json(cc1.json()))
