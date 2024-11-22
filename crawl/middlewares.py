# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from utils.user_agent import USER_AGENT_LIST
import random,time
from crawl.config import *
from utils.tools import *
from scrapy.downloadermiddlewares.retry import *
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from time import time
from urllib.parse import urldefrag

from tls_client import Session
from twisted.internet import threads
from twisted.internet.error import TimeoutError
from scrapy.http import HtmlResponse
from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler
import logging
from time import time
from urllib.parse import urldefrag

from tls_client import Session
from twisted.internet import threads
from twisted.internet.error import TimeoutError
from scrapy.http import HtmlResponse
from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler

logger = logging.getLogger(__name__)


class CloudFlareDownloadHandler(HTTP11DownloadHandler):

    def __init__(self, settings, crawler=None):
        super().__init__(settings, crawler)
        self.session: Session = Session(
            client_identifier="chrome_104"
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def download_request(self, request, spider):
        from twisted.internet import reactor
        timeout = request.meta.get("download_timeout") or 10
        # request details
        url = urldefrag(request.url)[0]
        start_time = time()

        # Embedding the provided code asynchronously
        d = threads.deferToThread(self._async_download, request)

        # set download latency
        d.addCallback(self._cb_latency, request, start_time)
        # check download timeout
        self._timeout_cl = reactor.callLater(timeout, d.cancel)
        d.addBoth(self._cb_timeout, url, timeout)
        return d

    def _async_download(self, request):
        timeout = int(request.meta.get("download_timeout"))
        proxies = request.meta.get("proxies") or None
        headers = request.headers.to_unicode_dict()
        if request.method == "GET":
            response = self.session.get(
                url=request.url,
                headers=headers,
                proxy=proxies,
                timeout_seconds=timeout,
            )
        else:
            response = self.session.post(
                url=request.url,
                headers=headers,
                proxy=proxies,
                timeout_seconds=timeout,
            )
        return HtmlResponse(
            url=request.url,
            status=response.status_code,
            body=response.content,
            encoding="utf-8",
            request=request,
        )

    def _cb_timeout(self, result, url, timeout):
        if self._timeout_cl.active():
            self._timeout_cl.cancel()
            return result
        raise TimeoutError(f"Getting {url} took longer than {timeout} seconds.")

    def _cb_latency(self, result, request, start_time):
        request.meta["download_latency"] = time() - start_time
        return result
logger = logging.getLogger(__name__)
class DownloaderMiddleware(object):

    def __init__(self):
        self.session: Session = Session(
            client_identifier="chrome_104"
        )

    def process_request(self, request, spider):
        # proxies = request.meta.get("proxies") or None
        headers = request.headers.to_unicode_dict()
        if request.method == "GET":
            try:
                response = self.session.get(
                    url=request.url,
                    headers=headers,
                    timeout_seconds=60,
                )
            except Exception as e:
                print(e)
        else:
            response = self.session.post(
                url=request.url,
                headers=headers,
                timeout_seconds=60,
            )
        return HtmlResponse(
            url=request.url,
            status=response.status_code,
            body=response.content,
            encoding="utf-8",
            request=request,
        )
class CrawlSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class CrawlDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class HttpError(IgnoreRequest):
    """A non-200 response was filtered"""

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(HttpError, self).__init__(*args, **kwargs)





class RandomUserAgentMiddleware(object):
    """
    随机选择user-agent的中间件
    """
    def __init__(self):
        self.user_agent_list = USER_AGENT_LIST
        self.customized_user_agent = None

    @classmethod
    def from_crawler(cls, crawler):
        """scrapy扩展"""
        obj = cls()
        crawler.signals.connect(obj.spider_opened, signal=signals.spider_opened)
        return obj

    def spider_opened(self, spider):
        """爬虫打开执行"""
        self.customized_user_agent = getattr(spider, 'user_agent', self.customized_user_agent)

    def process_request(self, request, spider):
        """添加随机ua"""
        if self.customized_user_agent:
            request.headers[b'User-Agent'] = self.customized_user_agent
        else:
            request.headers[b'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        pass
        # if request.meta.get('is_proxy', False) or PROXY_SWITCH:
        #     proxy = get_random(spider)
        #     logging.error(proxy)
        #     if request.url.startswith("http://"):
        #         proxy = proxy['http']
        #     elif request.url.startswith("https://"):
        #         proxy = proxy['https']
        #     request.meta["proxy"] = proxy


class RequestTimeoutError:
    """拦截超时错误再次请求（只请求一次）"""
    def process_exception(self, request, exception, spider):
        # 判断是否重试过
        if isinstance(exception, TimeoutError):
            if not request.meta.get('is_retry', False):
                request.meta['is_retry'] = True
                return request

class GetFailedUrl(RetryMiddleware):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            # time.sleep(random.randint(3, 5))
            logging.error(request.meta)
            # request.meta['proxy'] = get_random(spider)
            logging.error('返回值异常, 进行重试...')
            return self._retry(request, reason, spider) or response
        return response
    def tls_req(self,request):
        session=Session(
            client_identifier="chrome_104"
        )
        headers = request.headers.to_unicode_dict()
        if request.method == "GET":
            response = session.get(
                    url=request.url,
                    headers=headers,
                    timeout_seconds=60,
                )
        else:
            response = session.post(
                url=request.url,
                headers=headers,
                body=request.body,
                timeout_seconds=60,
            )
        return HtmlResponse(
            url=request.url,
            status=response.status_code,
            body=response.content,
            encoding="utf-8",
            request=request,
        )
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            # logging.error(request.meta["proxy"])
            logging.error(request.meta)
            # time.sleep(random.randint(3, 5))
            logging.error('连接异常, 进行重试...')
            # logging.error(request.meta["proxy"])
            logging.error(self.max_retry_times)
            request.meta['proxy']=get_random(spider)
            return self._retry(request, exception, spider)
