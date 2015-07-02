import scrapy
import MySQLdb
import re
from amazoncrawler.items import AmazoncrawlerItem
from amazoncrawler.items import AmazonProductLinkItem
from amazoncrawler.items import AmazonProductDetailItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

import dbs
from scrapy.http.request import Request
from amazoncrawler.items import SellerItem
from scrapy.selector import HtmlXPathSelector 
from scrapy.selector import Selector
from amazoncrawler.items import MyImageItem

from scrapy.contrib.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

# 1 here we gives a URL and get the list of item
class AmazonAllDepartmentSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/gp/site-directory/"
    ]
    def parse(self, response):
        for sel in response.xpath('//ul[@class="nav_cat_links"]/li'):
            item = AmazoncrawlerItem()
            # pop()  removes [u'']  tag from string
            item['title'] = sel.xpath('a/text()').extract().pop()
            item['link'] = 'http://amazon.com' + str(sel.xpath('a/@href').extract().pop())
            item['desc'] = sel.xpath('text()').extract()
            yield item



# 2 here we get product link from data base and find seller see more link then we can find amazon seller
class AmazonSellerSpider(scrapy.Spider):
    name = "amazonSellerSeeMore"
    allowed_domains = ["amazon.com"]
    

    def __init__(self):
        self.connection = dbs.get_connection()
        self.cur = self.connection.cursor()

    def start_requests(self):
        # db = MySQLdb.connect(self.host, self.user, self.password, self.db)
        # cur = db.cursor()
        self.cur.execute("select ProductDepartmentId,ProductDepartmentLilnk FROM amazon_project.ProductDepartment")
        for link in self.cur.fetchall():
            yield Request(
                    url= link[1], #''.join(('http://www.pytexas.org', href)),
                    callback=self.parseSeller,
                    meta={'ProductDepartmentId': link[0]}
                )
            # yield Request(link[1], callback=self.parseSeller)

    def parseSeller(self, response):
        hxs = HtmlXPathSelector(response)
        item = SellerItem()
        item['title'] = response.meta['ProductDepartmentId']
        item['link'] = 'http://amazon.com' + str(hxs.select('//ul[@id="ref_303116011"]/li/a/@href').extract().pop())
        # for j in range(len(item['link'])):
        # self.cur.execute("""INSERT INTO amazon_project.ProductSellerSeeMore (ProductId,ProductSellerSeeMoreLink) 
        #                     VALUES (%s,%s)""", (item['title'],item['link']))

        args = [item['title'],item['link']]
        self.cur.callproc('InsertProductSellerSeeMore',args)
        self.connection.commit()
        return item




# 3 here we find amazon seller link
class AmazonSellerLinkSpider(scrapy.Spider):
    name = "amazonSellerAmazonLink"
    allowed_domains = ["amazon.com"]
    
    def __init__(self):
        self.connection = dbs.get_connection()
        self.cur = self.connection.cursor()

    def start_requests(self):
        self.cur.execute("select ProductSellerSeeMoreId,ProductSellerSeeMoreLink FROM amazon_project.ProductSellerSeeMore")
        for link in self.cur.fetchall():
            yield Request(
                    url= link[1], #''.join(('http://www.pytexas.org', href)),
                    callback=self.parseSeller,
                    meta={'ProductSellerSeeMoreId': link[0]}
                )


    def parseSeller(self, response):
        for sel in response.xpath('//div[@id="ref_303116011"]/ul/li'):
            item = AmazoncrawlerItem()
            # pop()  removes [u'']  tag from string
            item['title'] = sel.xpath('a/span[@class="refinementLink"]/text()').extract()
            item['link'] = 'http://amazon.com' + str(sel.xpath('a/@href').extract().pop())
            item['desc'] = response.meta['ProductSellerSeeMoreId']
            yield item




# 4 get Amazon product link 
class AmazonProductLinkSpider(scrapy.Spider):
    name = "amazonProductLink"
    allowed_domains = ["amazon.com"]
    

    def __init__(self):
        self.connection = dbs.get_connection()
        self.cur = self.connection.cursor()

    def start_requests(self):
        self.cur.execute("select ProductSellerAmazonId,ProductSellerAmazonLink FROM amazon_project.ProductSellerAmazon where ProductSellerAmazonTitle = 'Amazon.com'")
        for link in self.cur.fetchall():
            yield Request(
                    url= link[1], #''.join(('http://www.pytexas.org', href)),
                    callback=self.parseSeller,
                    meta={'ProductSellerAmazonId': link[0]}
                )


    def parseSeller(self, response):
        for sel in response.xpath('//div[@class="s-item-container"]/div[@class="a-row a-spacing-mini"][1]'):
            item = AmazonProductLinkItem()
            # pop()  removes [u'']  tag from string
            item['title'] = str(sel.xpath('div[@class="a-row a-spacing-none"]/a/@title').extract().pop())
            item['link'] = str(sel.xpath('div[@class="a-row a-spacing-none"]/a/@href').extract().pop()) ##'http://amazon.com' + str(sel.xpath('div[@class="a-row a-spacing-none"]/a/@href').extract().pop())
            item['productSellerAmazonId'] = int(response.meta['ProductSellerAmazonId'])
            item['next'] = sel.xpath('//div[@id="pagn"]/span[@class="pagnRA"]/a[@id="pagnNextLink"]/@href').extract()
            try:
                yield Request(
                        url= 'http://amazon.com' + item['next'][0], 
                        callback=self.parseSeller,
                        meta={'ProductSellerAmazonId': item['productSellerAmazonId']}
                    )
            except IndexError:
                item['next'] = null   
            yield item
            



# 5 get all the information of Product 
class AmazonProductDetailSpider(scrapy.Spider):
    name = "AmazonProductDetail"
    allowed_domains = ["amazon.com"]
    
    
    def __init__(self):
        self.connection = dbs.get_connection()
        self.cur = self.connection.cursor()

    def start_requests(self):
        self.cur.execute("select ProductAmazonLinkId,ProductAmazonLink FROM amazon_project.ProductAmazonLink where ProductAmazonLinkId = 1")
        for link in self.cur.fetchall():
            yield Request(
                    url= link[1], #''.join(('http://www.pytexas.org', href)),
                    callback=self.parseDetail,
                    meta={'ProductAmazonLinkId': link[0]}
                )

    def parseDetail(self, response):
        hxs = HtmlXPathSelector(response)
        item = AmazonProductDetailItem()

        item['productLinkId'] = int(response.meta['ProductAmazonLinkId'])
        item['title'] = hxs.select('//div[@class="a-section a-spacing-none"]/h1[@id="title"]/span[@id="productTitle"]/text()').extract()
        item['byBrand'] = hxs.select('//div[@class="a-section a-spacing-none"]/a[@id="brand"]/text()').extract()
        item['rating'] = hxs.select('//span[@id="acrPopover"]/span[@class="a-declarative"]/a/i[1]/@class').extract()
        item['listedPrice'] = hxs.select('//div[@id="price"]/table[@class="a-lineitem"]/tr/td[@class="a-span12 a-color-secondary a-size-base a-text-strike"]/text()').extract()
        item['actualPrice'] = hxs.select('//div[@id="price"]/table[@class="a-lineitem"]/tr/td[@class="a-span12"]/span[@id="priceblock_ourprice"]/text()').extract()
        item['savePrice'] = hxs.select('//div[@id="price"]/table[@class="a-lineitem"]/tr/td[@class="a-span12 a-color-price a-size-base"]/text()').extract()
        item['availability'] = hxs.select('//div[@id="availability_feature_div"]/div[@id="availability"]/span[@class="a-size-medium a-color-success"]/text()').extract()
        # print item['listedPrice']
        # print item['listedPrice'][0]
        if len(item['listedPrice']) == 0:
            item['listedPrice'] = 0
        item['listedPrice'] = re.findall(r"[-+]?\d*\.*\d+", str(item['listedPrice']))

        if len(item['actualPrice']) == 0:
            item['actualPrice'] = 0
        item['actualPrice'] = re.findall(r"[-+]?\d*\.*\d+", str(item['actualPrice']))

        if len(item['savePrice']) == 0:
            item['savePrice'] = 0
        item['savePrice'] = re.findall(r"[-+]?\d*\.*\d+", str(item['savePrice']))
        # item['savePrice'] = str(item['savePrice']).split(';')

        self.cur.execute("""insert into amazon_project.ProductAmazonDetail (ProductAmazonLinkId, Title, byBrand, Rating, ListedPrice, ActualPrice, SavePrice, Availibility)
                        values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                           (item['productLinkId'],
                            item['title'][0],
                            item['byBrand'][0],
                            item['rating'][0],
                            item['listedPrice'][0],
                            item['actualPrice'][0],
                            item['savePrice'][0],
                            item['availability'][0].strip(),
                           ))
        # args = [item['productLinkId'],
        #         item['title'][0],
        #         item['byBrand'][0],
        #         item['rating'][0],
        #         item['listedPrice'],
        #         item['actualPrice'][0],
        #         item['savePrice'],
        #         item['availability'][0].strip()]

        # self.cur.callproc('InsertProductAmazonDetail',args)
        self.connection.commit()
        
        for sel in response.xpath('//div[@id="altImages"]/ul/li/span/span/span/span/span'):
            image_urls  = sel.xpath('img/@src').extract()
            item['image_urls'] = [x for x in image_urls]
            yield item
        # return item




class ImageSpider(scrapy.Spider):
    name = "wikipedia"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://wwsw.amazon.com/Google-Chromecast-Streaming-Media-Player/dp/B00DR0PDNE/ref=sr_1_1?m=ATVPDKIKX0DER&s=tv&ie=UTF8&qid=1422348776&sr=1-1"
    ]
    def parse(self, response):
        for sel in response.xpath('//div[@id="altImages"]/ul/li/span/span/span/span/span'):
            item = MyImageItem()
            # pop()  removes [u'']  tag from string
            image_urls  = sel.xpath('img/@src').extract()
            item['image_urls'] = [x for x in image_urls]
            yield item



class LoginSpider(scrapy.Spider):
    name = 'login'
    allowed_domains = ['amazon.com']
    start_urls = ['https://www.amazon.in/ap/signin?_encoding=UTF8&openid.assoc_handle=inflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin']

    def parse(self, response):
        return [FormRequest.from_response(response,
                    formdata={'email': 'xxx@live.com', 'xxx': 'xxx'},
                    callback=self.after_login)]

    def after_login(self, response):
        # check login succeed before going on
        print "checkk success"
        if "authentication failed" in response.body:
            print "Login failed"
            return
