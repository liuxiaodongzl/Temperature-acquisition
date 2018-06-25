#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u'''
Created on 2018年5月28日

@author: lenovo
'''
__author__ = 'liuxiaodong <122570855@qq.com>'
__version__ = '1.0.0'
__company__ = u'重庆交大'
__updated__ = '2018-05-29'


import socket
import codecs
import time
import pymysql
import datetime
import struct

''' 
client   
connect()   
recv()   
send()   
sendall()     
'''

# 以字典形式创建数据库配置信息，方便修改
PY_MYSQL_CONN_DICT = {
    "host": '10.1.161.149',
    "port": 3306,
    "user": 'bridge',
    "passwd": 'wlw123456',
    "db": 'bridge',
    "charset": 'utf8'
}


class dbConnect:

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.__conn_dict = PY_MYSQL_CONN_DICT

    def connect(self, cursor=pymysql.cursors.DictCursor):
        try:
            self.conn = pymysql.connect(**self.__conn_dict)
            self.cursor = self.conn.cursor(cursor=cursor)  # 数据库连接成功并返回游标
            return self.cursor
        except Exception as e:
            print("连接失败:%s" % e)

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


# crc16校验
def crc16(x):
    u'''   
    @summary: 计算CRC16值   
    @param x: bytes   
    @return: 返回2字节值，类似：b'\x7B\x2A'。   
    '''
    if not isinstance(x, bytes):
        raise ValueError('Parameter must be a bytes type')
    b = 0xA001
    a = 0xFFFF
    for byte in x:
        a = a ^ byte
        for _ in range(8):
            last = a % 2
            a = a >> 1
            if last == 1:
                a = a ^ b
    aa = '0' * (6 - len(hex(a))) + hex(a)[2:]
    ll, hh = int(aa[:2], 16), int(aa[2:], 16)
    rtn = '%x' % (hh * 256 + ll & 0xffff)
    while len(rtn) < 4:
        rtn = '0' + rtn
    rtn = hextobytes(rtn)
    return rtn


def hextobytes(x):
    u''' 
    16进制转字节流 
    '''
    if not isinstance(x, str):
        x = str(x, 'ascii')
    return bytes.fromhex(x)


def bytestohex(x):
    u''' 
        字节流转16进制 
    '''
    if not isinstance(x, bytes):
        x = bytes(x, 'ascii')
    return ''.join(["%02x" % i for i in x]).strip()


def fetchone():
    conn = dbConnect()
    cousor = conn.connect()
    sql = """
    SELECT  gcxmbm cdbm, cdmc, cgqbm, jldw, sfqy, sjlx, sflb, lbfs, lbcs, bz FROM cdb WHERE 1
     """
    cousor.execute(sql)
    result = cousor.fetchone()  # 获取第一一条数据并返回结果
    conn.close()
    return result


def insertone(**kwargs):
    conn = dbConnect()
    cursor = conn.connect()
    sql = """insert into cdb(%s) values(%s)"""
    key_list = []
    value_list = []
    for k, v in kwargs.items():
        key_list.append(k)
        value_list.append('%%(%s)s' % k)
    sql = sql % (','.join(key_list), ','.join(value_list))
    cursor.execute(sql, kwargs)
    conn.close()


def fetchtwo():
    conn = dbConnect()
    cursor = conn.connect()
    cursor.execute("select * from cdsjb")
    result = cursor.fetchall()
    conn.close()
    print("success")
    return result


def inserttwo(**kwargs):
    conn = dbConnect()
    cursor = conn.connect()
    sql = """insert into cdsjb(%s) values(%s)"""
    key_list = []
    value_list = []
    for k, v in kwargs.items():
        key_list.append(k)
        value_list.append('%%(%s)s' % k)
    sql = sql % (','.join(key_list), ','.join(value_list))
    cursor.execute(sql, kwargs)
    conn.close()


def insertthree(gcxmbm, gcxmmc):
    conn = dbConnect()
    cursor = conn.connect()
    sql = """insert into gcxmb(gcxmbm,gcxmmc) values(%s,%s)"""
    cursor.execute(sql, (gcxmbm, gcxmmc))
    conn.close()


def fetchthree():
    conn = dbConnect()
    cursor = conn.connect()
    sql = """ select * from gcxmb """
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.close()
    return result


def main():
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(sk)
    address = ('10.1.156.82', 8001)
    sk.connect(address)
    inp = '030300000002c5e9'
    gcxmbm, gcxmmc = "631507030118lxd", "温湿度处理"  # 这个为自己设定的工程项目编码和名称，用于后面对gcxmb表的操作

    # 提前定义工程编码和名称，因为需要对温度和湿度进行操作，所以定义两个，也是用于后面对cdb表的操作
    cdbm1, cdbm2 = "shidu", "wendu"
    cdmc1, cdmc2 = "湿度", "温度"

    while True:
        list_wendu = []
        list_shidu = []
        global inst_wendu  # 瞬时温度
        global inst_shidu  # 瞬时湿度
        n = 0
        begin_time = time.time()  # 开始读取是的时间戳
        while True:
            sk.send(codecs.decode(inp, 'hex'))
            try:
                result = sk.recv(1024)
            except socket.timeout:
                print('timeout')
            crc = crc16(result[:-2])  # 进行CRC16-2校验
            if crc == result[-2:]:
                print('CRC16成功')
            shidu, wendu = struct.unpack(
                '>hh', result[3:7])  # 用struct方法解析湿度和温度
            shidu /= 100
            wendu /= 100
            # 比较上一次的温湿度的波动
            with open("last_data", 'r') as r:
                last_data = r.read()
            if not last_data:  # 如果last_data.txt中没有数据，就把当前温室度作为上一次温湿度进行比较
                last_data = str(wendu) + '%' + str(shidu)  # 字符串拼接
            last_wendu, last_shidu = last_data.split("%")  # 字符串以%拆分，得到温湿度
            last_wendu, last_shidu = float(
                last_wendu), float(last_shidu)  # 转化为float型数值
            if(abs(shidu - last_shidu) > 5 or abs(wendu - last_wendu > 5)):  # 比较当前温湿度与上一次温湿度差异，波动大于5就过滤掉
                print(abs(shidu - last_shidu), abs(wendu - last_wendu))
                print("数字波动太大，未记录")
                continue
            else:
                # 将当前温度湿度写入文档作为记录
                data = str(wendu) + "%" + str(shidu)
                with open("last_data", 'w') as f:
                    f.write(data)
                n += 1
                list_shidu.append(shidu)
                list_wendu.append(wendu)
                end_time = time.time()  # 获取结束时的时间戳
                if(end_time - begin_time > 5):  # 如果如果两次间隔大于五秒，停止读取数据，开始对数据进行处理
                    inst_wendu = list_wendu[-1]  # 数组最后一个就是当时的瞬时值
                    inst_shidu = list_shidu[-1]
                    time.sleep(0.1)
                    break
                else:  # 时间没有大于五秒则继续读取数据
                    continue
        cur_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime())  # 记录处理完成的时间
        print(cur_time)
        print("实时温度%s" % (inst_wendu))
        print("实时湿度%s" % (inst_shidu))
        print("开始向数据库传入数据...")
        gcxmb_data = fetchthree()  # 先对gcxmb表进行查询，如果存在数据，则进行下一步，如果不存在就插入数据
        if not gcxmb_data:
            try:
                insertthree(gcxmbm, gcxmmc)
            except Exception:
                print("工程项目表插入失败")
        cdb_data = fetchone()  # 对cdb表进行查询，存在数据则跳过，不存在则插入数据
        if not cdb_data:
            try:
                insertone(gcxmbm=gcxmbm, cdbm=cdbm1, cdmc=cdmc1,
                          cgqbm="03", jldw="RH", sflb=1)
                insertone(gcxmbm=gcxmbm, cdbm=cdbm2, cdmc=cdmc2,
                          cgqbm="03", jldw="摄氏度", sflb=1)
            except Exception:
                print("测点表插入失败 ")
        try:  # 插入处理后的数据
            inserttwo(gcxmbm=gcxmbm, cdbm=cdbm1,
                      clsj=cur_time, inst=inst_shidu)
            inserttwo(gcxmbm=gcxmbm, cdbm=cdbm2,
                      clsj=cur_time, inst=inst_wendu)
            print("传入成功")
        except:
            print("测点数据表插入失败")
    sk.close()


main()
