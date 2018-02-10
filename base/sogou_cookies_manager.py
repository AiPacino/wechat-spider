import sys
sys.path.append('../')

import init
import threading
import random

import utils.tools as tools
from utils.log import log
from db.sqlite3db import Sqlite3

MAX_UN_AVAILABLE_TIMES = 10
MIN_COOKIES_POOL = 50

class SogouCookiesManager():
    def __init__(self):
        self._sqlite3db = Sqlite3()
        self._cookies = []

    def run(self):
        while True:
            self.monitor_cookies()
            tools.delay_time(MONITOR_COOKIES_INTERVAL)

    def create_table(self):
        sql = '''
            CREATE TABLE if not exists sogou_cookies (
            id                  INTEGER          PRIMARY KEY AUTOINCREMENT,
            cookie              VARCHAR( 1000 )  UNIQUE,
            is_available        BOOLEAN          DEFAULT ( 1 ),
            un_available_time   DATETIME,
            un_available_times  INTEGER          DEFAULT ( 0 )
        )
        '''

        self._sqlite3db.create_table(sql)

    def add_cookies_from_file(self, file):
        cookies = tools.read_file(file, True)
        for cookie in cookies:
            cookie = cookie.strip()
            print(cookie)
            if cookie:
                sql = "insert into sogou_cookies (cookie) values ('%s')" % (cookie)
                self._sqlite3db.add(sql)

    def load_cookies(self):
        sql = 'select id, cookie, un_available_times from sogou_cookies where is_available = 1'
        cookies = self._sqlite3db.find(sql) # [(id,cookie, un_available_times), (id,cookie, un_available_times)]

        return cookies

    def get_cookie(self):
        if len(self._cookies) < MIN_COOKIES_POOL:
            self._cookies = self.load_cookies()

        cookie = []
        try:
            cookie = random.choice(self._cookies)
        except Exception as e:
            log.error('无可用的cookies')

        return cookie


    def set_cookie_un_available(self, cookie):
        '''
        @summary: 设置cookie不可用
        ---------
        @param cookie:(id. cookie, un_available_times)
        ---------
        @result:
        '''
        if not cookie: return

        try:
            # 从列表中移除
            self._cookies.remove(cookie)

            # 更新数据库
            sql = '''
                update sogou_cookies set
                  is_available = 0,
                  un_available_time = '%s',
                  un_available_times = un_available_times + 1
                where id = %d
                '''%(tools.get_current_date(), cookie[0])

            self._sqlite3db.update(sql)

        except Exception as e:
            log.error(e)

    def set_cookie_available(self, cookie):
        '''
        @summary: 设置cookie可用
        ---------
        @param cookie:(id. cookie, un_available_times)
        ---------
        @result:
        '''

        if not cookie: return

        un_available_times = cookie[2]
        if un_available_times:
            # 经过实际使用，真的可用，重置不可用时间、不可用次数为无，cookie状态设置为可用
            sql = '''
                update sogou_cookies set
                    is_available = 1,
                    un_available_time = null,
                    un_available_times = 0
                where id = %d
                '''%(cookie[0])

            self._sqlite3db.update(sql)


    def monitor_cookies(self):
        '''
        @summary: 监控管理cookies
        1、删除无用的cookie ： 不可用次数超过最大值
        2、将闲置24小时的cookie 设为可用
        ---------
        ---------
        @result:
        '''

        # 删除无用的cookie
        sql = 'delete from sogou_cookies where un_available_times > %d'%MAX_UN_AVAILABLE_TIMES
        self._sqlite3db.delete(sql)

        # 将闲置24小时的cookie 设为可用
        sql = '''
            update sogou_cookies set
                is_available = 1
            where un_available_time < '%s'
        '''%(tools.timestamp_to_date(tools.get_current_timestamp() - 24 * 60 * 60 ))

        self._sqlite3db.update(sql)


if __name__ == '__main__':
    sogou_cookies_manager = SogouCookiesManager()
    # sogou_cookies_manager.create_table()
    sogou_cookies_manager.add_cookies_from_file('base/weichat_sogou_cookies.txt')
    # print(sogou_cookies_manager.get_cookie())
    # sogou_cookies_manager.set_cookie_un_available((312, 'CXID=A612B349627E429B911A8CF98E4159F9; SUV=00022B896A794A4D595EDD99DDD68712; usid=5YYwOMxAmbYjTB70; LSTMV=398%2C289; LCLKINT=2018; ad=Qlllllllll2zvWsPlllllVIoxU1lllllNQQ@eZllll9lllllpllll5@@@@@@@@@@; SUID=894D796A5D68860A58ED862A000C055F; ABTEST=6|1518055954|v1; IPLOC=CN1100; PHPSESSID=7522far68i5rcvcef8aq07s4k0; SUIR=1518055954; seccodeErrorCount=2|Thu, 08 Feb 2018 02:19:01 GMT; SNUID=36308F8FF3F6905A07274C0EF4D35232; seccodeRight=success; successCount=1|Thu, 08 Feb 2018 02:19:21 GMT; refresh=1', 0))
    # sogou_cookies_manager.set_cookie_available((2, 'CXID=A612B349627E429B911A8CF98E4159F9; SUV=00022B896A794A4D595EDD99DDD68712; usid=5YYwOMxAmbYjTB70; LSTMV=398%2C289; LCLKINT=2018; ad=Qlllllllll2zvWsPlllllVIoxU1lllllNQQ@eZllll9lllllpllll5@@@@@@@@@@; SUID=894D796A5D68860A58ED862A000C055F; ABTEST=6|1518055954|v1; IPLOC=CN1100; PHPSESSID=7522far68i5rcvcef8aq07s4k0; SUIR=1518055954; seccodeErrorCount=2|Thu, 08 Feb 2018 02:19:01 GMT; SNUID=36308F8FF3F6905A07274C0EF4D35232; seccodeRight=success; successCount=1|Thu, 08 Feb 2018 02:19:21 GMT; refresh=1', 1))
