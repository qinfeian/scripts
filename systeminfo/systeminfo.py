# coding=utf-8
"""
获取服务器运行状态
"""

from __future__  import  division
import re,os,time,subprocess
from time import sleep
#import pyutmp  #display linux /var/run/utmp

def rounds(digit=2,arg1=1,arg2=1,arg3=1):
    """
    rewrite
    """
    try:
        result = round((arg1/arg2/arg3),digit)
    except ZeroDivisionError:
        result = 0
    return  result


def get_stat():
    stat_file = open(r'/proc/stat','r')
    try:
        stat_info = stat_file.readline()
    finally:
        stat_file.close()
    stat_info = stat_info.split()[1::]
    stat_info = map(int, stat_info)
    filling_num = 9 - len(stat_info)
    if filling_num != 0:
        for num in xrange(filling_num):
            stat_info.append(0)
    #print stat_info
    return stat_info

def get_ifconfig():
    ipadd = {}
    ifconfigCmd = "/sbin/ifconfig"
    subp   = subprocess.Popen(ifconfigCmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    ifconfigInfo = subp.stdout.read()
    try:
        ifconfigInfo = ifconfigInfo.split("\n\n")
    except:
        ifconfigInfo = []
    findAll = re.compile(r"""(\w+\d+)
                              .*addr:(\d+.\d+.\d+.\d+)
                              """,re.I|re.X|re.S)
    for ip in ifconfigInfo:
        try:
            ipname,ip =  findAll.findall(ip)[0]
            ipadd.setdefault(ipname,[]).append(ip)
        except (ValueError,IndexError):
            pass
    return ipadd

def get_iostat():
    """

    """
    result = {}
    disk_file = open(r'/proc/diskstats','r')
    part_file = open(r'/proc/partitions','r')
    try:
        disk_info = disk_file.readlines()
        part_info = part_file.readlines()
    finally:
        disk_file.close()
        part_file.close()
    part_info = [ dev.strip().split()[3]  for dev in part_info if len(dev) > 1 ]
    for line in disk_info:
        if len(line) < 1:
            continue
        line = line.strip().split()
        dev  = line[2]
        if dev in part_info:
            result[dev] = line[3::]
    return result

def uptime():
    """
    /proc/loadavg
    0.01 0.00 0.00 1/92 32626
        lavg_1 (4.61) 1-分钟平均负载
        lavg_5 (4.36) 5-分钟平均负载
        lavg_15(4.15) 15-分钟平均负载
        nr_running (9) 在采样时刻，运行队列的任务的数目，与/proc/stat的procs_running表示相同意思
        nr_threads (84) 在采样时刻，系统中活跃的任务的个数（不包括运行已经结束的任务）
        last_pid(5662) 最大的pid值，包括轻量级进程，即线程。
    /proc/uptime
    543133.05 542932.50
        第一个参数是代表从系统启动到现在的时间(以秒为单位)
        第二个参数是代表系统空闲的时间(以秒为单位)：
    """
    project = ('uptime','freetime','load1','load5','load15','user')
    load_file = open(r'/proc/loadavg','r')
    uptime_file = open(r'/proc/uptime','r')
    try:
        uptime_info = uptime_file.read()
        load_info = load_file.read()
    finally:
        uptime_file.close()
        load_file.close()
    usetime,freetime   = [int(float(i)) for i in uptime_info.split()]
    load1,load5,load15 = load_info.split()[0:3]
    data = (usetime,freetime,load1,load5,load15,0)
    result = dict(zip(project,data))
    return result

def process():
    """
    R   running
    S   sleeping
    D   sleeping
    T   stop
    Z   zombie
    """
    project = ('total','running','sleeping','stopped','zombie')
    running = sleeping = stopped = zombie = 0
    file_list = os.listdir(r'/proc')
    pids = [i for i in file_list if re.findall(r'\d+',i)]
    total= len(pids)
    for pid in pids:
        status_file = '/proc/' + pid + '/status'
        try:
            status_file = open(status_file,'r')
        except IOError:
            break
        try:
            status_info = status_file.read()
        finally:
            status_file.close()
        status = re.findall(r'State:\s+(\w)',status_info)[0]
        if   status == 'R':
            running += 1
        elif status == 'S' or status == 'D':
            sleeping += 1
        elif status == 'T':
            stopped += 1
        elif status == 'Z':
            zombie += 1
    data = (total,running,sleeping,stopped,zombie)
    result = dict(zip(project,data))
    return result

def cpuLoad():
    """
    /proc/stat
             1          2       3       4           5       6       7     8 9
        cpu  144434599 11174 21046488 5688826509 24655741 658208 10475763 0 0
        cpu0 15429098 673 1426044 717835857 1511705 0 60234 0 0
        cpu1 17987848 2205 2587285 712141480 2784616 50045 710094 0 0
        ......
        1jiffies=0.01秒
        us --> user    用户态的CPU时间（单位：jiffies） ，不包含 nice值为负进程。
        ni --> nice    nice值为负的进程所占用的CPU时间（单位：jiffies）
        sy --> system  核心时间（单位：jiffies）
        id --> idle    除硬盘IO等待时间以外其它等待时间（单位：jiffies）
        wa --> iowait  硬盘IO等待时间（单位：jiffies） ，
        hi --> irq     硬中断时间（单位：jiffies）
        si --> softirq 软中断时间（单位：jiffies）
        st --> stealstolen
        guest          2.6.24以下内核版本没有这项数值
    """
    project = ['us','sy','ni','idle','wa','hi','si','st','gu']
    cpuinfo1 = get_stat()
    time.sleep(0.1)
    cpuinfo2 = get_stat()
    cpuinfo  = [ t2 - t1 for t1,t2 in zip(cpuinfo1,cpuinfo2)]
    total_time = sum(cpuinfo)
    cpuinfo = [ "%3.1f" %(num / total_time * 100) for num in cpuinfo]
    cpuinfo = dict(zip(project,cpuinfo))
    return cpuinfo

def mem():
    """

    """
    project = ['physical_total','physical_used','physical_free', 'physical_shard','physical_buffers','physical_cached',
                'buffers_used','buffers_cache',
                'swap_total','swap_used','swap_free']
    dicTmp = {}
    mem_file = open(r'/proc/meminfo','r')
    try:
        meminfo = mem_file.readlines()
    finally:
        mem_file.close()
    for line in meminfo:
        line = line.replace(':','').strip()
        line = re.split('\s+',line)
        if len(line) != 3:
            continue
        name,size,unit = line
        dicTmp[name] = int(size) * 1024
    buffer_free = dicTmp['MemFree'] + dicTmp['Buffers'] + dicTmp['Cached']
    buffer_used = dicTmp['MemTotal'] - buffer_free
    info = [dicTmp['MemTotal'],
            dicTmp['MemTotal'] - dicTmp['MemFree'],
            dicTmp['MemFree'],
            0,
            dicTmp['Buffers'],
            dicTmp['Cached'],
            buffer_used,
            buffer_free,
            dicTmp['SwapTotal'],
            dicTmp['SwapTotal'] - dicTmp['SwapFree'],
            dicTmp['SwapFree']
            ]
    result = dict(zip(project,info))
    return  result

def net():
    """

    """
    project = ['input','output','name','ipadd']
    net_file = open('/proc/net/dev','r')
    try:
        netInfo = net_file.readlines()
    finally:
        net_file.close()
    netInfo = netInfo[2::]
    result = {}
    ipadd = get_ifconfig()
    for net in netInfo:
        net = net.replace(':',' ')
        net =  re.split('\s+',net.strip())
        if len(net) != 17:
            continue
        cardName,receiveBytes = net[0],net[1]
        transmitBytes = net[9]
        try:
            ip = ipadd[cardName]
            ip = ','.join(ip)
        except KeyError:
            ip = None
        info = (receiveBytes,transmitBytes,cardName,ip)
        traffic = dict(zip(project,info))
        result[cardName] = traffic
    return result

def disk():
    """

    """
    project = ['filesystem','mountedon','size','used','availused','sizeuse','nodeuse']
    result = {}
    filesys = []
    with open("/proc/filesystems") as f:
        for line in f.readlines():
            if not line.startswith("nodev"):
                filesys.append(line.strip())
    retlist = []
    with open("/proc/mounts") as f:
        for line in f.readlines():
            if line.startswith('none'):continue
            fields = line.split()
            mountpoint = fields[1]
            fstype = fields[2]
            if fstype not in filesys:continue
            retlist.append(mountpoint)
    for path in retlist:
        st    = os.statvfs(path)
        size  = (st.f_blocks * st.f_frsize) / 1024
        avail = (st.f_bavail * st.f_frsize) / 1024
        used  = ((st.f_blocks - st.f_bfree) * st.f_frsize) / 1024
        percent = int(used * 100 / size)
        iused   = int((st.f_files - st.f_ffree) * 100 / st.f_files)
        info    = (0,path,size,used,avail,percent,iused)
        result[path] = dict(zip(project,info))
    return result

def iostat(interval=1):
    """
    iostat:
        0        1          2       3     4        5       6        7          8        9       10      11
        Device:  rrqm/s   wrqm/s   r/s   w/s     rsec/s   wsec/s    avgrq-sz avgqu-sz   await  svctm  %util
        sda      0.03     621.37  0.13  10.79    10.58    5057.28   463.95     0.53     48.36   2.99   3.27
        rrqm/s:         每秒进行 merge 的读操作数目。即 delta(rmerge)/s
        wrqm/s:         每秒进行 merge 的写操作数目。即 delta(wmerge)/s
        r/s:            每秒完成的读 I/O 设备次数。即 delta(rio)/s
        w/s:            每秒完成的写 I/O 设备次数。即 delta(wio)/s
        rsec/s:         每秒读扇区数。即 delta(rsect)/s
        wsec/s:         每秒写扇区数。即 delta(wsect)/s
        rkB/s:          每秒读K字节数。是 rsect/s 的一半，因为每扇区大小为512字节。
        wkB/s:          每秒写K字节数。是 wsect/s 的一半。
        avgrq-sz:       平均每次设备I/O操作的数据大小 (扇区)。即 delta(rsect+wsect)/delta(rio+wio)
        avgqu-sz:       平均I/O队列长度。即 delta(aveq)/s/1000 (因为aveq的单位为毫秒)。
        await:          平均每次设备I/O操作的等待时间 (毫秒)。即 delta(ruse+wuse)/delta(rio+wio)
        svctm:          平均每次设备I/O操作的服务时间 (毫秒)。即 delta(use)/delta(rio+wio)
        %util:          一秒中有百分之多少的时间用于 I/O 操作，或者说一秒中有多少时间 I/O 队列是非空的。
        即 delta(use)/s/1000 (因为use的单位为毫秒)

    /proc/diskstat
        0  1   2    3       4      5      6     7     8       9         10     11
        0 sda 16140 67741 1740112 1453724 16858 18744 1043336 390704 0 173612 1844580
            1、major     主设备号
            2、minor     磁盘次设备号
            3、name      磁盘的设备名
            4、rio       读请求总数
            5、rmerge    合并的读请求总数
            6、rsect     读扇区总数
            7、ruse      读数据花费的时间，单位ms
            8、wio       写请求总数
            9、wmerge    合并的写请求总数
            10、wsect    写扇区总数
            11、wuse     写数据花费的时间
            12、snow     现在正在进行的IO数等于IO队列中请求数
            13、sset     系统真正花费在IO上的时间，减去重复等待时间
            14、suse     系统花费在IO上花费的时间。
    """
    project = ['await','rsec','wsec','util','device']
    result = {}
    ioinfo_old = get_iostat()   #dict{'name':'3::'}
    sleep(interval)
    ioinfo_new = get_iostat()
    for dev in ioinfo_old.keys():
        io_old,io_new = ioinfo_old[dev],ioinfo_new[dev]
        io = [ int(io2) - int(io1) for io1,io2 in zip(io_old,io_new) ]
        #print io
        rio,rmerge,rsect,ruse,wio,wmerge,wsect,wuse,snow,sset,suse = io
        await = rounds(2 ,(ruse+wuse) ,(rio+wio) ,interval)
        rsec  = rounds(2 ,(rsect * 512) ,interval)
        wsec  = rounds(2 ,(wsect * 512) ,interval)
        util  = rounds(2 ,suse ,interval ,1000)
        info = dict(zip(project ,(await,rsec,wsec,util,dev)))
        result[dev] = info
    return result

def main():
    """
    单元测试
    """
    mark = "~*" * 20
    project = ['uptime','process','cpu','mem','net','disk','io']
    info = [uptime(),process(),cpuLoad(),mem(),net(),disk(),iostat()]
    for num,pro in enumerate(project):
        print "%s%s%s" %(mark,pro,mark)
        unit = info[num]
        for key in unit.keys():
            print "%s:%s" %(key,unit[key])

if __name__ == '__main__':
    print "start unit test"
    main()