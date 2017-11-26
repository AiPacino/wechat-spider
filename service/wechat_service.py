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

SIZE = 100

class WechatService():
    _todo_accounts = collections.deque()
    _rownum = 1

    _is_done = False

    def __init__(self):
        self._db = OracleDB()
        self._es = ES()
        self.__load_todo_account()

    def __load_todo_account(self):
        if not WechatService._todo_accounts:
            sql = '''
                select *
                  from (select rownum r, t.id, t.biz
                          from TAB_WECHAT_ACCOUNT t
                         where rownum < {size})
                 where r >= {rownum}
                '''.format(rownum = WechatService._rownum, size = WechatService._rownum + SIZE)

            results = self._db.find(sql)
            if not results:
                WechatService._is_done = True
                WechatService._rownum = 1
                self.__load_todo_account()
            else:
                WechatService. _todo_accounts = collections.deque(results) #  转为队列
                WechatService._rownum += SIZE

    def get_next_account(self):
        '''
        @summary:
        ---------
        ---------
        @result: 返回biz, 是否已做完一圈 (biz, True)
        '''
        if not WechatService._todo_accounts:
            self.__load_todo_account()

        next_account = WechatService._todo_accounts.popleft()[2], WechatService._is_done
        # 重置_is_done 状态
        WechatService._is_done =  False

        return next_account

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
            %s'''%tools.dumps_json(article_info))

        self._es.add('wechat_article', article_info, article_info.get('article_id'))

    def add_account_info(self, account_info):
        log.debug('''
            -----公众号信息-----
            %s'''%tools.dumps_json(account_info))

if __name__ == '__main__':
    # wechat = WechatService()
    pass
