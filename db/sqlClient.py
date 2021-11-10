# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from handler.configHandler import ConfigHandler
import psycopg2


class SqlClient(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.conn = psycopg2.connect(database="proxy",user="postgres",password="postgres",host="127.0.0.1",port="5432")
        self.cur = self.conn.cursor()


    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.cur.execute("select proxy from proxy_list")
        data = self.cur.fetchall()
        c=0
        for i in data:
        	  if proxy.proxy in i:
        	  	c=1
        	  	break
        if c==0:
            self.cur.execute("insert into proxy_list (proxy,fail_count,region,annoymous,source,check_count,last_status,last_time,https,socket,username,password,delay) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(proxy.proxy,proxy.fail_count,proxy.region,proxy.anonymous,proxy.source,proxy.check_count,proxy.last_status,proxy.last_time,proxy.https,proxy.socket,proxy.username,proxy.password,proxy.delay))
            self.conn.commit()


    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        self.cur.execute("delete from proxy_list where proxy = '%s'"%(proxy.proxy))
        self.conn.commit()

    def quit(self):
        self.conn.close()
