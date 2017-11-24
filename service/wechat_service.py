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

class WechatService():
    def __init__(self):
        pass

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
