# Scrapy settings for crawl project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
BOT_NAME = "crawl"

SPIDER_MODULES = ["crawl.spiders"]
NEWSPIDER_MODULE = "crawl.spiders"
import logging
from loguru import logger


# from scrapy.utils.log import configure_logging
# configure_logging(install_root_handler=True)
# logging.disable(50) # CRITICAL = 50

# # Crawl responsibly by identifying yourself (and your website) on the user-agent
# #USER_AGENT = "crawl (+http://www.yourdomain.com)"
# LOG_ENABLED = True #是否启动日志记录，默认True
# LOG_ENCODING = 'UTF-8'
# LOG_LEVEL = 'DEBUG'  # 设置日志级别，DEBUG 级别会捕获所有日志
# # LOG_LEVEL = 'DEBUG'  # 设置日志级别，DEBUG 级别会捕获所有日志
# LOG_FORMAT = '%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(lineno)s | %(message)s'  # 设置日志格式
# LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'  # 设置日期格式
LOG_ENABLED = False

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # print("aaaaaaaaaaaa", record.pathname)
        if "spiders" in record.pathname:
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame = logging.currentframe()
            depth = 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            kwargs = {
                'exception': record.exc_info if record.exc_info else None,
                'depth': depth
            }
            logger.opt(**{k: v for k, v in kwargs.items() if v is not None}).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0)

# 添加
logger.add("./logs/scrpay_{time}.log", level="INFO", rotation="10 MB")



ROBOTSTXT_OBEY = False
COMPRESSION_ENABLED=False
DOWNLOAD_HANDLERS = {
    'http': ('crawl.fingerprint_download_handler.'
             'FingerprintDownloadHandler'),
    'https': ('crawl.fingerprint_download_handler.'
              'FingerprintDownloadHandler'),
}
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                }

HTTPERROR_ALLOWED_CODES = [403]
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "crawl.middlewares.CrawlSpiderMiddleware": 543,
#}
DOWNLOADER_MIDDLEWARES = {
    "crawl.middlewares.CloudFlareDownloadHandler": 543,
}
# Enable or disable downloader middlewares
# 请求处理中间件
DOWNLOADER_MIDDLEWARES = {
   # 'http': 'crawl.middlewares.CloudFlareDownloadHandler',
   # 'https':'crawl.middlewares.CloudFlareDownloadHandler',
   # "crawl.middlewares.DownloaderMiddleware": 100,
   "crawl.middlewares.RandomUserAgentMiddleware": 200,
   "crawl.middlewares.ProxyMiddleware": 200,
   # 'scrapy.downloadermiddlewares.ssl.SSLDownloadMiddleware': None,
   "crawl.middlewares.GetFailedUrl": 100,
   "crawl.middlewares.RequestTimeoutError": 100,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}
# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3 # 想重试几次就写几

RETRY_HTTP_CODES = [500,404, 502, 503, 504, 408,454,403]

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'crawl.pipelines.CrawlPipeline': 50
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
# # redis去重配置
# REDIS_HOST = '127.0.0.1'                           # 主机名
# REDIS_PORT = 6379                                     # 端口
# REDIS_PARAMS = {'password': ''}            # Redis连接参数  默认：REDIS_PARAMS = {'socket_timeout': 30,'socket_connect_timeout': 30,'retry_on_timeout': True,'encoding': REDIS_ENCODING,}）
# # REDIS_PARAMS['redis_cls'] = 'myproject.RedisClient' # 指定连接Redis的Python模块  默认：redis.StrictRedis
# REDIS_ENCODING = "utf-8"                              # redis编码类型  默认：'utf-8'

# REDIS_URL = 'redis://user:pass@hostname:9001'       # 连接URL（优先于以上配置）源码可以看到
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'
# 纯源生的它内部默认是用的以时间戳作为key
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'




REDIS_HOST = 'r-uncs.com'                           # 主机名
REDIS_DB = 9                           # 主机名
REDIS_PORT = 6379                                     # 端口
REDIS_PARAMS = {'password': ''}            # Redis连接参数  默认：REDIS_PARAMS = {'socket_timeout': 30,'socket_connect_timeout': 30,'retry_on_timeout': True,'encoding': REDIS_ENCODING,}）
# REDIS_PARAMS['redis_cls'] = 'myproject.RedisClient' # 指定连接Redis的Python模块  默认：redis.StrictRedis
REDIS_ENCODING = "utf-8"






# #############调度器配置###########################
# from scrapy_redis.scheduler import Scheduler
# redis 最大处理深度
# redis 最大处理深度
REDIS_PROCESSING_DEPTH = 4000
# redis 锁存活时间
REDIS_LOCK_TIME = 30
# 是否启用DNS内存缓存
DNSCACHE_ENABLED = False


SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DEPTH_PRIORITY = 1  # 广度优先
# DEPTH_PRIORITY = -1 # 深度优先
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'  # 默认使用优先级队列（默认），其他：PriorityQueue（有序集合），FifoQueue（列表）、LifoQueue（列表）
# 广度优先
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
# 深度优先
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'
CONCURRENT_REQUESTS = 8

SCHEDULER_QUEUE_KEY = '%(spider)s:requests'         # 调度器中请求存放在redis中的key
SCHEDULER_SERIALIZER = "scrapy_redis.picklecompat"  # 对保存到redis中的数据进行序列化，默认使用pickle
SCHEDULER_PERSIST = True                            # 是否在关闭时候保留原来的调度器和去重记录，True=保留，False=清空
SCHEDULER_FLUSH_ON_START = True                     # 是否在开始之前清空 调度器和去重记录，True=清空，False=不清空
SCHEDULER_IDLE_BEFORE_CLOSE = 10                    # 去调度器中获取数据时，如果为空，最多等待时间（最后没数据，未获取到）。
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'  # 去重规则，在redis中保存时对应的key
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'    # 去重规则对应处理的类