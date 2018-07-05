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
from base import constance

# 会过期
TOOKEN = 681408549
COOKIE = 'ua_id=qrHNGwhqyhUvNSApAAAAACVECa9T4D5IeDU1-Cmk1Co=; pgv_pvid=8019597375; pgv_pvi=5665655808; pt2gguin=o0564773807; RK=XbiAagaBbk; ptcz=6ed8395e60cfabf0b0f1a60eafcbe8d5c8299b2c8884399a4d8998f3f27ec7f0; mm_lang=zh_CN; pgv_si=s502258688; uuid=3b353ca2286e8d61b886d81b776343ba; ticket=729ddacb2934588d86ae5e7adce21c2fa0dbeeeb; ticket_id=gh_870ffb1242a7; cert=NUKpmB_enuhiRNswARfWUeFQQLfLf_2X; noticeLoginFlag=1; data_bizuin=2392640165; bizuin=2392713418; data_ticket=e6go5p+lAr0QBW6FSYTq2zl0vJi+OAJ90r3T4ZYI6O+tW1eSSzrRvt9AqSqiPT56; slave_sid=SGtxaW9HeWZ4ekJfMnpaX01NVFM3ZmFyYnB6NDlZaHVBODRVY2xRSUk4TktVNmIzUkpSOWRvTVdTRmRTTllOMzNvbkxuQ1djQ1VZRExZVnRQaDB3MzJoQ0duZTBrSEg2blJzaDRCbElLWVN4VlYzWGpQYUJERDJhVktCQ2NGeTVMTExjOFBGem05VkJRQndU; slave_user=gh_870ffb1242a7; xid=4fc1811533e10b28bc1751146274932a; openid2ticket_opcqcjrNnRf62olc2Aj4PIU2hq9E=TyHEfgMlWTd0+faLhhc19drEx0o1BEwP8MPyCwp2Dxo='

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
        log.debug('search keywords ' + keyword)
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

        log.debug('search keywords ' + __biz)

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
        # print(articles_json)

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
    biz = wechat_public_platform.get_biz(account_id = '', account = 'coder_life')
    print(biz)
    is_have_new_article = wechat_public_platform.is_have_new_article('MjM5NDEwNjUyNQ==')
    print(is_have_new_article)
