# coding=utf-8
"""
计算最大的公网IP
"""
#import socket
#import struct


#def ipDecimal(ip):
#    return socket.ntohl(struct.unpack("I",socket.inet_aton(ip))[0])
#def ipString(ip):
#    return  socket.inet_ntoa(struct.pack('I',socket.htonl(ip)))

def ipDecimal(ip):
    result = ''
    ip_section = ip.split('.')
    for num in ip_section:
        num = int(num)
        bnum = str(bin(num)[2::])
        offset = 8 - len(bnum)
        bnum = (str(0) * offset) + bnum
        result += bnum
    result = int(result,2)
    return result

def ipString(intip):
    result = ''
    ip = str(bin(intip)[2::])
    offset = 32 - len(ip)
    ip = (str(0) * offset) + ip
    num = 0
    for x in range(4):
        ip_section = ip[num:num+8]
        num += 8
        section = int(ip_section,2)
        section =  str(section) + '.'
        result += section
    result = result.strip('.')
    return result

class Ipaddress():
    """

    """
    def maxInetip(self,ipaddress):
        """
        A类： 10.0.0.0    ~ 10.255.255.255
        B类： 172.16.0.0  ~ 172.31.255.255
        C类： 192.168.0.0 ~ 192.168.255.55
        """
        aMin = ipDecimal('10.0.0.0')
        aMax = ipDecimal('10.255.255.255')
        bMin = ipDecimal('172.16.0.0')
        bMax = ipDecimal('172.31.255.255')
        cMin = ipDecimal('192.168.0.0')
        cMax = ipDecimal('192.168.255.255')
        ipInet = []
        all    = []
        ipList = ipaddress
        ipList = ','.join(ipList)
        ipList = ipList.split(',')
        for ip in ipList:
            ip = ipDecimal(ip)
            all.append(ip)
            if   aMin < ip < aMax:
                pass
            elif bMin < ip < bMax:
                pass
            elif cMin < ip < cMax:
                pass
            else:
                ipInet.append(ip)
        if ipInet:
            ipInet = sorted(ipInet,reverse=True)
            ip = ipInet[0]
            return ipString(ip)
        else:
            all = sorted(all,reverse=True)
            ip = all[0]
            return ipString(ip)

ipaddress = Ipaddress()

def test():
    """
    单元测试
    """
    data1 = ['172.16.0.1,243.88.20.2','192.168.0.5','221.202.33.44']
    data2 = ['192.168.0.1,192.168.10.86','172.16.30.33']
    print "Max ip address:%s" %ipaddress.maxInetip(data1)
    print "Max ip address:%s" %ipaddress.maxInetip(data2)
if __name__ == "__main__":
    test()