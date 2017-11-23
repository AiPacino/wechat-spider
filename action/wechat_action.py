# -*- coding: utf-8 -*-
'''
Created on 2017-09-22 15:55
---------
@summary:
---------
@author: Boris
'''
import sys
sys.path.append('..')

from utils.log import log
import utils.tools as tools
import web
import json
from service.wechat_service import WechatService
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变print标准输出的默认编码

class WechatAction():
    def __init__(self):
        pass

    def open_next_account(self, __biz):
        '''
        @summary: 跳转到下一个公众号
        ---------
        @param __biz:
        ---------
        @result:
        '''

        url = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s==#wechat_webview_type=1&wechat_redirect'%__biz
        nextAccount = "<script>setTimeout(function(){window.location.href='" + url + "';},2000);</script>"

        return nextAccount

    def open_next_page(self, __biz, pass_ticket, appmsg_token, offset = 10):
        '''
        @summary: 跳转到历史文章
        ---------
        @param __biz:
        @param pass_ticket:
        @param appmsg_token:
        @param offset:
        ---------
        @result:
        '''
        url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz={__biz}&f=json&offset={offset}&count=10&is_ok=1&scene=124&uin=777&key=777&pass_ticket={pass_ticket}&wxtoken=&appmsg_token={appmsg_token}&x5=0&f=json'.format(__biz = __biz, offset = offset, pass_ticket = pass_ticket, appmsg_token = appmsg_token)

        log.debug('''
            nextPageUrl : %s
            '''%url)

        nextPage = "<script>setTimeout(function(){window.location.href='" + url + "';},2000);</script>"

        tools.delay_time(5)
        return nextPage

    def __parse_article_content(self, article_list):
        log.debug(tools.dumps_json(article_list))
        pass

    def get_article_list(self, data, req_url):
        '''
        @summary: 获取文章列表
        分为两种
            1、第一次查看历史消息 返回的是html格式 包含公众号信息
            2、下拉显示更多时 返回json格式
        但是文章列表都是json格式 且合适相同
        抓取思路：
        1、如果是第一种格式，直接解析文章内容，拼接下一页json格式的地址
        2、如果是第二种格式，
        ---------
        @param data:
        ---------
        @result:
        '''
        # 取html格式里的文章列表
        regex = "msgList = '(.*?})';"
        article_list = tools.get_info(data, regex, fetch_one = True)
        article_list = article_list.replace('&quot;', '"')
        if article_list:
            log.debug(req_url)
            self.__parse_article_content(article_list)

            # 以下是拼接下拉显示更多的历史文章 跳转
            # 取appmsg_token 在html中
            regex = 'appmsg_token = "(.*?)";'
            appmsg_token = tools.get_info(data, regex, fetch_one = True)

            # 取其他参数  在url中
            __biz = tools.get_param(req_url, '__biz')
            pass_ticket = tools.get_param(req_url, 'pass_ticket')

            # 返回跳转到下一页
            return self.open_next_page(__biz, pass_ticket, appmsg_token)

        else:# json格式
            data = tools.get_json(data)
            article_list = data.get('general_msg_list', {})
            self.__parse_article_content(article_list)

            # 以下是拼接下拉显示更多的历史文章 跳转
            # 取参数  在url中
            __biz = tools.get_param(req_url, '__biz')
            pass_ticket = tools.get_param(req_url, 'pass_ticket')
            appmsg_token = tools.get_param(req_url, 'appmsg_token')

            # 取offset 在json中
            offset = data.get('next_offset', 0)

            # 返回跳转到下一页
            return self.open_next_page(__biz, pass_ticket, appmsg_token, offset)

    def get_read_watched_count(self, data):
        pass

    def get_comment(self, data):
        pass

    def deal_request(self, name):
        web.header('Content-Type','text/html;charset=UTF-8')

        data_json = json.loads(json.dumps(web.input()))
        data = data_json.get('data')
        req_url = data_json.get('req_url')

        # log.debug('''
        #     method : %s
        #     data   ：%s
        #     '''%(name, data))

        log.debug('''
            method : %s
            url   ：%s
            '''%(name, req_url))

        reponse = ''
        if name == 'get_article_list':
            reponse = self.get_article_list(data, req_url)

        elif name == 'get_read_watched_count':
            reponse = self.get_read_watched_count(data)

        elif name == 'get_comment':
            reponse = self.get_comment(data)

        log.debug('''
            ---------reponse---------
            %s'''%reponse)

        return reponse # 此处返回''空字符串  不会触发node-js http 的回调

    def GET(self, name):
        return self.deal_request(name)

    def POST(self, name):
        return self.deal_request(name)


if __name__ == '__main__':

    # wechat = WechatAction()
    # nextAccount = wechat.open_next_account('MzIzOTU0NTQ0MA')
    # print(nextAccount)
#     http://0.0.0.0:6210/
# 60084 CP Server Thread-1 2017-11-22 19:29:16 wechat_action.py get_article_list [line:98] DEBUG /mp/profile_ext?action=home&__biz=MzIxMzA3OTc2NQ==&scene=124&devicetype=iOS11.1.1&version=16051620&lang=zh_CN&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=0Q7RAmYVQ8N42EmYcB1P1c7pQzxhcYTwIku2URbwDQYMzbFge%2FxGthMytCGKyn%2FV&wx_header=1
# 60084 CP Server Thread-1 2017-11-22 19:29:16 wechat_action.py get_article_list [line:108] DEBUG html
# 60084 CP Server Thread-1 2017-11-22 19:29:16 tools.py dumps_json [line:403] ERROR <action.wechat_action.WechatAction object at 0x000002894F48E0B8> is not JSON serializable
# 60084 CP Server Thread-1 2017-11-22 19:29:16 wechat_action.py open_next_page [line:66] DEBUG {'__biz': <action.wechat_action.WechatAction object at 0x000002894F48E0B8>,
#  'action': 'getmsg',
#  'appmsg_token': '0Q7RAmYVQ8N42EmYcB1P1c7pQzxhcYTwIku2URbwDQYMzbFge%2FxGthMytCGKyn%2FV',
#  'count': '10',
#  'f': 'json',
#  'is_ok': '1',
#  'key': '777',
#  'offset': '932_Qi3Ue8ArOnVs0bAlXStFGFSeCiKxw_vbDKBCGg~~',
#  'pass_ticket': 'MzIxMzA3OTc2NQ',
#  'scene': '124',
#  'uin': '777',
#  'wxtoken': '',
#  'x5': '0'}
# 60084 CP Server Thread-1 2017-11-22 19:29:16 wechat_action.py open_next_page [line:69] DEBUG https://mp.weixin.qq.com/mp/profile_ext?wxtoken=&action=getmsg&__biz=<action.wechat_action.WechatAction object at 0x000002894F48E0B8>&count=10&is_ok=1&scene=124&appmsg_token=0Q7RAmYVQ8N42EmYcB1P1c7pQzxhcYTwIku2URbwDQYMzbFge%2FxGthMytCGKyn%2FV&key=777&pass_ticket=MzIxMzA3OTc2NQ&uin=777&offset=932_Qi3Ue8ArOnVs0bAlXStFGFSeCiKxw_vbDKBCGg~~&f=json&x5=0
# 60084 CP Server Thread-1 2017-11-22 19:29:16 wechat_action.py deal_request [line:158] DEBUG reponse:
# 127.0.0.1:57028 - - [22/Nov/2017 19:29:16] "HTTP/1.1 POST /wechat/get_article_list" - 200 OK
# [Cancelled]

    url = '/mp/profile_ext?action=home&__biz=MzIxMzA3OTc2NQ==&scene=124&devicetype=iOS11.1.1&version=16051620&lang=zh_CN&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=0Q7RAmYVQ8N42EmYcB1P1c7pQzxhcYTwIku2URbwDQYMzbFge%2FxGthMytCGKyn%2FV&wx_header=1'
    __biz = tools.get_param(url, '__biz')
    print(__biz)

    pass_ticket = '932_Qi3Ue8ArOnVs0bAlXStFGFSeCiKxw_vbDKBCGg~~'
    appmsg_token = '0Q7RAmYVQ8N42EmYcB1P1c7pQzxhcYTwIku2URbwDQYMzbFge%2FxGthMytCGKyn%2FV'
    offset = 10
    params = {
            "action": "getmsg",
            "is_ok": "1",
            "pass_ticket": pass_ticket,
            "scene": "124",
            "key": "777",
            "__biz": __biz,
            "f": "json",
            "x5": "0",
            "appmsg_token": appmsg_token,
            "count": "10",
            "uin": "777",
            "offset": offset,
            "wxtoken": ""
        }
    log.debug(tools.dumps_json(params))
    url = 'https://mp.weixin.qq.com/mp/profile_ext'
    url = tools.joint_url(url, params)

    print(url)