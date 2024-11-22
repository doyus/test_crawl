#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：db.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：10/9/2024 下午5:20 
'''
from utils.mysql_db import *
import json, copy
from loguru import logger as logging


def get_task(v9_id,id):
    """
    判断id是否存在
    """
    if id:
        sql = 'SELECT id,config FROM bgspider_task WHERE id = %s'
        cursor.execute(sql, (id))
    else:
        sql = 'SELECT id,config FROM bgspider_task WHERE site_id_v9 = %s'
        cursor.execute(sql, (v9_id))

    data = cursor.fetchall()
    if data:
        return data[0]['id'], json.loads(data[0]['config'])
    else:
        return 0, []
def update_scrapy_log(site_id,log):
    if len(log)>50000:
        log=log[:50000]
    insert_query = 'SELECT id  FROM scrapy_crawl_log where site_id=%s limit 1'
    cursor.execute(insert_query, (site_id))
    data = cursor.fetchall()
    if data:
        sql = f'UPDATE scrapy_crawl_log SET  log = %s WHERE site_id=%s;'
        cursor.execute(sql, (log, site_id))
    else:
        query = f"INSERT INTO scrapy_crawl_log (site_id,log) VALUES (%s,%s)"
        cursor.execute(query, [site_id,log])
    conn.commit()

def exis_url(hashs):
        """
        判断这条数据是否存在
        :return:
        """
        insert_query = 'SELECT * FROM cms_crawl_data where deduct_md5=%s limit 1'
        cursor.execute(insert_query, (hashs))
        data = cursor.fetchall()
        if data:
            return data[0]['aus_id']
        else:
            return False
def exis_id(data):
    """
    判断这条数据是否存在
    :return:
    """
    insert_query = f'SELECT * FROM cms_crawl_data where '
    _str = ''
    query_list = []
    for _data in data['repeat_list']:
        if _str=='':
            _str += _data['key'] + ' = %s'
        else:
            _str += ' and ' + _data['key'] + ' = %s'
        query_list.append(_data['value'])
    insert_query += _str
    if data['repeatFlag']:
        insert_query += ' and classd_name=%s'
        query_list.append(data['classd_name'])
    cursor.execute(insert_query, query_list)
    data = cursor.fetchall()
    if data:
        return data[0]['aus_id']
    else:
        return False


def update_num(id):
    sql = f'UPDATE bgspider_task SET  scrapy_count = scrapy_count + 1 WHERE id={id};'
    cursor.execute(sql)
    conn.commit()


def update_log(log, id):
    if not log:
        return
    sql = f'UPDATE bgspider_task SET  log = %s WHERE id=%s;'
    cursor.execute(sql, (log, id))
    conn.commit()


def save_cms_api(save_data, site_id):
    CmsCrawlDataKeys = ['deduct_md5', 'title', 'comments', 'main_host', 'ok_status', 'classd_name', 'publish_date',
                        'table_name2',
                        'classd_id', 'table_name', 'original_id', 'sync_status', 'area', 'area_id', 'category',
                        'category_id',
                        'files', 'crawl_status', 'program_source', 'client_ip', 'responsible_person', 'source'
                        ]
    CmsCrawlContentKeys = ['id', 'description']
    CmsCrawlDataAttachments = ['id', 'method', 'attachment_url', 'req_data']
    id = exis_url(save_data['deduct_md5'])
    if id:
        '''公告存在'''
        update_num(site_id)
        logging.debug(f'已经存在,id为：{id}')
    else:
        '''公告不存在'''
        if "attachment_url" in str(save_data.get('files', None)):
            crawl_status = "2"
            files = []
            att_files = save_data.get('files', None)
        else:
            crawl_status = "1"
            files = []
            att_files = None
        _save = copy.deepcopy(save_data)
        _save['crawl_status'] = crawl_status
        _save['files'] = json.dumps([])

        columns = ", ".join(CmsCrawlDataKeys)
        placeholders = ", ".join(["%s"] * len(CmsCrawlDataKeys))
        query = f"INSERT INTO cms_crawl_data ({columns}) VALUES ({placeholders})"
        cursor.execute(query, [_save[x] for x in CmsCrawlDataKeys])
        conn.commit()
        _save['id'] = cursor.lastrowid

        columns = ", ".join(CmsCrawlContentKeys)
        placeholders = ", ".join(["%s"] * len(CmsCrawlContentKeys))
        query = f"INSERT INTO cms_crawl_data_content ({columns}) VALUES ({placeholders})"
        cursor.execute(query, [_save[x] for x in CmsCrawlContentKeys])
        conn.commit()
        if att_files:
            '''存在附件'''
            for attach in att_files:
                if "http" in attach.get('attachment_url', ''):
                    req_data = attach.get('req_data', {})
                    if isinstance(req_data, str):
                        req_data = json.dumps(req_data)
                    att_data = {
                        'id': _save['id'],
                        'method': attach['method'],
                        'attachment_url': attach['attachment_url'],
                        'req_data': json.dumps(req_data, ensure_ascii=False),
                    }
                    columns = ", ".join(CmsCrawlDataAttachments)
                    placeholders = ", ".join(["%s"] * len(CmsCrawlDataAttachments))
                    query = f"INSERT INTO cms_crawl_data_attachments ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, [att_data[x] for x in CmsCrawlDataAttachments])
                    conn.commit()
        update_num(site_id)
        return f'保存成功：id是：{_save["id"]}'
