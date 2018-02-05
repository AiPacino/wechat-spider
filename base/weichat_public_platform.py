# -*- coding: utf-8 -*-
'''
Created on 2017-11-28 18:34
---------
@summary: 基于微信公众平台取_biz及检查今日是否发文
---------
@author: Boris
'''


import sys
sys.path.append('../')

import init
import utils.tools as tools
from utils.log import log
import random
import constance

# 会过期
TOOKEN = 2103841294
COOKIE = 'pgv_pvi=5528556544; RK=XamCagaLPm; pac_uid=1_564773807; gaduid=5a66dad580d5b; pt2gguin=o0564773807; ptcz=e30ece25da8051fa18d7817693d6ad2b88c9961b4e54f1138a8c8f73883d2fef; pgv_pvid=6169397048; o_cookie=564773807; ua_id=CJCj6o73zn173CMUAAAAAHJD5fGqeruUXpS_2f5xMas=; mm_lang=zh_CN; noticeLoginFlag=1; p_o2_uin=564773807; pgv_si=s4708166656; uuid=5da383467cc4a47719b7d7a71b0e4e46; ticket=61db0e5c0e14130718f4a673bff454de66660c5c; ticket_id=gh_870ffb1242a7; cert=T8J7ocwh3ADLXJ1S9dk8KJSLSATIHmrx; data_bizuin=2392640165; bizuin=2392713418; data_ticket=O7VD9Eq4SY/x586Ngf66ciUeRrONhqQT8NgwnXhGfG3Ib8h+mq1zG9BFwbjFMGi2; slave_sid=T21USXBWWTNScl90U3JpN0V0N3JKVGJ1QXE1WFNFU1p5bk9fNl8yTkh5bDNfWWt5cldiQjVTRmplNnRIbmt3MGhDV2RvX2RqRm8wTGpVWjhiVkpNT0xjOGlBc1hRRVNkc0dLU3FJMl83R3Q4cXVnaFQ1ZzN5a3dMQ0hPQXNLTFJGMlA3ekJSekRRNTZRWm9H; slave_user=gh_870ffb1242a7; xid=e714db65138e653bf39efae55e12a553; openid2ticket_opcqcjrNnRf62olc2Aj4PIU2hq9E=zPpw5rBj+i2dt5o2mnscwloF2BtqpMum7t+AJvMCXFU='

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&isMul=1&isNew=1&lang=zh_CN&token=2103841294",
    "Cookie": COOKIE,
    "Host": "mp.weixin.qq.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest"
}

class WechatPublicPlatform():
    def __init__(self):
        pass

    def get_biz(self, account_id = '', account = ''):
        '''
        @summary: 获取公众号的__biz参数
        ---------
        @param account_id:
        @param account:
        ---------
        @result:
        '''

        keyword = account_id or account # 账号id优先
        __biz = ''

        url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
        params = {
            "count": "5",
            "begin": "0",
            "action": "search_biz",
            "lang": "zh_CN",
            "random": str(random.random()) + str(random.randint(1,9)),
            "ajax": "1",
            "token": TOOKEN,
            "f": "json",
            "query": keyword
        }

        account_json = tools.get_json_by_requests(url, params = params, headers = HEADERS)

        #TOOKEN过期 返回 {'base_resp': {'ret': 200003, 'err_msg': 'invalid session'}}
        account_list = account_json.get("list", [])
        for account_info in account_list:
            if account_info.get('nickname').lower() == keyword.lower() or account_info.get('alias').lower() == keyword.lower():
                __biz = account_info.get('fakeid', '')
                break

        log.debug('''
            公众号名称          %s
            公众号账号          %s
            __biz               %s
            '''%(account, account_id, __biz))

        return __biz

    def is_have_new_article(self, __biz):
        '''
        @summary: 检查公众号今日是否发文
        ---------
        @param account_id:
        @param account:
        ---------
        @result:
        '''

        url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
        params = {
            "lang": "zh_CN",
            "token": TOOKEN,
            "query": "",
            "f": "json",
            "count": "5",
            "action": "list_ex",
            "ajax": "1",
            "type": "9",
            "fakeid": __biz,
            "random": str(random.random()) + str(random.randint(1,9)),
            "begin": "0"
        }

        articles_json = tools.get_json_by_requests(url, params = params, headers = HEADERS)

        # TOOLEN 过期 返回 {'base_resp': {'err_msg': 'invalid csrf token', 'ret': 200040}}
        article_list = articles_json.get('app_msg_list', [])
        for article in article_list:
            release_time = article.get('update_time')
            release_time = tools.timestamp_to_date(release_time)
            log.debug("最近发文时间 %s"%release_time)

            if release_time >= tools.get_current_date('%Y-%m-%d'):
                return constance.UPDATE
            else:
                return constance.NOT_UPDATE
        else:
            return constance.ERROR



if __name__ == '__main__':
    wechat_public_platform = WechatPublicPlatform()
    # biz = wechat_public_platform.get_biz(account_id = '', account = 'coder_life')
    # print(biz)
    is_have_new_article = wechat_public_platform.is_have_new_article('MjM5NDEwNjUyNQ==')
    print(is_have_new_article)
