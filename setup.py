# Automatically created by: gerapy
from setuptools import setup, find_packages
setup(
    name='crawl',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy':['settings=crawl.settings']},
)