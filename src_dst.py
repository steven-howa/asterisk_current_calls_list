#!/usr/bin/env python
#coding:utf-8
#此脚本中 所有的外线从SIP/Gateway中继路由出去， 分机号码是8开头的四位数， 话机是SIP话机（外线以82108869为准）。
import re
import os
import time
from prettytable import PrettyTable
def get_all_list():
    chan_detail = os.popen("asterisk -rx ' core show channels verbose'").readlines()[1:-3]
    chan_list = map(lambda x:(x.strip().split()[0],x.strip().split()[-1]),chan_detail)
    chan_list_tuple = set(map(lambda x:tuple(sorted(x)), chan_list))
    return map(lambda x:x[1], tuple(chan_list_tuple))

def get_outline_list():
    chan_detail = os.popen("asterisk -rx ' core show channels'").read() 
    chan_list =  re.findall(r'(\SIP/\Gateway-\w+)',chan_detail)
    return chan_list
def get_outline_cdr():
    a = get_outline_list()
    callin_list = []
    callout_list = []
    for n in a:
        chan_cdr = os.popen("asterisk -rx 'core show channel %s'" %n).read()
        src_dst = re.findall(r'(dst=\d+|src=\d+|duration=\d+)',chan_cdr)
        if len(src_dst) == 3:#此为呼入
            src = src_dst[0].split("=")[1]
            dst = src_dst[1].split("=")[1]
            duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[2].split("=")[1])))
            callin_list.append((src,dst,duration))
        elif len(src_dst) == 2:
            Direct_Bridge = re.findall(r'(Direct\s+Bridge:\sSIP/\w+)',chan_cdr)
            Connected_Line_ID = re.findall(r'(Connected\s+Line\s+ID:\s+\d+)',chan_cdr)
            if not Direct_Bridge:#此为呼出
                src = "初始化"
                dst = dst = src_dst[0].split("=")[1]
                duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[1].split("=")[1])))
                callout_list.append((src,dst,duration))
            elif 'Gateway' in Direct_Bridge[0]: #此为呼入
                src = Connected_Line_ID[0].split(":")[-1].strip()
                dst = src_dst[0].split("=")[1]
                duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[1].split("=")[1])))
                callin_list.append((src,dst,duration))
            elif 'SIP/8' in Direct_Bridge[0]:#此为呼出
                src = Direct_Bridge[0].split("/")[-1].strip()
                dst = src_dst[0].split("=")[1]
                duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[1].split("=")[1])))
                callout_list.append((src,dst,duration))
    return  callin_list + callout_list
                               
def get_source_destination():
    a = get_all_list()
    cdr_dst_list = []
    for n in a:
        chan_cdr = os.popen("asterisk -rx 'core show channel %s'" %n).read()
        src_dst = re.findall(r'(dst=\d+|src=\d+|duration=\d+)',chan_cdr)
        if len(src_dst) == 3:    
            src = src_dst[0].split("=")[1]
            dst = src_dst[1].split("=")[1]
            duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[2].split("=")[1])))
            cdr_dst_list.append((src,dst,duration))
        elif len(src_dst) == 2:
            Connected_Line_ID = re.findall(r'(Connected\s+Line\s+ID:\s+\d+)',chan_cdr)
            Direct_Bridge = re.findall(r'(Direct\s+Bridge:\sSIP/\w+)',chan_cdr)
            if Connected_Line_ID[0].split(":")[1].strip() == '82108869' and Direct_Bridge == ['Direct Bridge: SIP/Gateway']:
                src = '82108869'
                dst = src_dst[0].split("=")[1]
                duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[1].split("=")[1])))
                cdr_dst_list.add((src,dst,duration))
            else:
                src = Connected_Line_ID[0].split(":")[-1].strip()
                dst = src_dst[0].split("=")[1]
                duration = time.strftime('%H:%M:%S',time.gmtime(int(src_dst[1].split("=")[1])))
                cdr_dst_list.append((src,dst,duration))
    return cdr_dst_list
def cdr_test():
    cdr_list = PrettyTable(["ID","主叫", "被叫", "通话时间(秒)"])
    cdr_list.align["ID"] = "l"# Left align city names
    cdr_list.padding_width = 1
    call_list = get_source_destination()
    n = 1
    for source,destination,time in call_list:
        cdr_list.add_row([n,source,destination,time])
        n += 1
    return cdr_list
def outline_cdr_test():
    cdr_list = PrettyTable(["外线ID","主叫", "被 叫", "通话时长(秒)"])
    cdr_list.align["ID"] = "l"# Left align ID number
    cdr_list.padding_width = 1
    call_list = get_outline_cdr()
    n = 1
    for source,destination,time in call_list:
        cdr_list.add_row([n,source,destination,time])
        n += 1
    return cdr_list    
a = outline_cdr_test()
print a
