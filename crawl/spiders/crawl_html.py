# -*- coding: utf-8 -*-
import json
import re
import copy, scrapy
import time

from scrapy.http import Request, Response, JsonRequest
from crawl.items import CrawlItem
from utils.db import *
from redis_queue_file.redis_db import *
from crawl.spiders.first_url_rule import *
from crawl.spiders.list_rule import *
# from scrapy_redis.spiders import Spider
# class CrawlHtml(scrapy.Spider):
# import logging
# logger = logging.getLogger(__name__)


class CrawlHtml(scrapy.Spider):
    name = 'crawl_html'
    redis_key = f'redis_key:{name}_zset'
    custom_settings = {
        'REDIS_START_URLS_AS_ZSET': True,
    }

    def __init__(self, *args, **kwargs):
        self.redis_server = redis_server
        self.ParseAction = ParseAction()
        self.id = kwargs.get('id')
        self.v9_id = kwargs.get('v9_id')

    def start_requests(self):
        return self.first_requests()

    # while True:
    #     yield self.first_requests()
    def first_requests(self):
        for x in range(1):
            if not self.id and not self.v9_id:
                site_id, self.config = self.redis_get_rule_redis()
            else:
                site_id, self.config = self.redis_get_rule(self.v9_id, self.id)
            if self.config:
                __name = jsonpath.jsonpath(self.config, '$..name')[0]
                region = self.config['rule_data']['first_rules']['region']['text'].replace('/全国/', '')
                channel = self.config['rule_data']['first_rules']['channel']['text']
                print("地区", region)
                print("频道", channel) #/项目信息/项目公示
                # if self.config['rule_data']['first_rules']['changes']:#?debug
                #     pass
                # __id = self.config.get('site_id')
                print("site_id", site_id)
                self.logger.info(f'获取到当前任务,任务id是:{site_id};;,任务名称是{__name}')
                self.detail_info = {}
                first_rule = self.config['rule_data']['first_rules']
                self.headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                }
                cookies = {}
                try:
                    if first_rule['firstUrls'].strip():
                        start_url_list = FirstUrl().before_req(first_rule)
                        for req in start_url_list:
                            __type = req.get('type')
                            meta = {
                                'id': first_rule['id'],
                                'is_proxy': False,
                                'log': '',
                                'site_id': site_id,
                                'classd_name': __name,
                                'region': region,
                                'channel': channel,
                            }
                            start_url = req['url']
                            if 'headers' in req:
                                self.headers = req['headers']
                            if req.get('method') == 'POST':
                                data = req['data']
                                if __type == 'json':
                                    meta['__type'] = 'json'
                                    yield JsonRequest(url=start_url.strip(), headers=self.headers, data=data,
                                                      meta=copy.deepcopy(meta),
                                                      callback=self.parse, method="POST",
                                                      cookies=cookies)
                                else:
                                    meta['__type'] = 'data'
                                    yield scrapy.FormRequest(url=start_url.strip(), headers=self.headers, formdata=data,
                                                             meta=copy.deepcopy(meta),
                                                             callback=self.parse, method="POST",
                                                             cookies=cookies)
                            else:
                                yield Request(url=start_url.strip(), headers=self.headers, meta=copy.deepcopy(meta),
                                              callback=self.parse,
                                              cookies=cookies)
                    else:
                        start_url_list = FirstUrl().format_first_url(first_rule, 'page')
                        for req in start_url_list:
                            meta = {
                                'id': first_rule['id'],
                                'is_proxy': False,
                                'log': '',
                                'site_id': site_id,
                                'classd_name': __name,
                                'region': region,
                                'channel': channel,
                            }
                            __type = req.get('type')
                            start_url = req['url']
                            if 'headers' in req:
                                self.headers = req['headers']
                            if req['method'] == 'POST':
                                data = req.get('data', {})
                                meta['data'] = data
                                if __type == 'json':
                                    meta['__type'] = 'json'

                                    yield JsonRequest(url=start_url.strip(), headers=self.headers, data=data,
                                                      meta=copy.deepcopy(meta),
                                                      callback=self.parse, method="POST",
                                                      cookies=cookies)
                                else:
                                    meta['__type'] = 'data'
                                    yield scrapy.FormRequest(url=start_url.strip(), headers=self.headers, formdata=data,
                                                             meta=copy.deepcopy(meta),
                                                             callback=self.parse, method="POST",
                                                             cookies=cookies)
                            else:
                                yield Request(url=start_url.strip(), headers=self.headers, meta=copy.deepcopy(meta),
                                              callback=self.parse,
                                              cookies=cookies)
                except Exception as e:
                    update_log(f'第一次解析规则出错{str(e)}', site_id)
            else:
                self.logger.warning('当前没有任务')
    def redis_get_rule_redis(self):
        """从redis中的取出任务"""
        try:
            url_list = self.redis_server.brpop(REDIS_KEY_NAME_PREFIX, 1)  # [key, value]
            if url_list:
                seed_url = json.loads(url_list[1])
                return json.loads(url_list[1])['site_id'], seed_url
            else:
                return 0, []
        except Exception as e:
            return 0, []

    def redis_get_rule(self, v9_id, id):
        """直接从数据库中读取任务"""
        try:
            id, sss = get_task(v9_id, id)
            return id, sss
        except Exception as e:
            print(e)
            return 0, []

    def before_parse(self, response):
        """
        生成翻页规则，和下一级请求
        """
        first_rule = self.config['rule_data']['first_rules']
        start_url_list = FirstUrl().format_first_url(first_rule)
        for req in start_url_list:
            meta = {
                'id': first_rule['id'],
                'is_proxy': False,
                'log': '',
                'region': response.meta['region'],
                'channel': response.meta['channel'],
                'classd_name': response.meta['classd_name'],
                'site_id': response.meta['site_id']
            }
            start_url = req['url']
            if 'headers' in req:
                self.headers = req['headers']
            if 'data' in req:
                data = req['data']
                yield JsonRequest(url=start_url, headers=self.headers, data=data, meta=copy.deepcopy(meta),
                                  callback=self.parse, method="POST",
                                  cookies=response.cookies)
                # yield scrapy.FormRequest(url=start_url, headers=self.headers,formdata=json.dumps(data), meta=copy.deepcopy(meta),
                #               callback=self.parse, method="POST",
                #               cookies=cookies)
                # yield scrapy.FormRequest(url=start_url, headers=self.headers,body=json.dumps(data), meta=copy.deepcopy(meta),
                #               callback=self.parse, method="POST",
                #               cookies=cookies)
            else:
                yield Request(url=start_url, headers=self.headers, meta=copy.deepcopy(meta),
                              callback=self.parse,
                              cookies=response.cookies)

    def parse(self, response):
        """
        生成翻页规则，和下一级请求
        """
        self.logger.info('开始解析规则')
        logs = response.meta['log']
        # detail_ = self.ParseAction.execute(response,self.config['rule_data']['rule_tree']['list_rule'],self.config )
        try:
            detail_ = self.ParseAction.execute(response, 'list_rule', self.config)
        except Exception as e:
            detail_ = None
            logs += str(e)
        if detail_:
            self.logger.info('列表页解析成功')
            try:
                for detail in detail_:
                    meta = {
                        'detail': detail,
                        'is_proxy': True,
                        'log': logs,
                        'site_id': response.meta['site_id'],
                        'id': response.meta['id'],
                        'classd_name': response.meta['classd_name'],
                        'region': response.meta['region'],
                        'channel': response.meta['channel'],
                    }
                    req = detail['SOURCE_URL']
                    repeats = self.repeats(response, detail, 'LIST')
                    if repeats:
                        self.logger.info('当前公告被去重')
                        continue
                    filters = self.filters(detail)
                    if not filters:
                        self.logger.info('当前公告不采集')
                        continue
                    if not self.config['rule_data']['rule_tree']['detail_rule']['rules']:
                        # 当前节点已经不存在细栏请求数据
                        item_ = CrawlItem()
                        item_['TITLE'] = detail['TITLE']
                        item_['CATEGORY_ID'] = detail.get('CATEGORY_ID')
                        item_['DESCRIPTION'] = detail['DESCRIPTION']
                        item_['classd_name'] = response.meta['classd_name']
                        # item_['SITE_ID'] = response.meta['id']
                        item_['site_id'] = response.meta['site_id']
                        item_['SOURCE_URL'] = detail['SOURCE_URL']
                        item_['region'] = response.meta['region']
                        item_['channel'] = response.meta['channel']
                        if self.config['rule_data']['first_rules']['changes']:
                            item_['channel'] = check_table_name2(response,
                                                                 self.config['rule_data']['first_rules']['changes'])
                        item_['PUBLISH_DATE'] = detail['PUBLISH_DATE']
                        if 'DESCRIPTION' not in detail:
                            self.logger.info('DESCRIPTION不存在')
                            # return
                        else:
                            item_['CONTENT'] = detail['DESCRIPTION']
                            item_['DESCRIPTION'] = response.text
                            filters = self.filters(item_)
                            if not filters:
                                self.logger.info('当前公告不采集')
                                yield
                            yield item_
                    else:
                        __type = req.get('type')
                        start_url = req['url']
                        if 'headers' in req:
                            self.headers = req['headers']
                        if req['method'] == 'POST':
                            data = req.get('data', {})
                            meta['data'] = data
                            if __type == 'json':
                                meta['__type'] = 'json'

                                yield JsonRequest(url=start_url.strip(), headers=self.headers, data=data,
                                                  meta=copy.deepcopy(meta),
                                                  callback=self.parse_detail_rules, method="POST",
                                                  cookies={})
                            else:
                                meta['__type'] = 'data'
                                yield scrapy.FormRequest(url=start_url.strip(), headers=self.headers, formdata=data,
                                                         meta=copy.deepcopy(meta),
                                                         callback=self.parse_detail_rules, method="POST",
                                                         cookies={})
                        else:
                            yield Request(url=start_url.strip(), headers=self.headers, meta=copy.deepcopy(meta),
                                          callback=self.parse_detail_rules,
                                          cookies={})
            except Exception as e:
                logs += str(e) + '\n'
        else:
            logs += '++++++++++++列表解析到的数据为空++++++++++++' + '\n'
            self.logger.info(logs)
        update_log(logs, response.meta['site_id'])

    def repeats(self, response, save_data, rep_type):
        """
        repeatFlag:当前源
        repeatPosType:当前源
        repeatFlag:当前源
        去重节点,
        """
        repeats_data = {}
        self.logger.info('开始执行去重节点')
        for rep in self.config['rule_data']['first_rules']['repeats']:
            if rep['repeatPosType'] == rep_type:
                repeats_data['repeatFlag'] = rep['repeatFlag']
                repeats_data['repeat_list'] = []
                for _ in rep['sourceFieldNames']:
                    _key = ''
                    # 字段不一致，更新下
                    if _ == 'SOURCE_URL':
                        _key = 'comments'
                    elif _ == 'TITLE':
                        _key = 'title'
                    if _key:
                        if _key == 'comments':
                            _data = {
                                'key': _key,
                                'value': save_data[_]['source_url']
                            }
                        else:
                            _data = {
                                'key': _key,
                                'value': save_data[_]
                            }

                        repeats_data['repeat_list'].append(_data)
            else:
                continue
        if repeats_data:
            repeats_data['classd_name'] = response.meta['classd_name']
            status = exis_id(repeats_data)
            return status
        else:
            return '节点位置不对，跳出'

    def filters(self, save_data):
        """
        repeatFlag:当前源
        repeatPosType:当前源
        repeatFlag:当前源
        去重节点,
        """
        repeats_data = {}
        self.logger.info('开始执行过滤节点')
        filters = self.config['rule_data']['first_rules']['filters']
        if filters_field_name(save_data, filters):
            for fil in filters:
                if fil['text'] in save_data[fil['fieldName']]:
                    if fil['spiderFlag'] == 1:
                        return True
                    elif fil['spiderFlag'] == 0:
                        return False
        else:
            return '缺失字段'

    def parse_detail_rules(self, response):
        """
        列表页规则解析详情页
        :param response:
        :return:
        """
        logs = response.meta['log']
        try:
            detail_ = self.ParseAction.execute(response, 'detail_rule', self.config)
        except Exception as e:
            detail_ = None
            logs += str(e) + '\n'
        if detail_:
            self.logger.info('详情解析成功')
            try:
                for detail in detail_:
                    response.meta['detail'][detail['fieldName']] = ''.join(detail['spiderValue'])
                item_ = CrawlItem()
                item_['TITLE'] = response.meta['detail']['TITLE']
                item_['classd_name'] = response.meta['classd_name']
                # item_['SITE_ID'] = response.meta['id']
                item_['site_id'] = response.meta['site_id']
                item_['SOURCE_URL'] = response.meta['detail']['SOURCE_URL']
                item_['region'] = response.meta['region']
                item_['channel'] = response.meta['channel']
                if self.config['rule_data']['first_rules']['changes']:
                    item_['channel'] = check_table_name2(response, self.config['rule_data']['first_rules']['changes'])
                item_['PUBLISH_DATE'] = response.meta['detail']['PUBLISH_DATE']
                if 'DESCRIPTION' not in response.meta['detail']:
                    self.logger.info('DESCRIPTION不存在')
                    # return
                else:
                    item_['CONTENT'] = response.meta['detail']['DESCRIPTION']
                    item_['DESCRIPTION'] = response.text
                    filters = self.filters(item_)
                    if not filters:
                        self.logger.info('当前公告不采集')
                        yield
                    yield item_
            except Exception as e:
                logs += str(e) + '\n'
        else:
            logs += '++++++++++++详情解析到的数据为空++++++++++++' + '\n'
        update_log(logs, response.meta['site_id'])
