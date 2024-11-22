#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：client.py
@IDE     ：PyCharm 
@INFO     ： 
@Author  ：BGSPIDER
@Date    ：14/11/2024 下午2:09 
'''

from requests import Session
class ScrapydError(Exception):
    """
    客户端
    """
    default_detail = 'Scrapyd Error'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail

    def __str__(self):
        return self.detail

    def __repr__(self):
        return '{0}("{1}")'.format(self.__class__.__name__, self.detail)

class ScrapydResponseError(ScrapydError):

    default_detail = 'Scrapyd Response Error'


class Client(Session):
    def _handle_response(self, response):
        """
        处理从 Scrapyd 收到的响应
        """
        if not response.ok:
            raise ScrapydResponseError(
                "Scrapyd 返回错误 a {0} error: {1}".format(
                    response.status_code,
                    response.text))

        try:
            json = response.json()
        except ValueError:
            raise ScrapydResponseError("Scrapyd 返回的响应JSON错误"
                                       "response: {0}".format(response.text))
        if json['status'] == 'ok':
            json.pop('status')
            return json
        elif json['status'] == 'error':
            raise ScrapydResponseError(json['message'])

    def request(self, *args, **kwargs):
        response = super(Client, self).request(*args, **kwargs)
        return self._handle_response(response)
