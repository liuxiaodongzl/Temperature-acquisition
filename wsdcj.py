#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u'''
Created on 2018年5月7日

@author: lenovo
'''
__author__ = 'liuxiaodong <122570855@qq.com>'
__version__ = '1.0.0'
__company__ = u'重庆交大'
__updated__ = '2018-05-09'

import socket
import codecs
import time
"""
client
    connect()
    recv()
    send()
    sendall()
"""
# 创建套接字，绑定套接字到本地IP与端口
sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#address = ('10.1.156.82', 8001)
sk.connect(('10.1.156.82', 8001))
inp = '030300000002c5e9'
while True:
    if inp == 'exit':
        print("exit")
        break
    sk.send(codecs.decode(inp, 'hex'))
    time.sleep(2)
    result = sk.recv(1024)
    result = codecs.encode(result, 'hex')
    r = bytes(result).decode('utf-8')
    shidu = int(r[6:10], 16) / 100
    wendu = int(r[10:14], 16) / 100
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("温度：%s，湿度：%s\n" % (wendu, shidu))
sk.close()
