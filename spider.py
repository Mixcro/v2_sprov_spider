#!/usr/bin/env python3
import json
import requests
import sys


class Spider(object):

    def __init__(self, url, user, passwd):
        self.url = url if url[-1] == '/' else '%s/'%url
        self.user = user
        self.passwd = passwd
        self.session = requests.session()
        self.stat = {}
        self.accounts = {}
        self.stat_raw = {}
        self.accounts_raw = []

    def login(self):
        url = '%slogin'%self.url
        payload = {
            'username': self.user,
            'password': self.passwd
        }
        r = self.session.post(url, data=payload)
        if r.status_code == 200:
            if not json.loads(r.text)['success']:
                raise Exception(json.loads(r.text)['msg'])
        else:
            raise Exception("%s Network ERROR!" % r.status_code)

    def logout(self):
        url = '%ssprov-ui/restart'%self.url
        self.session.post(url)
        url = '%slogout/'%self.url
        self.session.get(url)

    def get_server_status(self):
        url = '%sserver/status'%self.url
        r = self.session.post(url)
        self.stat_raw = json.loads(r.text)['obj']
        stat_items = ['status',
                      'uptime',
                      'hostname',
                      'cpu_usage',
                      'memory_usage',
                      'disk_usage',
                      'load',
                      'interface_stat',
                      'bandwidth']
        for i in range(0, len(stat_items)):
            self.stat[stat_items[i]] = self.stat_raw[i]['value']

    def get_accounts(self):
        url = '%sv2ray/config'%self.url
        r = self.session.post(url)
        accounts = json.loads(json.loads(r.text)['msg'])['inbounds']
        for account in accounts:
            self.accounts[account['tag']] = {
                'protocol': account['protocol'],
                'port': account['port'],
                'enable': account['enable'],
                'downlink': account['downlink'],
                'uplink': account['uplink'],
                'id': account['settings']['clients'][0]['id']
            }

    def ctl_disable_account(self, account_tag):
        url = '%sv2ray/inbound/disable'%self.url
        port = self.accounts[account_tag]['port']
        if self.accounts[account_tag]['enable']:
            r = self.session.post(url, data={'port': port})
            if r.status_code == 200:
                if not json.loads(r.text)['success']:
                    raise Exception(json.loads(r.text)['msg'])
            else:
                raise Exception("%s Network ERROR!" % r.status_code)

    def ctl_enable_account(self, account_tag):
        url = '%sv2ray/inbound/enable'%self.url
        port = self.accounts[account_tag]['port']
        if not self.accounts[account_tag]['enable']:
            r = self.session.post(url, data={'port': port})
            if r.status_code == 200:
                if not json.loads(r.text)['success']:
                    raise Exception(json.loads(r.text)['msg'])
            else:
                raise Exception("%s Network ERROR!"%r.status_code)

    def ctl_reset_account(self, account_tag):
        url = '%sv2ray/inbound/resetTraffic'%self.url
        port = self.accounts[account_tag]['port']
        r = self.session.post(url, data={'port': port})
        if r.status_code == 200:
            if not json.loads(r.text)['success']:
                raise Exception(json.loads(r.text)['msg'])
        else:
            raise Exception("%s Network ERROR!"%r.status_code)

    def print_server_status(self):
        print(json.dumps(self.stat, ensure_ascii=False, indent=1))

    def print_accounts(self):
        print(json.dumps(self.accounts, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    # init_config(config_path='./config.json'):
    with open('./config.json', 'r') as f:
        config = json.load(f)
    url = config['server']['server_url']
    user = config['server']['user']
    passwd = config['server']['password']

    # CUI
    test_spider = Spider(url, user, passwd)
    if len(sys.argv) > 1:
        if sys.argv[1] == 'reset':
            try:
                test_spider.login()
                test_spider.get_accounts()
                account_list = test_spider.accounts.keys() if sys.argv[2] == 'all' else ['inbound-%s'%sys.argv[2]]
                for account in account_list:
                    test_spider.ctl_enable_account(account)
                    test_spider.ctl_reset_account(account)
                    print('RESET %s'%account)
                test_spider.logout()
            except Exception as e:
                test_spider.logout()
                raise e
        elif sys.argv[1] == 'check':

            def check_traffic(account, downlink, uplink):
                if account[8:] in config['traffic_limit']['accounts'].keys():
                    limit = config['traffic_limit']['accounts'][account[8:]]
                else:
                    limit = config['traffic_limit']['default_limit']
                return False if uplink + downlink < limit or limit == 0 else True

            try:
                test_spider.login()
                test_spider.get_accounts()
                account_list = test_spider.accounts.keys() if sys.argv[2] == 'all' else ['inbound-%s'%sys.argv[2]]
                for account in account_list:
                    account_downlink = test_spider.accounts[account]['downlink']
                    account_uplink = test_spider.accounts[account]['uplink']
                    if check_traffic(account, account_downlink, account_uplink):
                        test_spider.ctl_disable_account(account)
                    print('TRAFFIC CHECK %s: uplink %.3f G | downlink %.3f G' %(account,
                                                                                account_uplink/1024**3,
                                                                                account_downlink/1024**3))
                test_spider.logout()
            except Exception as e:
                test_spider.logout()
                raise e
    else:
        print('''
USAGE: ./spider.py [cmd] [target]
    [cmd]: reset, check
    [target]: all, [user port]
EXAMPLE:
    ./spider.py reset all      # reset all user traffic
    ./spider.py check all      # check all user traffic and auto ban overload user
    ./spider.py reset 59603    # reset user's traffic whois port is 59603''')
