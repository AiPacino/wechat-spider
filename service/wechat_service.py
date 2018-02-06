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

import collections

from utils.log import log
import utils.tools as tools
from db.oracledb import OracleDB
from db.elastic_search import ES
from base.wechat_sogou import WechatSogou
from base.wechat_public_platform import WechatPublicPlatform
from base import constance
import random

SIZE = 100
TIME_INTERVAL = 24 * 60 * 60

CHECK_NEW_ARTICLE = True  # 有新发布的文章才爬取

class WechatService():
    _db = OracleDB()
    _es = ES()
    _wechat_sogou = WechatSogou()
    _wechat_public_platform = WechatPublicPlatform()

    _todo_accounts = collections.deque()
    _rownum = 1

    _is_done = False # 做完一轮
    _is_all_done = False # 所有账号当日发布的消息均已爬取

    # wechat_sogou 最后没被封的时间
    _wechat_sogou_enable = True
    _wechat_sogou_last_unenable_time = tools.get_current_timestamp()

    # wechat_public_platform 最后没被封的时间
    _wechat_public_platform_enable = True
    _wechat_public_platform_last_unenable_time = tools.get_current_timestamp()

    def __init__(self):
        pass

    def __load_todo_account(self):
        if not WechatService._todo_accounts:
            sql = ''
            if not WechatService._is_all_done:
                sql = '''
                    select *
                       from (select rownum r, t.id, t.domain, t.biz, t.name
                               from TAB_IOPM_SITE t
                              where t.biz is not null and mointor_status = 701 and (today_msg is null or today_msg = 0) and rownum < {size})
                      where r >= {rownum}
                    '''.format(rownum = WechatService._rownum, size = WechatService._rownum + SIZE)
            else: # 今日公众号发布的新文章均已爬取
                sql = '''
                    select *
                       from (select rownum r, t.id, t.domain, t.biz, t.name
                               from TAB_IOPM_SITE t
                              where t.biz is not null and mointor_status = 701 and rownum < {size})
                      where r >= {rownum}
                    '''.format(rownum = WechatService._rownum, size = WechatService._rownum + SIZE)

            print(sql)
            results = WechatService._db.find(sql)
            if not results:
                if WechatService._rownum == 1:
                    # 今日公众号发布的新文章均已爬取，爬虫休息，明日再爬
                    WechatService._is_all_done = True  # 为了WeichatAction 设置休眠时间用
                    # 取下一天的公众号
                    self.__load_todo_account()

                else:
                    WechatService._is_done = True
                    WechatService._rownum = 1
                    self.__load_todo_account()

            else:
                WechatService. _todo_accounts = collections.deque(results) #  转为队列
                WechatService._rownum += SIZE

    def is_have_new_article(self, account_id, account_name, __biz):
        '''
        @summary: 检查是否有新发布的文章
        ---------
        @param account_id:
        @param __biz:
        ---------
        @result:
        '''

        result = ''
        if WechatService._wechat_sogou_enable: # 搜狗微信可用
            result = WechatService._wechat_sogou.is_have_new_article(account_id = account_id, account = account_name)
            if result == constance.UPDATE:
                # 有新发布的文章 抓取
                pass

            elif result == constance.NOT_UPDATE:
                # 无新发布的文章 pass
                pass

            elif result == constance.ERROR:
                pass

            elif result == constance.VERIFICATION_CODE:
                # 被封了 请求失败 记录下失败时间
                WechatService._wechat_sogou_enable = False
                WechatService._wechat_sogou_last_unenable_time = tools.get_current_timestamp()

        # 搜狗微信停用时间超过24小时了 可重新尝试
        elif tools.get_current_timestamp() - WechatService._wechat_sogou_last_unenable_time > TIME_INTERVAL: # 搜狗微信不可用 但是已经间歇一天 还可以一试
            result = WechatService._wechat_sogou.is_have_new_article(account_id = account_id, account = account_name)
            if result == constance.UPDATE:
                # 搜狗微信可用
                WechatService._wechat_sogou_enable = True

            elif result == constance.NOT_UPDATE:
                pass

            elif result == constance.ERROR:
                pass

            elif result == constance.VERIFICATION_CODE:
                pass

            # 更新下可用时间
            WechatService._wechat_sogou_last_unenable_time = tools.get_current_timestamp()

        # 如果搜狗微信不可用 则使用微信公众平台检查是否有新发布的文章
        if not result or result == constance.VERIFICATION_CODE:
            if WechatService._wechat_public_platform_enable: # 微信公众平台可用
                result = WechatService._wechat_public_platform.is_have_new_article(__biz)
                if result == constance.UPDATE:
                    # 有新发布的文章 抓取
                    pass

                elif result == constance.NOT_UPDATE:
                    # 无新发布的文章 pass
                    pass

                elif result == constance.ERROR:
                    # 被封了 请求失败 记录下失败时间
                    WechatService._wechat_public_platform_enable = False
                    WechatService._wechat_public_platform_last_unenable_time = tools.get_current_timestamp()

            elif tools.get_current_timestamp() - WechatService._wechat_public_platform_last_unenable_time > TIME_INTERVAL: # 搜狗微信不可用 但是已经间歇一天 还可以一试
                result = WechatService._wechat_public_platform.is_have_new_article(__biz)
                if result == constance.UPDATE:
                    # 有新发布的文章 抓取
                    WechatService._wechat_public_platform_enable = True

                elif result == constance.NOT_UPDATE:
                    # 无新发布的文章 pass
                    pass

                elif result == constance.ERROR:
                    # 被封了 请求失败 记录下失败时间
                    pass

                # 更新下可用时间
                WechatService._wechat_public_platform_last_unenable_time = tools.get_current_timestamp()

        return result

    def get_next_account(self):
        '''
        @summary:
        ---------
        ---------
        @result: 返回biz, 是否已做完一圈 (biz, True)
        '''

        while True:
            if not WechatService._todo_accounts:
                self.__load_todo_account()

            next_account_info =  WechatService._todo_accounts.popleft()
            next_account_id = next_account_info[2]
            next_account_biz = next_account_info[3]
            next_account_name = next_account_info[4]

            next_account = next_account_id, next_account_biz, WechatService._is_done, WechatService._is_all_done

            if not WechatService._wechat_sogou_enable:
                log.debug('搜狗微信不可用')

            if not WechatService._wechat_public_platform_enable:
                log.debug('微信公众平台不可用')

            # 不用检查是否发布新文章 直接跳出
            if not CHECK_NEW_ARTICLE:
                break

            # 搜狗微信和微信公众平台均不可用 跳出
            if not WechatService._wechat_sogou_enable and not WechatService._wechat_public_platform_enable:
                break

            # 使用检查新文章时，有一定的几率跳出， 采用微信客户端直接爬取，防止搜狗微信使用频繁出现验证码
            if random.randint(1, 3) == 1:
                log.debug('跳出 防止搜狗微信被封')
                break

            # 检查是今日是否有文章发布
            result = self.is_have_new_article(next_account_id, next_account_name, next_account_biz)
            if result == constance.UPDATE:
                break
            elif result == constance.NOT_UPDATE:
                if WechatService._is_done: # 防止公众号都没更新， 产生死循环 都检查完一遍 发现都没更新  直接跳出
                    break
                else:
                    tools.delay_time(15)
                    continue
            elif result == constance.ERROR:
                break
            elif result == constance.VERIFICATION_CODE:
                break
            else: # 检查更新不可用 直接调用客户端爬取
                break

        # 重置_is_done与_is_all_done 状态
        WechatService._is_done =  False
        WechatService._is_all_done = False

        return next_account

    def update_account_article_num(self, __biz):
        # 查询es 统计数量
        # 今日
        body = {
            "size":0,
            "query":{
                "filtered":{
                    "filter":{
                        "range":{
                            "record_time":{
                                "gte":tools.get_current_date('%Y-%m-%d') + ' 00:00:00',
                                "lte":tools.get_current_date('%Y-%m-%d') + ' 23:59:59'
                            }
                        }
                    },
                    "query":{
                        'match':{
                            "__biz" : __biz
                        }
                    }
                }
            }
        }
        result = WechatService._es.search('wechat_article', body)
        today_msg = result.get('hits', {}).get('total', 0)

        # 历史总信息量
        body = {
            "size":0,
            "query":{
                "filtered":{
                    "query":{
                        'match':{
                            "__biz" : __biz
                        }
                    }
                }
            }
        }
        result = WechatService._es.search('wechat_article', body)
        total_msg = result.get('hits', {}).get('total', 0)

        if total_msg:
            sql = "update TAB_IOPM_SITE t set t.today_msg = %d, t.total_msg = %d where t.biz = '%s'"%(today_msg, total_msg, __biz)
        else:
            sql = "update TAB_IOPM_SITE t set t.today_msg = %d where t.biz = '%s'"%(today_msg, __biz)
        print(sql)
        WechatService._db.update(sql)

    def is_exist(self, table, data_id):
        if WechatService._es.get(table, data_id = data_id, doc_type = table):
            return True
        else:
            return False

    def add_article_info(self, article_info):
        '''
        @summary:
        ---------
        @param article_info:
        ---------
        @result:
        '''


        log.debug('''
            -----文章信息-----
            标题     %s
            发布时间 %s
            作者     %s
            url      %s
            '''%(article_info['title'], article_info['release_time'], article_info['author'], article_info['url'])
            )

        WechatService._es.add('wechat_article', article_info, article_info.get('article_id'))

    def add_account_info(self, account_info):
        log.debug('''
            -----公众号信息-----
            %s'''%tools.dumps_json(account_info))

        WechatService._es.add('wechat_account', account_info, account_info.get('__biz'))

if __name__ == '__main__':
    wechat = WechatService()
    wechat.get_next_account()
    pass
