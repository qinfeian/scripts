# coding=utf-8
"""
获取服务器硬件信息

"""

import subprocess
import re

class Dmidecode():
    """
    获取板载信息
    """
    def __init__(self):
        dmidecodeCmd = "/bin/env dmidecode"
        #if os.path.isfile(dmidecodeCmd):
        subp   = subprocess.Popen(dmidecodeCmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        dmidecodeInfo= subp.stdout.read()
        try:
            dmidecodeInfo = dmidecodeInfo.split("\n\n")
        except:
            dmidecodeInfo = []
        self.dmidecodeInfo = dmidecodeInfo

    def blosInfo(self):
        dmidecodeInfo = self.dmidecodeInfo
        findAll = re.compile(r"""vendor:([^\n]+)\n             #制造商信息
                                 .*version:([^\n]+)\n          #BLOS版本
                                 .*release\s+date:([^\n]+)\n   #生产日期
                                 .*address:([^\n]+)\n          #blos地址
                                 """,re.I|re.X|re.S)
        result = {}
        project = ['vendor','version','releaseDate','address']
        for ls in dmidecodeInfo:
            #print ls
            if ls.find("BIOS Information") > 0:
                try:
                    blosInfo = findAll.findall(ls)[0]
                    blosInfo = [x.strip() for x in blosInfo]
                    result =  dict(zip(project,blosInfo))
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None
    def systemInfo(self):
        dmidecodeInfo = self.dmidecodeInfo
        findAll = re.compile(r"""manufacturer:([^\n]+)\n     #制造商信息
                                 .*product\s+name:([^\n]+)\n  #产品信息（服务器版本，比如dell R710 R10等）
                                 .*version:([^\n]+)\n         #版本
                                 .*serial\s+number:([^\n]+)\n #序列号，保修用
                                 .*uuid:([^\n]+)\n            #主板ID
                                 """,re.I|re.X|re.S)
        result = {}
        project = ['manufacturer','name','version','serialNumber','uuid']
        for ls in dmidecodeInfo:
            #print ls
            if ls.find("System Information") > 0:
                try:
                    systemInfo = findAll.findall(ls)[0]
                    systemInfo = [x.strip() for x in systemInfo]
                    result =  dict(zip(project,systemInfo))
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None
    def cacheInfo(self):
        dmidecodeInfo = self.dmidecodeInfo
        findAll = re.compile(r"""type:([^\n]+)\n        #内存类型
                                 .*capacity:([^\n]+)\n   #最大支持内存
                                 .*devices:([^\n]+)      #内存插槽数
                                 """,re.I|re.X|re.S)
        result = {}
        project = ['type','capacity','devices']
        for ls in dmidecodeInfo:
            #print ls
            if ls.find("Physical Memory Array") > 0:
                try:
                    cache = findAll.findall(ls)[0]
                    cache =  [x.strip() for x in cache]
                    result= dict(zip(project,cache))
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None
    def cpuInfo(self):
        dmidecodeInfo = self.dmidecodeInfo
        findAll = re.compile(r"""designation:([^\n]+)\n             #CPU插槽位置
                                  .*id:([^\n]+)\n                    #CPU ID
                                  .*version:([^\n]+)\n               #CPU型号
                                  .*voltage:([^\n]+)\n               #CPU电压
                                  .*clock:([^\n]+)\n                 #CPU外频
                                  .*max\s+speed:([^\n]+)\n           #CPU最大主频
                                  .*current\s+speed:([^\n]+)\n       #CPU当前主频
                                  .*upgrade:([^\n]+)\n               #CPU接口类型
                                  (?=.*core\s+count:([^\n]+)\n)?     #CPU核心个数
                                  (?=.*core\s+enabled:([^\n]+)\n)?   #CPU核心启用个数
                                  (?=.*thread\s+count:([^\n]+)\n)?   #CPU线程数
                                 """,re.I|re.X|re.S)
        result = {}
        project = ['designation','id','version','voltage','clock','maxSpeed',
                 'currentSpeed','upgrade','coreCount','coreEnabled','threadCount']
        for ls in dmidecodeInfo:
            if ls.find("Processor Information") > 0:
                try:
                    cpuInfo = findAll.findall(ls)[0]
                    cpuInfo = [ x.strip() for x in cpuInfo]
                    cpuInfo = dict(zip(project,cpuInfo))
                    cpuNum = cpuInfo['designation']
                    try:
                        if result[cpuNum]:
                            pass
                    except KeyError:
                        result[cpuNum] = cpuInfo
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None
    def memoryInfo(self):
        dmidecodeInfo = self.dmidecodeInfo
        findAll = re.compile(r"""size:([^\n]+)\n                #内存大小
                                  .*\tlocator:([^\n]+)\n         #内存插槽位置
                                  .*type:([^\n]+)\n              #内存类型
                                  .*speed:([^\n]+)\n             #内存时钟频率
                                  .*manufacturer:([^\n]+)\n      #制造商编码
                                  .*serial\s+number:([^\n]+)\n   #序列号
                                  .*asset\s+tag:([^\n]+)\n       #资产标签
                                  .*part\s+number:([^\n]+)\n?    #物料编码
                                  (?:.*rank:([^\n]+)\n?)?        #内存芯片镶嵌类型
                                 """,re.I|re.X|re.S)
        result = {}
        project = ['size','locator','type','speed','manufacturer','serialNumber',
                     'assetTag','partNumber','rank']
        for ls in dmidecodeInfo:
            if ls.find("Memory Device") > 0:
                try:
                    memoryInfo = findAll.findall(ls)[0]
                    #print memoryInfo
                    memoryInfo = [ x.strip() for x in memoryInfo]
                    memoryInfo = dict(zip(project,memoryInfo))
                    memoryNum  = memoryInfo['locator']
                    try:
                        if result[memoryNum]:
                            pass
                    except KeyError:
                        result[memoryNum] = memoryInfo
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None
class Kudzu():
    """
    获取网卡信息
    """
    def __init__(self):
        kudzuCmd  = "/bin/env kudzu --probe --class=network"
        subp      = subprocess.Popen(kudzuCmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        kudzuInfo = subp.stdout.read()
        if subp.poll() == 0:
            kudzuInfo = kudzuInfo.split("-")
        else:
            kudzuInfo = []
#        #test--code
#        kudzuInfo = open(r"netwok.info").read()
#        kudzuInfo = kudzuInfo.split("-")
#        #test--code
        self.kudzuInfo = kudzuInfo

    def networkCard(self):
        kuzuInfo = self.kudzuInfo
        findAll = re.compile(r"""device:([^\n]+)\n      #设备编号
                                  .*driver:([^\n]+)\n    #驱动版本
                                  .*desc:([^\n]+)\n      #详情
                                  .*hwaddr:([^\n]+)\n    #MAC 地址
                              """,re.I|re.X|re.S)
        result = {}
        project = ['device','driver','desc','hwaddr']
        #print kuzuInfo
        for ls in kuzuInfo:
            if ls.find("NETWORK") > 0:
                try:
                    nCinfo = findAll.findall(ls)[0]
                    nCinfo = [ x.strip() for x in nCinfo]
                    nCinfo = dict(zip(project,nCinfo))
                    cardName = nCinfo['device']
                    cardName = cardName.split(":")[0]
                    try:
                        if result[cardName]:
                            pass
                    except KeyError:
                        result[cardName] = nCinfo
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None

class Partedinfo():
    """
    获取硬盘信息
    """
    def __init__(self):
        partedCmd  = "/bin/env parted -l"
        subp      = subprocess.Popen(partedCmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        partedInfo = subp.stdout.read()
        if subp.poll() == 0:
            #partedInfo = partedInfo.strip("\n")
            partedInfo = partedInfo.split("\n\n")
        else:
            partedInfo = []
        self.partedInfo = partedInfo

    def diskInfo(self):
        partedInfo = self.partedInfo
        findAll = re.compile(r"""model:([^\n]+)\n    #硬盘模式，制造商，序列号，连接方式
                               .*disk([^:]+)         #挂载节点
                                 :([^\n]+)\n         #硬盘大小
                              """,re.I|re.X|re.S)
        result = {}
        project = ['model','device','size']
        #print partedInfo
        for ls in partedInfo:
            if ls.find("Model") >= 0:
                try:
                    diskInfo = findAll.findall(ls)[0]
                    diskInfo = [ x.strip() for x in diskInfo]
                    diskInfo = dict(zip(project,diskInfo))
                    device = diskInfo['device']
                    #print diskInfo
                    try:
                        if result[device]:
                            pass
                    except KeyError:
                        result[device] = diskInfo
                except (ValueError,IndexError):
                    pass
        if result:
            return  result
        else:
            return None

dmidecode = Dmidecode()
kudzu     = Kudzu()
partedinfo = Partedinfo()

def main():
    """
    单元测试
    """
    mark1 = "=/" * 20
    mark2 = "~*" * 20
    project = ['blos','system','cache','cpu','mem','net','disk']
    p2      = ['cpu','mem']
    info = [dmidecode.blosInfo(),dmidecode.systemInfo(),dmidecode.cacheInfo(),
            dmidecode.cpuInfo(),dmidecode.memoryInfo(),kudzu.networkCard(),partedinfo.diskInfo()]
    for num,pro in enumerate(project):
        print "%s%s%s" %(mark1,pro,mark1)
        dictInfo = info[num]
        if dictInfo is not None:
            for key in dictInfo.keys():
                if pro in p2:
                    print mark2
                    dictInfo2 = dictInfo[key]
                    for key2 in dictInfo2.keys():
                        print "\t%s:%s" %(key2,dictInfo2[key2])
                else:
                    print "%s:%s" %(key,dictInfo[key])
        else:
            print "obtain error"

if __name__ == "__main__":
    main()