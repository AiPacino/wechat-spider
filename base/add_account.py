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
    sql = 'select t.name, t.keyword2 from TAB_IOPM_CLUES t where t.zero_id = 7 and t.first_id = 137 and t.second_id = 183'
    accounts = db.find(sql)
    for account in accounts:
        account_name = account[0]
        account_ids = account[1].split(',')
        for account_id in account_ids:
            if account_id:
                biz = wechat_public_platform.get_biz(account_id = account_id, account = '')
                if biz:
                    sql = "insert into TAB_IOPM_SITE t (t.id, t.name, t.position, t.classify, t.mointor_status, t.biz, t.priority) values (seq_iopm_site.nextval, '{name}', 1, 2, 701, '{biz}', 1)".format(name = account_name, biz = biz)
                    print(sql)
                    db.add(sql)
                    tools.delay_time(10)
        # break
