# -*- coding: utf-8 -*-
'''
Created on 2017-11-28 18:34
---------
@summary: 基于搜狗微信取_biz
---------
@author: Boris
'''


import sys
sys.path.append('../')

import init
import utils.tools as tools
from utils.log import log
from db.oracledb import OracleDB
import ip_proxies

class WechatSogou():
    def __init__(self):
        self._db = OracleDB()

    def deal_null_biz(self):
        sql = 'select id, name, domain from TAB_IOPM_SITE t where classify = 2 and t.biz is null'
        accounts_info = self._db.find(sql)

        for account_info in accounts_info:
            print(account_info)
            _id = account_info[0]
            account = account_info[1]
            account_id = account_info[2]

            account_info = self.get_account_info(account_id, account)
            log.debug(tools.dumps_json(account_info))

            if account_info.get('__biz'):
                account = account or account_info.get('account')
                account_id = account_id or account_info.get('account_id')
                __biz = account_info.get('__biz') or ''

                sql = "update TAB_IOPM_SITE set name = '%s', domain = '%s', biz = '%s' where id = %s"%(account, account_id, __biz, _id)
                log.debug(sql)
                self._db.update(sql)

            elif not account_info.get('check_info'):
                log.debug('查无此公众号 ：%s'% account)

            tools.delay_time(5)



    def get_account_info(self, account_id = '', account = ''):
        keyword = account_id or account # 账号id优先
        keyword = keyword.lower()

        log.debug('search keywords ' + keyword)

        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": "IPLOC=CN1100; ld=4yllllllll2zj$kYlllllVo3$xklllllWT89eyllll9lllllRklll5@@@@@@@@@@; SUV=00E3555B7B7CC4C55A0AA8195254D871; CXID=150E3ABE3C35F9E55217835F7720E719; ABTEST=8|1510801558|v1; LSTMV=418%2C28; LCLKINT=2070; ad=8kllllllll2zRlPflllllVoSynYlllllWT89eyllllwlllll9Cxlw@@@@@@@@@@@; SUID=C5C47C7B1508990A000000005A0AA818; weixinIndexVisited=1; JSESSIONID=aaa-1KvS1lhung8pB9v8v; sct=20; PHPSESSID=k3c9psast34njs32vjm3pas3l1; SUIR=E8E851562D28732A6B711C802DECBC6F; SNUID=5657EFE99397CD9A1140DD249397E84D",
            "Host": "weixin.sogou.com"
        }

        proxies = ip_proxies.get_proxies()
        headers["User-Agent"] = ip_proxies.get_user_agent()

        url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_='%(keyword)
        html, request = tools.get_html_by_requests(url, headers = headers, proxies = proxies)

        # 公众号信息块
        regex = '<!-- a -->(.*?)<!-- z -->'
        account_blocks = tools.get_info(html, regex)

        regex = '<input type=text name="c" value="" placeholder="(.*?)" id="seccodeInput">'
        check_info = tools.get_info(html, regex, fetch_one = True)
        if check_info:
            log.debug('''取公众号列表 : %s
                         url : %s
                      '''%(check_info, url)
                      )

        account_info = {'check_info' : check_info}

        for account_block in account_blocks:
            regex = '<a.*?account_name.*?>(.*?)</a>'
            account = tools.get_info(account_block, regex, fetch_one = True)
            account = tools.del_html_tag(account)

            regex = '<label name="em_weixinhao">(.*?)</label>'
            account_id = tools.get_info(account_block, regex, fetch_one = True)

            regex = '<a.*?account_name.*?href="(.*?)">'
            account_url = tools.get_info(account_block, regex, fetch_one = True)
            account_url = account_url.replace('&amp;',"&")

            __biz = ''
            if account.lower() == keyword or account_id.lower() == keyword:
                # 取biz
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Host": "mp.weixin.qq.com",
                    "Connection": "keep-alive",
                    "Referer": "http://weixin.sogou.com/weixin?type=1&s_from=input&query=%E6%B3%B8%E5%B7%9E%E7%94%B5%E8%A7%86%E5%8F%B0&ie=utf8&_sug_=n&_sug_type_=",
                    "Cookie": "RK=XbmCLga7Pm; pgv_pvi=9492080640; noticeLoginFlag=1; ua_id=D8NYmIGpieSNub9rAAAAAGNz-Z1l4qe4x5WdelXsnmk=; xid=f3e1fb8a5fe8452b1d60a4059706017a; openid2ticket_opcqcjrNnRf62olc2Aj4PIU2hq9E=iNiYDe6xyIQ59zJxdOH0fmku4sXhFTq299CHyxYNJH8=; mm_lang=zh_CN; uin=o0564773807; skey=@Q46eRUFUE; pt2gguin=o0564773807; ptisp=cnc; ptcz=8deaf5ec9f0b3c27516ab6b735a6f3af99bc3517b922f52917b0ed5c6d82002f; o_cookie=564773807; pgv_info=ssid=s5664129956; pgv_pvid=8949522462; pac_uid=1_564773807; sig=h017174242e513ba3ec2450e63ac7a82981b57f85995f81aa47747b23e28ab077954627089b9d7fc947; pgv_si=s7924323328",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Cache-Control": "max-age=0",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
                    "Upgrade-Insecure-Requests": "1"
                }

                proxies = ip_proxies.get_proxies()
                headers["User-Agent"] = ip_proxies.get_user_agent()

                html, request = tools.get_html_by_requests(account_url, proxies = proxies)
                print(html)
                regex = 'var biz = "(.*?)"'

                __biz = tools.get_info(html, regex, fetch_one = True)

                log.debug('''
                    公众号名称          %s
                    公众号账号          %s
                    账号url             %s
                    __biz               %s
                    '''%(account, account_id, account_url, __biz))

                account_info = {
                    'account' : account,
                    'account_id' : account_id,
                    '__biz' : __biz,
                }

        return account_info


if __name__ == '__main__':
    wechat_sogo = WechatSogou()
    # wechat_sogo.get_account_info(account_id = '', account = 'lzw-lztv')
    wechat_sogo.deal_null_biz()