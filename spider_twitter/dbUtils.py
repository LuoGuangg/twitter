import pymysql 
import time
import datetime
from DBUtils.PooledDB import PooledDB
from scrapy.conf import settings


class DBUtils():
    def __init__(self):
        self.pool = PooledDB(pymysql,50,host='127.0.0.1',user='root',passwd='lgroot',db='twitter',port=3306,charset="utf8")

    #查重
    def getTwitterById(self, twitterId):

        db = self.pool.connection()
        cue = db.cursor()
        
        try:  
            cue.execute("SELECT * FROM twitter WHERE twitter_id = '%s'"%twitterId)  
            results = cue.fetchall()
            if len(results) == 0:
                return False
            else:
                return True
        except Exception as e:  
            print('Insert error:',e)  
            db.rollback()  
        else:  
            db.commit()  


    # 保存twitter贴文
    def saveTwitter(self, item):
        db = self.pool.connection()
        cue = db.cursor()
        
        try:  
            GMT_FORMAT = '%I:%M %p - %d %b %Y'

            #格式化推文时间
            t = time.strptime(item['twitter_time'], GMT_FORMAT)

            #当前时间
            dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
            cue.execute("insert into twitter (twitter_id,twitter_author,twitter_content,twitter_time,twitter_reply,twitter_trunsmit,twitter_zan,twitter_img,create_date\
                ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)", \
                (item["twitter_id"], item["twitter_author"], item["twitter_content"], t, item["twitter_reply"], item["twitter_trunsmit"], item["twitter_zan"], item["twitter_img"], dt))  
            
            print("insert success")#测试语句  
        except Exception as e:  
            print('Insert error:',e)  
            db.rollback()  
        else:  
            db.commit()  


    def getSeendNameAll(self):
        db = self.pool.connection()
        cue = db.cursor()
        
        try:  
            cue.execute("SELECT seed_twitter_name FROM twitter_seed")  
            results = cue.fetchall()
            return results
        except Exception as e:  
            print('Insert error:',e)  
            db.rollback()  
        else:  
            db.commit()  


    # 设置该种子所有历史爬过
    def updateSeedTag(self, name):
        db = self.pool.connection()
        cue = db.cursor()
        
        try:  
            cue.execute("UPDATE twitter_seed SET seed_twitter_tag = 1 WHERE seed_twitter_name = '%s'"%name)  

        except Exception as e:  
            print('Insert error:',e)  
            db.rollback()  
        else:  
            db.commit()  

    # 种子爬取次数加一并且修改爬取位置
    def updateSeedCountLocation(self, name, twitterId):
        db = self.pool.connection()
        cue = db.cursor()
        
        try:  
            cue.execute("UPDATE twitter_seed SET seed_twitter_count = seed_twitter_count + 1, seed_twitter_location = '%s' WHERE seed_twitter_name = '%s'"%(twitterId, name))  

        except Exception as e:  
            print('Insert error:',e)  
            db.rollback()  
        else:  
            db.commit()  


    # 判断当前的推文之不是之前抓的最后贴文
    def isSeedLocation(self, spider_name, next_page_id):
        db = self.pool.connection()
        cue = db.cursor()
        
        try:  
            cue.execute("SELECT * FROM twitter_seed WHERE seed_twitter_name = '%s' AND seed_twitter_location = '%s'"%(spider_name, next_page_id))  
            if len(cue.fetchall()) == 1:
                return True
            else:
                return False

        except Exception as e:  
            print('Insert error:',e)  
            db.rollback()  
        else:  
            db.commit()  
