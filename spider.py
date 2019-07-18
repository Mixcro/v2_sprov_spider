#!/usr/bin/env python3
import json
import requests
import sys


### config ###
url = 'http://meow.earth:10000'
user = 'mixcro'
passwd = 'passwd'
month_traffic_limit = 64*1024**3  # 单用户月流量限制，单位是byte



class Spider(object):

    def __init__(self, url, user, passwd):
        if url[-1] == '/':
            self.url = url
        else:
            self.url = '%s/'%url
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
    test_spider = Spider(url, user, passwd)
    if len(sys.argv) > 1:
        if sys.argv[1] == 'reset':
            if sys.argv[2] == 'all':
                try:
                    test_spider.login()
                    test_spider.get_accounts()
                    for account in test_spider.accounts.keys():
                        test_spider.ctl_enable_account(account)
                        test_spider.ctl_reset_account(account)
                    test_spider.logout()
                except Exception as e:
                    test_spider.logout()
                    raise(e)
            else:
                try:
                    test_spider.login()
                    test_spider.get_accounts()
                    test_spider.ctl_enable_account('inbound-%s' % sys.argv[2])
                    test_spider.ctl_reset_account('inbound-%s'%sys.argv[2])
                    test_spider.logout()
                except Exception as e:
                    test_spider.logout()
                    raise(e)
        elif sys.argv[1] == 'check':
            if sys.argv[2] == 'all':
                try:
                    test_spider.login()
                    test_spider.get_accounts()
                    for account in test_spider.accounts.keys():
                        if test_spider.accounts[account]['downlink']+test_spider.accounts[account][
                                                         'uplink']>month_traffic_limit:
                            test_spider.ctl_disable_account(account)
                    test_spider.logout()
                except Exception as e:
                    test_spider.logout()
                    raise(e)
            else:
                try:
                    test_spider.login()
                    test_spider.get_accounts()
                    account = 'inbound-%s'%sys.argv[2]
                    if test_spider.accounts[account]['downlink'] + test_spider.accounts[account][
                                                     'uplink'] > month_traffic_limit:
                        test_spider.ctl_disable_account(account)
                    test_spider.logout()
                except Exception as e:
                    test_spider.logout()
                    raise(e)
    else:
        print(
            '''
USAGE: ./spider.py [cmd] [target]
    [cmd]: reset, check
    [target]: all, [user port]
EXAMPLE:
    ./spider.py reset all      # reset all user traffic
    ./spider.py check all      # check all user traffic and auto ban overload user
    ./spider.py reset 59603    # reset user's traffic whois port is 59603
            '''
        )
