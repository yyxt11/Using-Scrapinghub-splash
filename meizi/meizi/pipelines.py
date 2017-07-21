# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
import os
import pymysql
from meizi import settings
from twisted.enterprise import adbapi


#图片本地下载
class MeiziSavePicPipeline(object):
    def process_item(self, item, spider):
        print("**************************the download url is %s" %item['imageurl'])
        if item['imageurl']:
            image_url = item['imageurl']
            dir_path = '%s/%s' % (settings.IMAGES_STORE, settings.DocName)
            print("*****************the download path is %s" %dir_path)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            us = image_url.split('/')[-1]
            file_path = '%s/%s' % (dir_path,us)
            print("*****************the file path is %s" %file_path)
            with open(file_path, 'wb') as handle:
                response = requests.get(image_url, stream=True)
                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

            #去掉\u200b字符
            desc_decode = item['desc'][0].replace(u'\u200b','')
            #重命名
            refile_path = '%s/%s' % (dir_path,desc_decode+'.jpg')
            if not os.path.exists(refile_path):
             os.renames(file_path,refile_path)



        if item['url'][0] and item['desc'][0]:
            Item_dir_path = '%s/%s' %(dir_path,settings.Desc_STORE)
            file_object = open(Item_dir_path, 'a')
            file_object.write('\n'+ item['url'][0] + '    ' + desc_decode)
            file_object.close( )

        return item

#图片信息存入mysql scrapyspider_db
class MeizimysqlPipeline(object):

    def __init__(self):
        host = settings.MYSQL_HOST
        db = settings.MYSQL_DBNAME
        password = settings.MYSQL_PASSWD
        user = settings.MYSQL_USER
        self.connect = pymysql.connect(host,user,password,db,charset='utf8',use_unicode=True)
        self.cursor = self.connect.cursor()

    def process_item(self,item,spider):
        if item['url']:
            try:
                self.cursor.execute("""select*from meizi where meizi_url = %s""",item['url'][0])
                ret = self.cursor.fetchone()
                #去重操作，覆盖或写入
                if(ret):
                    self.cursor.execute("""update meizi set meizi_url=%s,
                                meizi_desc=%s,
                                meizi_from=%s,
                                meizi_imageurl=%s where meizi_url = %s""",
                                (item['url'][0],
                                 item['desc'][0],
                                 item['sourcefrom'][0],
                                 item['imageurl'],
                                 item['url'][0]))
                else:
                    self.cursor.execute("""insert into meizi(meizi_url,meizi_desc,meizi_from,meizi_imageurl)
                                value(%s,%s,%s,%s)""",
                                (item['url'][0],
                                 item['desc'][0],
                                 item['sourcefrom'][0],
                                 item['imageurl']))
                self.connect.commit()
            except Exception as err:
              print(err)
        else:
            pass
        return item;


