# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AmazoncrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    link = scrapy.Field(serializer=str)
    desc = scrapy.Field()
    next = scrapy.Field()
    pass


class SellerItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    link = scrapy.Field()
    pass

class AmazonProductLinkItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field(serializer=str)
    productSellerAmazonId = scrapy.Field()
    next = scrapy.Field()


class AmazonProductDetailItem(scrapy.Item):
    productLinkId = scrapy.Field()
    title = scrapy.Field()
    byBrand = scrapy.Field()
    rating = scrapy.Field()
    listedPrice = scrapy.Field()     
    actualPrice = scrapy.Field()    # actual price of product on amazon (amazon price)
    savePrice = scrapy.Field()      # how much you save on product 
    availability = scrapy.Field()   # In Stock or out of stock
    image_urls = scrapy.Field()
    images = scrapy.Field()
    
class MyImageItem(scrapy.Item):

    # ... other item fields ...
    image_urls = scrapy.Field()
    images = scrapy.Field()
    path = scrapy.Field()







