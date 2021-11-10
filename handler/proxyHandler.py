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
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler
from flask import jsonify
import csv
import os
import psycopg2
from requests import head
from db.sqlClient import SqlClient
conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
         'Connection': 'keep-alive',
         'Accept-Language': 'zh-CN,zh;q=0.8'}
class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)
        self.sql = SqlClient()

    def get(self, source, https=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(source, https)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https)
        self.sql.delete(proxy)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy)
        self.sql.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        self.sql.delete(proxy)
        conn = psycopg2.connect(database="proxy",user="postgres",password="postgres",host="127.0.0.1",port="5432")
        cur = conn.cursor()
        cur = cur.execute("insert into blacklist(proxy) values ('%s')" %(proxy.proxy))
        conn.commit()
        conn.close()
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = self.db.getAll(https)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.proxy)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}

    def checkConnect(self, proxy):
        """
        renturn 连通性ok不ok
        """
        proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=(proxy))}

        try:
            r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
            if r.status_code == 200:
                 return jsonify({"status":200,"message":"Good connectivity"})
            else:
                 return jsonify({"status":201,"message":"Unable to connect"})
        except Exception as e:
            return jsonify({"status":201,"message":"Unable to connect"})