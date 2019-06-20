import requests, os
import json, re, time
import logging.handlers
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest


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

class GetIP():
    '''获取IP'''

    def __init__(self):
        pass

    def getLocalIP(self):
        '''获取本机的外网IP'''
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=myip'
        headers = {'Referer': 'http://ip.taobao.com/ipSearch.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        res = requests.get(url, headers=headers).text  # content.decode()
        host = json.loads(res)['data']['ip']
        Logger().info('当前本机IP地址为：{}'.format(host))
        return host

    def getLocalIP1(self):
        url = 'https://httpbin.org/get?show_env=1'
        result = requests.get(url).json()
        host = result['headers']['X-Real-Ip']
        Logger().info('当前本机IP地址为：{}'.format(host))
        return host


    def getLocalHost(self):
        try:
            return self.getLocalIP()
        except:
            return self.getlocalIP1()

class AliDNS():

    def __init__(self):
        with open(os.path.abspath('config.json'), 'r') as f:
            self.config = json.load(f)
            self.AccessKeyId = self.config['AccessKeyId']
            self.AccessKeySecret = self.config['AccessKeySecret']
            self.Region = self.config['Region']
            self.client = AcsClient(self.AccessKeyId, self.AccessKeySecret, self.Region)

    def Get_RecordId(self, DomainName, RR):
        ''' 获取域名的RecordId'''
        self.request = CommonRequest()
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

    def Add_Domain_Record(self, RR, value, DomainName, Type):
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
        Logger().info(jsonObj)

    def update_Domain_Record(self, RR, value, Type, DomainName):
        '''修改域名解析记录'''
        self.request = CommonRequest()
        record_id = self.Get_RecordId(RR=RR, DomainName=DomainName)
        self.request.set_accept_format('json')
        self.request.set_domain('alidns.aliyuncs.com')
        self.request.set_method('POST')
        self.request.set_version('2015-01-09')
        self.request.set_action_name('UpdateDomainRecord')
        self.request.add_query_param('RR', RR)
        self.request.add_query_param('Type', Type)
        self.request.add_query_param('Value', value)
        self.request.add_query_param('RecordId', record_id)
        response = self.client.do_action(self.request)
        jsonObj = json.loads(response.decode("UTF-8"))
        Logger().info(jsonObj)

    def Get_Result(self, keyword, domain, Type):
        self.request = DescribeDomainRecordsRequest()
        self.request.set_accept_format('json')
        self.request.set_RRKeyWord(keyword)
        self.request.set_DomainName(domain)
        response = self.client.do_action_with_exception(self.request)
        jsonObj = json.loads(response.decode("UTF-8"))
        try:
            for i in jsonObj['DomainRecords']['Record']:
                if i['Type'] == Type and i['RR'] == keyword:
                    return i['Value']
        except:
            return '127.0.0.1'

    def Get_Result2(self, domain):
        self.request = DescribeDomainRecordsRequest()
        self.request.set_accept_format('json')
        # self.request.set_RRKeyWord(keyword)
        self.request.set_DomainName(domain)
        response = self.client.do_action_with_exception(self.request)
        jsonObj = json.loads(response.decode("UTF-8"))
        return jsonObj

    def run(self):
        while 1:
            value = GetIP().getLocalHost()
            for i in range(len(self.config['args'])):
                Type, domain = self.config['args'][i]['Type'], self.config['args'][i]['domain']
                for r in self.config['args'][i]['RR']:
                    domainIP = self.Get_Result(r, domain, Type)
                    if domainIP == value:
                        Logger().info('{}.{}:当前解析记录无异常'.format(r, domain))
                    elif domainIP == '127.0.0.1':
                        continue
                    else:
                        Logger().info('{}.{}:当前解析地址为：{}'.format(r, domain, domainIP))
                        Logger().info('{}.{}:域名当前解析地址与本地地址不致，开修改解析记录'.format(r, domain))
                        self.update_Domain_Record(RR=r, value=value, Type=Type, DomainName=domain)
            Logger().info('进程休眠中...')
            time.sleep(1800)


if __name__ == '__main__':
    AliDNS().run()
