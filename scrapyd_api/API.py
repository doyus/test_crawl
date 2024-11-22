#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
@Project ：crawl 
@File    ：API.py
@IDE     ：PyCharm 
@INFO     ： 对scrapy的封装接口
@Author  ：BGSPIDER
@Date    ：14/11/2024 下午2:22 
'''
from copy import deepcopy
from scrapyd_api import constants
from scrapyd_api.client import Client
from urllib.parse import urljoin

class ScrapydAPI(object):
    """
    对scrapy的封装接口
    """

    def __init__(self, target='http://localhost:6800', auth=None,
                 endpoints=None, client=None, timeout=None):
        """
        target:scrapyd的接口，auth账户认证，endpoints：节点， client格式化的客户端，timeout超时
        """
        if endpoints is None:
            endpoints = {}

        if client is None:
            client = Client()
            client.auth = auth

        self.target = target
        self.client = client
        self.timeout = timeout
        self.endpoints = deepcopy(constants.DEFAULT_ENDPOINTS)
        self.endpoints.update(endpoints)

    def _build_url(self, endpoint):
        """
        构建，不准确
        """
        try:
            path = self.endpoints[endpoint]
        except KeyError:
            msg = '未知错误 `{0}`'
            raise ValueError(msg.format(endpoint))
        absolute_url = urljoin(self.target, path)
        return absolute_url

    def add_version(self, project, version, egg):
        """
        添加
        """
        url = self._build_url(constants.ADD_VERSION_ENDPOINT)
        data = {
            'project': project,
            'version': version
        }
        files = {
            'egg': egg
        }
        json = self.client.post(url, data=data, files=files,
                                timeout=self.timeout)
        return json['spiders']

    def cancel(self, project, job, signal=None):
        """
        关闭任务
        """
        url = self._build_url(constants.CANCEL_ENDPOINT)
        data = {
            'project': project,
            'job': job,
        }
        if signal is not None:
            data['signal'] = signal
        json = self.client.post(url, data=data, timeout=self.timeout)
        return json['prevstate']

    def delete_project(self, project):
        """
        删除项目
        """
        url = self._build_url(constants.DELETE_PROJECT_ENDPOINT)
        data = {
            'project': project,
        }
        self.client.post(url, data=data, timeout=self.timeout)
        return True

    def delete_version(self, project, version):
        """
        删除
        """
        url = self._build_url(constants.DELETE_VERSION_ENDPOINT)
        data = {
            'project': project,
            'version': version
        }
        self.client.post(url, data=data, timeout=self.timeout)
        return True

    def job_status(self, project, job_id):
        """
        返回任务的状态
        """
        all_jobs = self.list_jobs(project)
        for state in constants.JOB_STATES:
            job_ids = [job['id'] for job in all_jobs[state]]
            if job_id in job_ids:
                return state
        return ''  # Job not found, state unknown.

    def list_jobs(self, project):
        """
        返回全部的job节点
        """
        url = self._build_url(constants.LIST_JOBS_ENDPOINT)
        params = {'project': project}
        jobs = self.client.get(url, params=params, timeout=self.timeout)
        return jobs

    def list_projects(self):
        """
        返回全部的项目
        """
        url = self._build_url(constants.LIST_PROJECTS_ENDPOINT)
        json = self.client.get(url, timeout=self.timeout)
        return json['projects']

    def list_spiders(self, project):
        """
        返回全部的spider
        """
        url = self._build_url(constants.LIST_SPIDERS_ENDPOINT)
        params = {'project': project}
        json = self.client.get(url, params=params, timeout=self.timeout)
        return json['spiders']

    def list_versions(self, project):
        """
        全部的版本号
        """
        url = self._build_url(constants.LIST_VERSIONS_ENDPOINT)
        params = {'project': project}
        json = self.client.get(url, params=params, timeout=self.timeout)
        return json['versions']

    def schedule(self, project, spider, settings=None, **kwargs):
        """
        运行项目中的 spider
        """

        url = self._build_url(constants.SCHEDULE_ENDPOINT)
        data = {
            'project': project,
            'spider': spider,
        }
        data.update(kwargs)
        if settings:
            setting_params = []
            for setting_name, value in settings.items():
                setting_params.append('{0}={1}'.format(setting_name, value))
            print(setting_params)
            data['setting'] = setting_params
        json = self.client.post(url, data=data, timeout=self.timeout)
        return json['jobid']
    def log(self,basepath='./log', project=None, spider=None,task_id=None,**kwargs):
        """
        获取日志
        """
        with open(f'{basepath}/{project}/{spider}/{task_id}.log', 'r+', encoding='utf-8') as f:
            log=f.read()
        return log