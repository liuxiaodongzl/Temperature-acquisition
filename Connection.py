#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u'''
Created on 2018年5月28日

@author: lenovo
'''
__author__ = 'liuxiaodong <122570855@qq.com>'
__version__ = '1.0.0'
__company__ = u'重庆交大'
__updated__ = '2018-05-28'

import pymysql
# host是虚拟机ip,user是自己所添加的用户，port是缺省端口，passwd是用户密码，db是数据库名
conn = pymysql.connect(host='10.1.161.149',
                       user='bridge',
                       port=3306,
                       charset='utf8',
                       passwd="wlw123456",
                       db="bridge"
                       )

cur = conn.cursor()
sql = ''' 
select sjcjtdh,mxh,xh,yzgs FROM cgqsjyzb where 1 
'''
try:
    cur.execute(sql)
    print("连接成功 ！")
except:
    print("连接信息库失败")
