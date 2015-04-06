# coding=utf-8
"""

"""

__author__  = 'Shine tong<linuxtong@gmail.com>'
__version__  = "0.1.0"
__date__     = "2013-04-08"
__all__      = ['cpu','physicalMem','buffersMem','swapMem','partition','uptime',
                'process','netCard','iostat','total']

from ipaddress import ipaddress
import systeminfo
import sys



def cpu():
    cpu = systeminfo.cpuLoad()
    return cpu

def mem():
    mem = systeminfo.mem()
    return mem

def disk():
    partition =  systeminfo.disk()
    return partition

def uptime():
    load =  systeminfo.uptime()
    return load

def process():
    process =  systeminfo.process()
    return process

def netCard():
    netCard = systeminfo.net()
    return netCard

def iostat():
    iostat = systeminfo.iostat(5)
    return iostat

def maxInetipadd():
    result = []
    try:
        cardInfo = systeminfo.net()
        for card in cardInfo.keys():
            netInfo = cardInfo[card]
            ip = netInfo['ipadd']
            if ip is not None:
                result.append(ip)
    except Exception,error:
        sys.stderr.writelines("To obtain net card ip address error,code:%s\n" %error)
    if result:
        return  ipaddress.maxInetip(result)
    else:
        return None

def total():
    """
    系统运行信息，CPU,内存，进程状态，分区，负载，网卡，io等
    """
    totalInfo = {}
    try:
        project = ['cpu','mem','partition','uptime','process','netCard','io']
        info = [cpu(),mem(),disk(),uptime(),process(),netCard(),iostat()]
        totalInfo = dict(zip(project,info))
    except Exception,error:
        sys.stderr.writelines("get run info error:%s\n" %error)
    return totalInfo