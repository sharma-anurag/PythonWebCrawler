# -*- coding: utf-8 -*-

# Scrapy settings for amazoncrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'amazoncrawler'

SPIDER_MODULES = ['amazoncrawler.spiders']
NEWSPIDER_MODULE = 'amazoncrawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'amazoncrawler (+http://www.yourdomain.com)'
ITEM_PIPELINES = ['amazoncrawler.pipelines.AmazoncrawlerPipeline',
					'amazoncrawler.pipelines.AmazonSellerLinkPipeline',
					'amazoncrawler.pipelines.AmazonProductLinkPipeline',
					'scrapy.contrib.pipeline.images.ImagesPipeline',
					'amazoncrawler.pipelines.AmazonProductDetailPipeline'
					
				 ]

# Where we store the images, in this case they will be stored
# in E:/ImageGrabber/full directory. Change this to meet your needs.
IMAGES_STORE = 'D:/Project/2324_Scrapy/amazoncrawler/Images'