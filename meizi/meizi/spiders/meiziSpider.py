# -*- coding: utf-8 -*-
import scrapy
import re
import os
import xml.dom.minidom
from scrapy_splash import SplashRequest
from scrapy.spiders import Spider
from meizi.items import MeiziItem
from scrapy.selector import Selector


class  BaiduSpider(Spider):
    name = 'meizi'
    start_urls = ["http://www.win4000.com/meitu.html"]


    def start_requests(self):
        splash_args = {
            'wait': 0.5,
        }
        curdir = os.path.abspath('.')
        configdir = curdir + '\\config.xml'
        configstarturl = self.configparse(configdir,'Start_url')
        print(configstarturl)
        if configstarturl:
            self.start_urls[0] = configstarturl
        else:
            print('start_url not set, use the default url:http://www.win4000.com/meitu.html')

        for url in self.start_urls:
            print(url)
            yield SplashRequest(url, self.parse,endpoint='render.html',
                          args=splash_args)


    def parse(self,response):
        print("==============render over===============================")
        for sel in response.xpath('//li[@class="box masonry-brick"]/a[@href]'):
           print("=========selector========")
           item = MeiziItem()
           SourceFrom = sel.xpath('../span[@class="txt"]/span[@class="from"]/a/text()').extract()
           Imageurl = sel.xpath('.//img/@src').extract()
           Desc = sel.xpath('..//div[@class="detail"]/p/text()').extract()
           URL = sel.xpath('..//span[@class="magnifier"]/a/@href').extract()
           Imageurl_list = Imageurl[0].split('_')
           if len(Imageurl_list)>= 2:
            Imageurl_max = Imageurl_list[len(Imageurl_list) - 2]
           else:
            Imageurl_max = Imageurl_list[0]
           #打开
           item['sourcefrom'] = SourceFrom
           item['url'] = URL
           item['desc'] = Desc
           item['imageurl'] = Imageurl_max
           yield item



        #页码合集
        pages = response.xpath('//div[@id="page_warp"]/div/a[@href]')
        currentpage = pages[0].xpath('..//a[@class="current"]/text()').extract()
        nextpage = pages[0].xpath('..//a[@class="after"]/@href').extract()
        print('**********************current page%s' %currentpage)
        print('**********************next page%s'%nextpage)

        curdir = os.path.abspath('.')
        configdir = curdir + '\\config.xml'
        configpage = self.configparse(configdir,'Page');
        if configpage:
            pagelimit = configpage
        else:
            print('page not set, use the default number:10')
            pagelimit= '10'

        #转化为int比较
        curentpageint = int(currentpage[0])
        pagelimitint = int(pagelimit)


        if len(pages) > 1:
            print('current page %s' %(currentpage))

        if nextpage:
            if curentpageint <= pagelimitint:
                request = SplashRequest(nextpage[0],callback=self.parse,endpoint='render.html',
                                       args={'wait': 0.5,})
                yield request#返回请求
            else:
                print('page limitation,current page is %d' %curentpageint)
        else:
            print("it's the last page")


    def configparse(self,filedir,keyword):
        dom = xml.dom.minidom.parse(filedir)
        root = dom.documentElement
        re = root.getElementsByTagName(keyword)
        return re[0].firstChild.data

