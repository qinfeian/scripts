# coding=utf-8
"""

"""
__author__  = 'Shine tong<linuxtong@gmail.com>'
__version__ = '0.1.0'
__date__    = '2013-03-29'
__all__     = [ 'totalInfo','blosInfo','systemInfo','cacheInfo',
                'cpuInfo','memoryInfo','netCardinfo','newInfo']

from hardwareinfo import dmidecode,kudzu,partedinfo
import os,md5

def init():
    """
    重新初始化类，获取新信息
    如未初始化，获取的信息是上一次初始化的信息
    """
    dmidecode.__init__()
    kudzu.__init__()
    partedinfo.__init__()

def blosInfo():
    return  dmidecode.blosInfo()

def systemInfo():
    return dmidecode.systemInfo()

def cacheInfo():
    return dmidecode.cacheInfo()

def cpuInfo():
    return dmidecode.cpuInfo()

def memoryInfo():
    return dmidecode.memoryInfo()

def netCardinfo():
    return kudzu.networkCard()

def diskInfo():
    return partedinfo.diskInfo()

def totalInfo():
    project = ['blos','system','cache','cpu','mem','net','disk']
    info = [blosInfo(),systemInfo(),cacheInfo(),cpuInfo(),memoryInfo(),netCardinfo(),diskInfo()]
    totalInfo = dict(zip(project,info))
    return totalInfo

def hardwareMd5():
#def newInfo(path='/tmp',cachename='hardware.info'):
#    if not os.path.exists(path):
#        os.makedirs(path,0755)
#    filename  = path + os.sep + cachename
#    try:
#        cache = open(filename, 'r' ).read()
#    except IOError:
#        cache = ""
    info = totalInfo()
    newmd5 = md5.new(str(info)).hexdigest()
#    if str(info) != str(cache):
#        fileHandle = open(filename,'w+')
#        fileHandle.write(str(info))
#    if oldmd5 == newmd5:
#        return None
#    else:
#        return info
    return newmd5