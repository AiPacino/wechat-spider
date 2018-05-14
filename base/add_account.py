# -*- coding: utf-8 -*-
'''
Created on 2018-05-09 15:13
---------
@summary:
---------
@author: Boris
'''

import sys
sys.path.append('..')
import init

import utils.tools as tools
from utils.log import log
from db.oracledb import OracleDB
from base.wechat_public_platform import WechatPublicPlatform

if __name__ == '__main__':
    db = OracleDB()
    wechat_public_platform =  WechatPublicPlatform()

    # 取微信号
    # sql = 'select t.name, t.keyword2 from TAB_IOPM_CLUES t where t.zero_id = 7 and t.first_id = 137 and t.second_id = 183'
    # accounts = db.find(sql)
    accounts = ['广电猎酷', '实说新语', '祁文共赏', '网信北京', '长话短说', '断刀读书']
    for account in accounts:
        account_id = ''
        account_name = account
        biz = wechat_public_platform.get_biz(account_id = account_id, account = account_name)
        if biz:
            sql = "insert into TAB_IOPM_SITE t (t.id, t.name, t.position, t.classify, t.mointor_status, t.biz, t.priority) values (seq_iopm_site.nextval, '{name}', 1, 2, 701, '{biz}', 1)".format(name = account_name, biz = biz)
            print(sql)
            db.add(sql)
        tools.delay_time(10)
        # break
