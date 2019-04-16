#!/usr/bin/python3
import requests
import logging.handlers
import json, re, time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


class AliDNS():

    def __init__(self):
        config = json.load(open('config.json','r'))
        self.AccessKeyId = config['AccessKeyId']
        self.AccessKeySecret = config['AccessKeySecret']
        self.Region =config['Region']
        self.client = AcsClient(self.AccessKeyId,self.AccessKeySecret,self.Region)
        self.request = CommonRequest()

    def Get_RecordId(self,DomainName,RR):
        ''' 获取域名的RecordId'''
        self.request.set_domain('alidns.aliyuncs.com')
        self.request.set_version('2015-01-09')
        self.request.set_action_name('DescribeDomainRecords')
        self.request.add_query_param('DomainName', DomainName)
        try:
            response = self.client.do_action_with_exception(self.request)
            jsonObj = json.loads(response.decode("UTF-8"))
            records = jsonObj["DomainRecords"]["Record"]
            for code in records:
                if code["RR"] == RR:
                    return code["RecordId"]
        except:
            Logger().info("Error")
    
    def Add_Domain_Record(self,RR,value,DomainName,Type):
        '''新增域名解析方法：
            RR:二级域名记录值；
            value:所要解析的IP地址；
            DominName:主域名    
        '''
        self.request.set_accept_format('json')
        self.request.set_domain('alidns.aliyuncs.com')
        self.request.set_method('POST')
        self.request.set_version('2015-01-09')
        self.request.set_action_name('AddDomainRecord')
        self.request.add_query_param('RR', RR)
        self.request.add_query_param('Type', Type)
        self.request.add_query_param('Value', value)
        self.request.add_query_param('DomainName', DomainName)
        response = self.client.do_action(self.request)
        jsonObj = json.loads(response.decode("UTF-8"))
        #Record_id = jsonObj['RecordId']
        Logger().info(jsonObj)
        #return  Record_id

    def update_Domain_Record(self,RR,value,Type,DomainName):
        '''修改域名解析记录'''
        record_id = self.Get_RecordId(RR=RR,DomainName=DomainName)
        self.request.set_accept_format('json')
        self.request.set_domain('alidns.aliyuncs.com')
        self.request.set_method('POST')
        self.request.set_version('2015-01-09')
        self.request.set_action_name('UpdateDomainRecord')
        self.request.add_query_param('RR', RR)
        self.request.add_query_param('Type', Type)
        self.request.add_query_param('Value', value)
        self.request.add_query_param('RecordId',record_id )
        response = self.client.do_action(self.request)
        jsonObj = json.loads(response.decode("UTF-8"))
        Logger().info(jsonObj['Message'])

class GetIP():

    '''获取IP'''
    def __init__(self):
        pass

    def getLocalIP(self):
        '''获取本机的外网IP'''
        url = 'http://ip.taobao.com//service/getIpInfo.php?ip=myip'
        headers = {'Referer': 'http://ip.taobao.com/ipSearch.html',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        res = requests.get(url,headers=headers).text#content.decode()
        host = json.loads(res)['data']['ip']
        Logger().info('当前本机IP地址为：%s' % host)
        return host

    def getLocalIP1(self):
        '''获取本机的外网IP1'''
        url = 'http://ip.taobao.com/service/getIpInfo2.php'
        headers = {'Referer': 'http://ip.taobao.com/ipSearch.html',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        data = {'ip': 'myip'}
        res = requests.post(url,headers=headers,data=data).text#content.decode()
        host = json.loads(res)['data']['ip']
        Logger().info('当前本机IP地址为：%s' % host)
        return host

    def getlocalIP2(self):
        '''获取本机的外网IP2'''
        url = 'http://2018.ip138.com/ic.asp'
        headers = {'Referer': 'http://www.ip138.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        html = requests.get(url=url,headers=headers).text#content.decode()
        result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",html)
        return result[0]

    def getDomainIP(self,domain):
        '''获取域名的IP,用于验证域名解析结果'''
        header = {"referer": "https://ip.cn/index.php?ip=" + domain,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
        url = 'https://ip.cn/index.php?ip=%s' % domain
        html = requests.get(url=url, headers=header).text
        res = re.findall('\d+.\d+.\d+.\d+', html)[0]
        Logger().info('%s:域名当前解析地址为%s' % (domain, res))
        return res

    def getLocalHost(self):
        try:
            return self.getLocalIP()
        except:
            return self.getlocalIP2()


class Logger(logging.Logger):
    def __init__(self, filename=None):
        super(Logger, self).__init__(self)
        # 日志文件名
        if filename is None:
            filename = './DDNS.log'
        self.filename = filename
        # 创建一个handler，用于写入日志文件 (每天生成1个，保留30天的日志)
        fh = logging.handlers.TimedRotatingFileHandler(self.filename, 'D', 1, 30)
        fh.suffix = "%Y%m%d-%H%M.log"
        fh.setLevel(logging.DEBUG) 
        # 再创建一个handler，用于输出到控制台 
        ch = logging.StreamHandler() 
        ch.setLevel(logging.DEBUG) 
        # 定义handler的输出格式 
        formatter = logging.Formatter('[%(asctime)s] - %(filename)s [Line:%(lineno)d] - [%(levelname)s]- %(message)s') 
        fh.setFormatter(formatter) 
        ch.setFormatter(formatter) 
        # 给logger添加handler 
        self.addHandler(fh) 
        self.addHandler(ch) 

def run():
    while 1:
        domain = ['xxxx.net','xxxx.cn']
        Type = 'A'
        RR = 'test'
        value = GetIP().getLocalHost()
        for i in domain:
            url = RR + '.' + i
            if GetIP().getDomainIP(url) == value:
                Logger().info('%s:当前解析记录无异常'%url)
            else:
                Logger().info('%s:域名当前解析地址与本地地址不致，开修改解析记录' %url)
                AliDNS().update_Domain_Record(RR,value,Type,DomainName=i)
        Logger().info('进程休眠中...')
        time.sleep(600)


if __name__ == '__main__':
    
    
    run()
    
        


