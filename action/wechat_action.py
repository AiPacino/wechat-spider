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

SLEEP_TIME = 2000 # 2000 毫秒

class WechatAction():
    def __init__(self):
        self._wechat_service = WechatService()

    def __open_next_account(self, __biz):
        '''
        @summary: 跳转到下一个公众号
        ---------
        @param __biz:
        ---------
        @result:
        '''

        url = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s==#wechat_webview_type=1&wechat_redirect'%__biz
        nextAccount = "<script>setTimeout(function(){window.location.href='%s';},%d);</script>"%(url, SLEEP_TIME)

        return nextAccount

    def __open_next_page(self, __biz, pass_ticket, appmsg_token, offset = 10):
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

        nextPage = "<script>setTimeout(function(){window.location.href='%s';},%d);</script>"%(url, SLEEP_TIME)

        return nextPage

    def __parse_account_info(self, data):
        pass

    def __parse_article_list(self, article_list):
        '''
        @summary: 解析文章列表
        ---------
        @param article_list: 文章列表信息 str
        {
            "list":[
                {
                    "comm_msg_info":{
                        "id":1000000513,
                        "type":49,
                        "datetime":1511354167,
                        "fakeid":"3082125093",
                        "status":2,
                        "content":""
                    },
                    "app_msg_ext_info":{
                        "title":"Python 内存优化",
                        "digest":"实际项目中，pythoner更加关注的是Python的性能问题。本文，关注的是Python的内存优化，一般说来，如果不发生内存泄露，运行在服务端的Python代码不用太关心内存，但是如果运行在客户端，那还是有优化的必要。",
                        "content":"",
                        "fileid":505083208,
                        "content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzA4MjEyNTA5Mw==&amp;mid=2652566858&amp;idx=1&amp;sn=d2a76f4a601f94d8acc7b436d18e9648&amp;chksm=8464dd00b313541684c14f974325ea6ae725ffc901fd9888cc00d1acdd13619de3297a5d9a35&amp;scene=27#wechat_redirect",
                        "source_url":"http:\/\/www.cnblogs.com\/xybaby\/p\/7488216.html",
                        "cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/fhujzoQe7TpODTuicia4geCiaIj1AbZwVQQVbRHy3FhzwMHEvCvtzXVicHTaPEu8jZ2pgkCAgBqEHugYMvzg3tpoww\/0?wx_fmt=jpeg",
                        "subtype":9,
                        "is_multi":1,
                        "multi_app_msg_item_list":[
                            {
                                "title":"面向对象：With the wonder of your love, the sun above always shines",
                                "digest":"With the wonder of your love, the sun above always shines",
                                "content":"",
                                "fileid":505083209,
                                "content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzA4MjEyNTA5Mw==&amp;mid=2652566858&amp;idx=2&amp;sn=97f223783da7748080f8103654447c99&amp;chksm=8464dd00b313541601938565a41487ea76209331fd6f4c8996a2ff5572f4fd465de9fa4cbaac&amp;scene=27#wechat_redirect",
                                "source_url":"https:\/\/mp.weixin.qq.com\/s\/_uD9jY4nXQQ6CtA__dsN8w?scene=25#wechat_redirect",
                                "cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/fhujzoQe7TpODTuicia4geCiaIj1AbZwVQQ5ukvwH1GPq5zlWxv05WvRiaw6BiaeyGRD1w17nAPGTlQgEvvDuZnB9HA\/0?wx_fmt=jpeg",
                                "author":"",
                                "copyright_stat":101,
                                "del_flag":1
                            }
                        ],
                        "author":"",
                        "copyright_stat":100,
                        "del_flag":1
                    }
                }
            ]
        }
        ---------
        @result:
        '''

        # log.debug(tools.dumps_json(article_list))
        article_list = tools.get_json(article_list)

        article_list = article_list.get('list', [])
        for article in article_list:
            log.debug(tools.dumps_json(article))
            release_time = article.get('comm_msg_info', {}).get('datetime')
            release_time = tools.timestamp_to_date(release_time)

            # 微信公众号每次可以发多个图文消息
            # 第一个图文消息
            app_msg_ext_info = article.get('app_msg_ext_info', {})
            title = app_msg_ext_info.get('title')
            summary = app_msg_ext_info.get('digest')
            url = app_msg_ext_info.get('content_url').replace('\\', '').replace('amp;', '')
            source_url = app_msg_ext_info.get('source_url').replace('\\', '')  # 引用的文章链接
            cover = app_msg_ext_info.get('cover').replace('\\', '')
            author = app_msg_ext_info.get('author')
            if url: # 被发布者删除的文章 无url和其他信息， 此时取不到mid 且不用入库
                article_id = int(tools.get_param(url, 'mid'))

                # 入库
                self._wechat_service.add_article_info(release_time, title, summary, url, source_url, cover, author, article_id)

            # 同一天附带的图文消息
            multi_app_msg_item_list = app_msg_ext_info.get('multi_app_msg_item_list')
            for multi_app_msg_item in multi_app_msg_item_list:
                title = multi_app_msg_item.get('title')
                summary = multi_app_msg_item.get('digest')
                url = multi_app_msg_item.get('content_url').replace('\\', '').replace('amp;', '')
                source_url = multi_app_msg_item.get('source_url').replace('\\', '') # 引用的文章链接
                cover = multi_app_msg_item.get('cover').replace('\\', '')
                author = multi_app_msg_item.get('author')
                if url: # 被发布者删除的文章 无url和其他信息， 此时取不到mid 且不用入库
                    article_id = int(tools.get_param(url, 'mid'))

                    # 入库
                    self._wechat_service.add_article_info(release_time, title, summary, url, source_url, cover, author, article_id)


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
        if 'action=home' in req_url:
            regex = "msgList = '(.*?})';"
            article_list = tools.get_info(data, regex, fetch_one = True)
            article_list = article_list.replace('&quot;', '"')
            self.__parse_article_list(article_list)

            #判断是否还有更多文章 没有跳转到下个公众号，有则下拉显示更多
            regex = "can_msg_continue = '(\d)'"
            can_msg_continue = tools.get_info(data, regex, fetch_one = True)
            if can_msg_continue == '0':# 无更多文章
                # 跳转到下一个公众号 TODO
                pass
            else:
                # 以下是拼接下拉显示更多的历史文章 跳转
                # 取appmsg_token 在html中
                regex = 'appmsg_token = "(.*?)";'
                appmsg_token = tools.get_info(data, regex, fetch_one = True)

                # 取其他参数  在url中
                __biz = tools.get_param(req_url, '__biz')
                pass_ticket = tools.get_param(req_url, 'pass_ticket')

                # 返回跳转到下一页
                return self.__open_next_page(__biz, pass_ticket, appmsg_token)

        else:# json格式
            data = tools.get_json(data)
            article_list = data.get('general_msg_list', {})
            self.__parse_article_list(article_list)

            #判断是否还有更多文章 没有跳转到下个公众号，有则下拉显示更多
            can_msg_continue = data.get('can_msg_continue')
            if not can_msg_continue: # 无更多文章
                # 跳转到下一个公众号 TODO
                pass
            else:
                # 以下是拼接下拉显示更多的历史文章 跳转
                # 取参数  在url中
                __biz = tools.get_param(req_url, '__biz')
                pass_ticket = tools.get_param(req_url, 'pass_ticket')
                appmsg_token = tools.get_param(req_url, 'appmsg_token')

                # 取offset 在json中
                offset = data.get('next_offset', 0)

                # 返回跳转到下一页
                return self.__open_next_page(__biz, pass_ticket, appmsg_token, offset)

    def get_article_info(self, data, req_url):
        log.debug('获取文章信息')

    def get_read_watched_count(self, data, req_url):
        log.debug('获取观看和评论量')
        pass

    def get_comment(self, data, req_url):
        log.debug('获取评论信息')
        pass

    def deal_request(self, name):
        web.header('Content-Type','text/html;charset=UTF-8')

        data_json = json.loads(json.dumps(web.input()))
        data = data_json.get('data') # data为str
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

        elif name == 'get_article_info':
            reponse = self.get_article_info(data, req_url)

        elif name == 'get_read_watched_count':
            reponse = self.get_read_watched_count(data, req_url)

        elif name == 'get_comment':
            reponse = self.get_comment(data, req_url)

        # log.debug('''
        #     ---------reponse---------
        #     %s'''%reponse)

        return reponse # 此处返回''空字符串  不会触发node-js http 的回调

    def GET(self, name):
        return self.deal_request(name)

    def POST(self, name):
        return self.deal_request(name)


if __name__ == '__main__':
    pass

    #TODO
    # 文章跳转
