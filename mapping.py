# -*- coding: utf-8 -*-
'''
Created on 2017-11-28 14:22
---------
@summary: 设置ES mapping
---------
@author: Boris
'''

from db.elastic_search import ES

class WecahtMapping():
    """docstring for WecahtMapping"""
    def __init__(self):
        self._es = ES()

    def set_account_mapping(self):
        mapping = {
            "wechat_account":{
                "properties":{
                    "summary":{
                        "type":"string",
                        "analyzer":"ik_max_word"
                    },
                    "head_url":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "__biz":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "qr_code":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "verify":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "record_time":{
                        "type":"date",
                        "format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                    },
                    "account":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "account_id":{
                        "type":"string",
                        "index":"not_analyzed"
                    }
                }
            }
        }

        self._es.set_mapping('wechat_account', mapping)


    def set_article_mapping(self):
        mapping = {
            "wechat_article":{
                "properties":{
                    "summary":{
                        "type":"string",
                        "analyzer":"ik_max_word"
                    },
                    "like_num":{
                        "type":"long"
                    },
                    "author":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "title":{
                        "type":"string",
                        "analyzer":"ik_max_word"
                    },
                    "content":{
                        "type":"string",
                        "analyzer":"ik_max_word"
                    },
                    "source_url":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "url":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "article_id":{
                        "type":"long"
                    },
                    "cover":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "read_num":{
                        "type":"long"
                    },
                    "__biz":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "record_time":{
                        "type":"date",
                        "format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                    },
                    "account":{
                        "type":"string",
                        "index":"not_analyzed"
                    },
                    "release_time":{
                        "type":"date",
                        "format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                    }
                }
            }
        }

        self._es.set_mapping('wechat_article', mapping)


if __name__ == '__main__':
    wechat_mapping = WecahtMapping()
    # wechat_mapping.set_account_mapping()
    wechat_mapping.set_article_mapping()
