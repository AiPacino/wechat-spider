# -*- coding: utf-8 -*-
'''
Created on 2017-11-28 18:34
---------
@summary: 基于搜狗微信取_biz及检查今日是否发文
---------
@author: Boris
'''


import sys
sys.path.append('../')

import init
import utils.tools as tools
from utils.log import log
import ip_proxies
import constance

class WechatSogou():
    def __init__(self):
        pass

    def __get_account_blocks(self, account_id = '', account = ''):
        keyword = account_id or account # 账号id优先

        log.debug('search keywords ' + keyword)

        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": "IPLOC=CN1100; ld=4yllllllll2zj$kYlllllVo3$xklllllWT89eyllll9lllllRklll5@@@@@@@@@@; SUV=00E3555B7B7CC4C55A0AA8195254D871; CXID=150E3ABE3C35F9E55217835F7720E719; ABTEST=8|1510801558|v1; LSTMV=418%2C28; LCLKINT=2070; ad=8kllllllll2zRlPflllllVoSynYlllllWT89eyllllwlllll9Cxlw@@@@@@@@@@@; SUID=C5C47C7B1508990A000000005A0AA818; weixinIndexVisited=1; JSESSIONID=aaa-1KvS1lhung8pB9v8v; sct=20; PHPSESSID=k3c9psast34njs32vjm3pas3l1; SUIR=E8E851562D28732A6B711C802DECBC6F; seccodeErrorCount=1|Tue, 28 Nov 2017 11:11:05 GMT; SNUID=A1A0181864613C6A610582E26446EC9A; successCount=1|Tue, 28 Nov 2017 11:11:22 GMT",
            "Host": "weixin.sogou.com"
        }

        # proxies = ip_proxies.get_proxies()
        # headers["User-Agent"] = ip_proxies.get_user_agent()

        url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_='%(keyword)
        html, request = tools.get_html_by_requests(url, headers = headers)#, proxies = proxies)

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

            return ''

        for account_block in account_blocks:
            regex = '<a.*?account_name.*?>(.*?)</a>'
            account = tools.get_info(account_block, regex, fetch_one = True)
            account = tools.del_html_tag(account)

            regex = '<label name="em_weixinhao">(.*?)</label>'
            account_id = tools.get_info(account_block, regex, fetch_one = True)

            if account.lower() == keyword.lower() or account_id.lower() == keyword.lower():
                return account_block


    def get_biz(self, account_id = '', account = ''):
        '''
        @summary: 获取公众号的__biz参数
        ---------
        @param account_id:
        @param account:
        ---------
        @result:
        '''

        account_block = self.__get_account_blocks(account_id, account)

        regex = '<a.*?account_name.*?>(.*?)</a>'
        account = tools.get_info(account_block, regex, fetch_one = True)
        account = tools.del_html_tag(account)

        regex = '<label name="em_weixinhao">(.*?)</label>'
        account_id = tools.get_info(account_block, regex, fetch_one = True)

        regex = '<a.*?account_name.*?href="(.*?)">'
        account_url = tools.get_info(account_block, regex, fetch_one = True)
        account_url = account_url.replace('&amp;',"&")

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

        # proxies = ip_proxies.get_proxies()
        # headers["User-Agent"] = ip_proxies.get_user_agent()

        html, request = tools.get_html_by_requests(account_url)#, proxies = proxies)
        regex = '<div class="weui_cells_tips">(.*?)</div>'
        check_info = tools.get_info(html, regex, fetch_one = True)
        if check_info:
            log.debug('''取公众号文章页 : %s
                         url : %s
                      '''%(check_info, account_url)
                      )
            return ''

        regex = 'var biz = "(.*?)"'

        __biz = tools.get_info(html, regex, fetch_one = True)

        log.debug('''
            公众号名称          %s
            公众号账号          %s
            账号url             %s
            __biz               %s
            '''%(account, account_id, account_url, __biz))

        return __biz

    def is_have_new_article(self, account_id = '', account = ''):
        '''
        @summary: 检查公众号今日是否发文
        ---------
        @param account_id:
        @param account:
        ---------
        @result:
        '''

        account_block = self.__get_account_blocks(account_id, account)
        regex = "timeConvert\('(\d*?)'\)"
        release_time = tools.get_info(account_block, regex, fetch_one = True)

        if release_time:
            release_time = int(release_time)
            release_time = tools.timestamp_to_date(release_time)
            log.debug("最近发文时间 %s"%release_time)

            if release_time >= tools.get_current_date('%Y-%m-%d'):
                return constance.UPDATE
            else:
                return constance.NOT_UPDATE

        else:
            return constance.ERROR



if __name__ == '__main__':
    wechat_sogo = WechatSogou()
    __biz = wechat_sogo.get_biz(account_id = '', account = 'coder_life')
    print(__biz)
    is_have_new_article = wechat_sogo.is_have_new_article(account_id = '', account = 'kaishustorynj')
    print(is_have_new_article)

