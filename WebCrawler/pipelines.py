# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import MySQLdb
import hashlib
import db
from scrapy.exceptions import DropItem
from scrapy.http import Request

#from scrapy.contrib.pipeline.images import ImagesPipeline, ImageException


class AmazoncrawlerPipeline(object):
    
    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        # below line specify which spider run then this execute
        if spider.name not in ['amazon']: 
            return item  

        try:
            # self.cursor.execute("""INSERT INTO amazon_project.ProductDepartment (ProductTitle,ProductDepartmentLilnk)
            #                 VALUES (%s,%s)""", 
            #                (item['title'],item.get('link')))
            args = [item['title'],item.get('link')]
            self.cursor.callproc('InsertProductDepartment',args)
            self.connection.commit()

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        return item


class AmazonSellerLinkPipeline(object):
    """docstring for AmazonSellerLinkSpider"""
   

    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = self.connection.cursor()
        
    def process_item(self, item, spider):
        if spider.name not in ['amazonSellerAmazonLink']: 
            return item  

        try:
            # self.cursor.execute("""INSERT INTO amazon_project.ProductSellerAmazon (ProductSellerSeeMoreId,ProductSellerAmazonTitle,ProductSellerAmazonLink) 
            #                 VALUES (%s,%s,%s)""", (item['desc'],item['title'],item['link']))

            args = [item['desc'],item['title'],item['link']]
            self.cursor.callproc('InsertProductSellerAmazon',args)
            self.connection.commit()

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        return item


class AmazonProductLinkPipeline(object):
    """docstring for AmazonSellerLinkSpider"""
    

    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = self.connection.cursor()
        
    def process_item(self, item, spider):
        if spider.name not in ['amazonProductLink']: 
            return item  

        try:
            # self.cursor.execute("""INSERT INTO amazon_project.ProductAmazonLink (ProductSellerAmazonId,ProductAmazonLinkTitle,ProductAmazonLink) 
            #                 VALUES (%s,%s,%s)""", (item['productSellerAmazonId'],item['title'],item['link']))
            
            args = [item['productSellerAmazonId'],item['title'],item['link']]
            self.cursor.callproc('InsertProductAmazonLink',args)
            self.connection.commit()

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        return item



class AmazonProductDetailPipeline(object):
    
    
    def __init__(self):
        self.connection = db.get_connection()
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        if spider.name not in ['AmazonProductDetail']: 
            return item

        try:
            # self.cursor.execute("INSERT INTO amazon_project.ProductAmazonDetailImage (ProductAmazonLinkId, ImageURL, ImageLocalPath)" + 
            #                     "VALUES (" + item['productLinkId'] + ",'" + item['image_urls'][0] + "','" + item['images'][0]['path'] + "')" + 
            #                     " ON DUPLICATE KEY UPDATE " + "ProductAmazonLinkId= VALUES(" + item['productLinkId'] + ")," + 
            #                     "ImageURL= VALUES(" + item['image_urls'][0] + "), ImageLocalPath= VALUES(" + item['images'][0]['path'] + ")" )

            self.cursor.execute("""INSERT INTO amazon_project.ProductAmazonDetailImage (ProductAmazonLinkId, ImageURL, ImageLocalPath)
                                VALUES (%s, %s, %s)  ON DUPLICATE KEY UPDATE    
                            ProductAmazonLinkId= VALUES(ProductAmazonLinkId), ImageURL= VALUES(ImageURL), ImageLocalPath= VALUES(ImageLocalPath)""",
                           (item['productLinkId'],
                            item['image_urls'][0],
                            item['images'][0]['path'],
                           ))
            # self.cursor.execute("""REPLACE into amazon_project.ProductAmazonDetailImage (ProductAmazonLinkId, ImageURL, ImageLocalPath) VALUES (%s, %s, %s)""",
            #                      (item['productLinkId'], 
            #                       item['image_urls'][0], 
            #                       item['images'][0]['path']))
            self.connection.commit()

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        return item


# class ProjectImagePipeline(object):


    
#     def __init__(self):
#         self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
#         self.cursor = self.connection.cursor()

#     def process_item(self, item, spider):
#         if spider.name not in ['Wiki']: 
#             return item

#         try:
#             self.cursor.execute("""INSERT INTO amazon_project.image (ProductAmazonLinkId, ImageURL, ImageLocalPath)
#                         VALUES (%s, %s, %s)""",
#                            (item['productLinkId'][0],
#                             item['image_urls'][0],
#                             item['images'][0]['path'],
#                            ))
#             self.connection.commit()

#         except MySQLdb.Error, e:
#             print "Error %d: %s" % (e.args[0], e.args[1])
#         return item
# class MyImagePipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         return [Request(x) for x in item.get('image_urls', [])]

#     def item_completed(self, results, item, info):
#         item['images'] = [x for ok, x in results if ok]
#         return item

#     # Override the convert_image method to disable image conversion
#     def convert_image(self, image, size=None):
#         buf = StringIO()
#         try:
#             image.save(buf, image.format)
#         except Exception, ex:
#             raise ImageException("Cannot process image. Error: %s" % ex)
#         return image, buf

#     def image_key(self, url):
#         image_guid = hashlib.sha1(url).hexdigest()
#         return 'full/%s.jpg' % (image_guid)        