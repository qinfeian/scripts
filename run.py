#!/usr/bin/env python
# coding=utf-8
"""

"""
from json import dumps,loads
from platform import uname, dist
from uuid import uuid1
import time,os,sys,socket,logging,logging.handlers,md5
import hardwareinfo
import systeminfo

#-----------------------configure-----------------------
#[local configure]
SendBuffersize = 1024000
Interval = 5
LogName  = 'client.log'
#[socket configure]
Server = '127.0.0.1'
Port   = 2000
PassWord="abc"


#-------------------progrom------------------------------
def daemonize(pidfile='/dev/null',
              stdin='/dev/null',
              stdout='/dev/null',
              stderr='/dev/null',
              startmsg = 'started with pid %s' ):
    """
         This forks the current process into a daemon.
         The stdin, stdout, and stderr arguments are file names that
         will be opened and be used to replace the standard file descriptors
         in sys.stdin, sys.stdout, and sys.stderr.
         These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
         may not appear in the order that you expect.
     """
    # flush io
    sys.stdout.flush()
    sys.stderr.flush()
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
        # Decouple from parent environment.
    cwd = os.getcwd()
    os.chdir(cwd)
    os.umask(0022)
    os.setsid()
    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
        # Open file descriptors and print start message
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)  #unbuffered
    pid = str(os.getpid())
    sys.stderr.write("\n%s\n" % startmsg % pid)
    sys.stderr.flush()
    if pidfile:
        file(pidfile,'w+').write("%s\n" % pid)
        # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def initlog(loglevel,path,logname):
    """
    @RotatingFileHandler( filename[, mode[, maxBytes[,backupCount]]])
    @setLevel
        CRITICAL 50
        ERROR    40
        WARNING  30
        DEBUG    20
        NOTSET   0
    """
    logpath =  path + os.sep +'log'
    logname = logpath + os.sep + logname
    if not os.path.exists(logpath):
        os.makedirs(logpath,0755)
        #os.popen("mkdir %s" %logpath)
    logger    = logging.getLogger()
    hdlr      = logging.handlers.RotatingFileHandler(logname,'a', 10*1024*1024,7)
    console   = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    hdlr.setFormatter(formatter)
    console.setFormatter(formatter)
    logger.addHandler(hdlr)
    if loglevel < 20:
        logger.addHandler(console)
    logger.setLevel(loglevel)
    return logger

def interval(interval):
    """
    根据间隔获取运行时间。
    """
    numList = [i for i in range(60)]
    return numList[::interval]

def send(sendObj,address,port,timeout=30):
    """
    发送数据并返回状态
    0       成功
    11      Socket初始化失败
    12      Socket连接错误
    13      Socket连接超时
    14      未知错误
    21      服务认证失败（密码错误）
    22      保留
    """
    status = 0
    sock   = 0
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error,error:
        logging.error("Socket has a error,code:%s" %error)
        status = 11
    try:
        sock.connect((address,port))
        sock.settimeout(timeout)
    except socket.gaierror,error:
        logging.error("Address-related error connecting %s:%s is error,code:%s"
                      %(address,port,error))
        status = 12
    except socket.error,error:
        logging.error("Connect to %s:%s failure,code:%s"
                      %(address,port,error))
        status = 13
    if status == 0:
        try:
            sock.sendall(sendObj)
            bakStatus = sock.recv(1024)
            if bakStatus == '00':
                logging.info("Send %s byes to %s:%s ok"
                             %(len(sendObj),address,port))
                status = 0
            elif bakStatus == '01':
                logging.error("Password error,server authentication error")
                status = 21
            elif bakStatus == '03':
                status = 22
            else:
                status = 23
        except Exception,error:
            logging.critical("socket has critical,code:%s" %error)
            status = 14
        finally:
            sock.close()
    return status

def run(timeStamp):
    """
    主程序
    """
    global  SendBuffer
    global  RunMd5
    #重新初始化硬件运行信息
    hardwareinfo.init()
    #组装hostid
    systemInfo = hardwareinfo.systemInfo()
    uuid = systemInfo['uuid']
    mac = uuid1().hex[-12:]
    hostid = "%s-%s" %(uuid,mac)
    hostid = md5.new(hostid).hexdigest()
    #获取服务器最大IP，内核等信息
    maxIp = systeminfo.maxInetipadd()
    osVersion,osName,kernel = uname()[0:3]
    kernel = "%s(%s)" %('-'.join(dist()),kernel)
    #获取硬件信息
    hdmd5 = hardwareinfo.hardwareMd5()
    if RunMd5 == hdmd5:
        hdinfo = None
    else:
        hdinfo = hardwareinfo.totalInfo()
        hdinfo['hdmd5'] = hdmd5
    RunMd5 = hdmd5
    #获取系统运行信息
    sysinfo = systeminfo.total()
    #组装发送字典
    keys = ['hostid',          #主机ID，根据主板UUID生成
            'ipadd',            #最大的公网ip
            'osVersion',        #操作系统名称{linux,windows}
            'osName',           #主机名称
            'kernel',           #内核版本
            'passwrod',          #服务器认证密码
            'hardware',         #硬件信息
            'system',           #运行信息
            'time'              #当前时间戳
            ]
    values = [hostid,
              maxIp,
              osVersion,
              osName,
              kernel,
              PassWord,
              hdinfo,
              sysinfo,
              timeStamp
            ]
    info = dict(zip(keys,values))
    SendBuffer[timeStamp] = info
    SendTmp = dumps(SendBuffer) + "\r\n"
    logging.debug("Send pretreatment:%s" %SendBuffer[timeStamp])
    logging.debug("Send buffer sieze:%s" %len(SendTmp))
    status = send(SendTmp,Server,Port)
    if status == 0:
        logging.info("Send status:%s,clear buffer" %status)
        SendBuffer = {}
    if len(SendTmp) > SendBuffersize:
        logging.critical("Max buffer size:%s,The current buffer size:%s,messages lost."
                         %(SendBuffersize,len(SendTmp)))
        SendBuffer = {}

if __name__ == '__main__':
    ProPath   = sys.path[0]
    Pidfile   = ProPath + os.sep + "client.pid"
    ProStdin  = "/dev/null"
    ProStdout = "/dev/null"
    ProStderr = ProPath + os.sep+ "error.log"
    try:
        options = sys.argv[1]
    except IndexError:
        options = ''
    if options == '-d':
        initlog(10,ProPath,LogName)
    else:
        daemonize(Pidfile,ProStdin,ProStdout,ProStderr)
        initlog(20,ProPath,LogName)
    SendBuffer={}
    RunMd5 = "old"

    while True:
        timeStamp = int(time.time())
        ltime = time.localtime(timeStamp)
        minutes = time.strftime('%M',ltime)
        second  = time.strftime('%S',ltime)
        minutes,second = int(minutes),int(second)
        if minutes in interval(Interval):
            if second == 0:
                run(timeStamp)
        time.sleep(1)