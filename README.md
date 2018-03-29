微信公众号抓取
====
***爬取范围***

1. 公众号所有历史文章，及公众号信息
2. 文章信息包括：标题、作者、贴图、简介、内容、url、点赞数、评论数、评论信息
3. 公众号信息包括：账号名、认证信息、二维码、头像地址、简介



1、数据结构
----
###1.1、 公众号表 ###
> 表名`wechat_account`


| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|account|varchat|||公众号名 如:工商银行|
|account_id|varchat|||公众号id 如：icbc601398|
|__biz|varchat|||公众号唯一参数， 用于关联文章|
|head_url|varchat|||头像地址|
|qr_code|varchat|||二维码|
|verify|varchat|||认证信息|
|summary|varchat|||简介|
|record_time|date|||爬取时间|


### 1.2、文章表 ###
> 表名`wechat_article`

| 字段名              | 数据类型| 长度 | 说明       | 描述 |
|:-------------------|:-------|:-----|:--------- |:----|
|article_id|number|||文章id|
|title|varchat|||标题|
|author|varchat|||作者|
|summary|varchat|||文章简介|
|cover|varchat|||简介处贴图|
|content|clob|||内容|
|like_num|number|||点赞数|
|read_num|number|||阅读数|
|comment|json|||评论信息|
|url|varchat|||文章链接|
|source_url|varchat|||阅读原文 链接|
|record_time|date|||爬取时间|
|release_time|date|||发布时间|
|account|varchat|||公众号名|
|__biz|varchat|||公众号唯一参数 可关联公众号表|

2、数据包分析
------

### 2.1 公众号数据请求解析 ###
2.1.1 点击公众号历史文章，通过抓包可以发现如下信息：

**历史文章列表链接**：

    https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MTg1ODI1NA==&scene=124&devicetype=iOS11.2.5&version=16060323&lang=en&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=Ih93pI6o%2B88hvER4xVmbvidH6jnRZ2Paz9tsJSLfrVe3u7EJ6UP5claYmLdQORvy&wx_header=1

可简化为：

    https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MTg1ODI1NA==&scene=124#wechat_redirect

**公众号信息**：（可由历史文章链接返回的数据中获取）

![](https://i.imgur.com/ShpavoW.png)

如图所示，我们在历史文章链接接口所返回的数据中可以获取到公众号的`名称`、`头像地址`、`认证机构`、`简介`。

`公众号二维码`需要拼接参数

     http://open.weixin.qq.com/qr/code?username=gh_eceaf2ac1bdd

username为历史文章列表数据里的username字段值, 如var username = "" || "gh_eceaf2ac1bdd"; 

注：

1. 头像地址为`<img src="http://wx.qlogo.cn/mmhead/Q3auHgzwzM45wwb69ZRxzjwsyIbOibLe9xdAvnOddaC9nKfFsyHykLA/0" id="icon">`内的src所指向地址。
2. 认证信息：已关注的公众号不返回认证信息，想取认证信息，直接搜索公众号，查看历史文章列表，通过正则提取。
3. `__biz`可作为公众号的唯一标识，可由历史文章列表的链接中提取

### 2.2 文章信息数据请求解析 ###

2.2.1 html格式的文章列表

1. 点击公众号查看历史文章，初次返回文章列表的数据包为html格式，正则提取`var msgList = `参数后面的信息，可得近10天的文章信息。有无更多文章可由`can_msg_continue = '0'`得知。无更多文章 can_msg_continue = '0'， 有更多文章 can_msg_continue = '1'。
2. 请求地址<pre>https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzIzOTU0NTQ0MA==&scene=124&devicetype=iOS11.1.1&version=16051620&lang=zh_CN&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=1vn9nCwlFpfowKXpKyZHFzzB64gF3f62hcV6RIiZApKABY7R6EnSDiBuYcnK4sSD&wx_header=1</pre>﻿​

2.2.2 json格式的文章列表

1. 若有更多文章，下拉请求更多发现返回的数据为json格式。
2. 请求地址
    <pre>https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzIzOTU0NTQ0MA==&f=json&offset=10&count=10&is_ok=1&scene=124&uin=777&key=777&pass_ticket=1vn9nCwlFpfowKXpKyZHFzzB64gF3f62hcV6RIiZApKABY7R6EnSDiBuYcnK4sSD&wxtoken=&appmsg_token=931_aRav431jnRB%252FDFCxZYjYLAqcUdGUt6_UHgWVcw~~&x5=0&f=json
    </pre>
3. 参数变化
    ![](https://i.imgur.com/DPRXugQ.png)
4. 换个公众号，查看历史文章，参数变化
    ![](https://i.imgur.com/9dQyrya.png)

得出：

1. json格式的文章列表变化的参数为__biz、pass_ticket、appmsg_token、offset
2. 如果是返回的文章列表是html数据，pass_ticket、__biz可由请求地址中获取，appmsg_token可由其返回的html中获取。如下：![](https://i.imgur.com/bTmMFxx.png)
3. 如果返回的是json数据， pass_ticket、appmsg_token、offset可由请求地址中获取  
4. offset为文章偏移量 默认为10，后续可由返回的json中获取
5. 注：pass_ticket、appmsg_token会过期， 失效时间为3个半小时。所以取历史文章翻页的时候，要考虑到地址过期的问题,否则不能取尽历史文章。过期后地址变化如下![](https://i.imgur.com/kJ2PijJ.png) appmsg_token 参数可由文章的源代码中获取，pass_ticket过期不影响数据的正常请求，可不管。

数据如下：

1. 文章列表数据：
    <pre>
    {
        "ret":0,
        "errmsg":"ok",
        "msg_count":10,
        "can_msg_continue":1,
        "general_msg_list":"{"list":[{"comm_msg_info":{"id":1000000275,"type":49,"datetime":1510333570,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"阿！里！工！程！师！","digest":"！！！","content":"","fileid":100002637,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486288&idx=1&sn=58575f84322673bc64f2c3bf00629e8b&chksm=e929365fde5ebf49420c47a86ecb1e01b0bc93c10bde32270e30d7abf8b61f0cd281dc023e77&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naIFia5LVpHNcKrud4HxNs9epyLkhjj2SL3tQThXk8AZdicuzm8fOsYowbcVdrmcH9XictI7AwQCHqicZA\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"阿里妹爱你们","copyright_stat":100,"del_flag":1}},{"comm_msg_info":{"id":1000000274,"type":49,"datetime":1510272480,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"《人民日报》刊文 | 王坚博士谈“云计算之后，我为什么要做城市大脑？”","digest":"“未来，在城市发展中数据资源将会比土地资源更重要。”","content":"","fileid":100002634,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486284&idx=1&sn=869f9ef422ba00cf5b3456143247445c&chksm=e9293643de5ebf55085935bd6537bd8f4b3f4a4f091cd9d7f374f60f585c217eb5ab22066630&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naJaVdMEqal46bENU72pIboWr2V6zMibvaibGibcMwsnREWmQczWicBkTWRUPbca3KkXPp9mCxSsiariaicGg\/0?wx_fmt=jpeg","subtype":9,"is_multi":1,"multi_app_msg_item_list":[{"title":"双11前夕，阿里技术人都在忙什么？","digest":"每年双11对于阿里巴巴的“攻城狮”来说，都是一次大考。","content":"","fileid":100002629,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486284&idx=2&sn=3ff2110eeea2d7592cb4bebe0a087f41&chksm=e9293643de5ebf5576f62827d5312f0e83f67e34bfc5afffcee837427b76bafe837d48b37fa0&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naJaVdMEqal46bENU72pIboWXl02OwDe8aCkPyXJbrUDfryXcR5iawicPmDNoiaXeGRMibuh9Bm9fJcq1A\/0?wx_fmt=jpeg","author":"燃！技享双11","copyright_stat":11,"del_flag":1}],"author":"王坚","copyright_stat":11,"del_flag":1}},{"comm_msg_info":{"id":1000000272,"type":49,"datetime":1510186080,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"阿里90后工程师，如何用AI程序写出双11打call歌？","digest":"这个神奇的程序，经过大量数据的“喂养”和设定，可以自己写饶舌歌曲。","content":"","fileid":100002616,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486267&idx=1&sn=bb9ca092b78f7f06a9bb84678a69887f&chksm=e9293634de5ebf22283a587b6d085323f8229b9e990027c84db515bcb8348248708afc0e740c&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naL1icqibib9mTw5zK96CNCW359BZRCwk3TmRTzLtCetDU0iclNtzwGK7XIjIQ7nRyaGvBUspiaBfic97zTA\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"芦阳","copyright_stat":11,"del_flag":1}},{"comm_msg_info":{"id":1000000270,"type":49,"datetime":1510099680,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"AI设计师“鲁班”进化史：每秒制作8000张双11海报，没有一张雷同！","digest":"今年天猫双11将有4亿张海报由“鲁班”设计。\\n\\n究竟它是如何做到的？","content":"","fileid":100002589,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486239&idx=1&sn=161dc151b2e335786ab007efedb42aa0&chksm=e9293610de5ebf064e1b5925efa309025efc1397d95a96669c13ff4f4e1771cc2b47684f3250&scene=27#wechat_redirect","source_url":"https:\/\/promotion.aliyun.com\/ntms\/act\/luban.html?wh_ttid=pc","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naIS8CmFOC5TCf8s01ky3UePM6xjIGgvlUubtVIMugnTN7fTCQ70gu96FRULM6GHex6OlpNiau1HeqQ\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"人机协同","copyright_stat":11,"del_flag":1}},{"comm_msg_info":{"id":1000000269,"type":49,"datetime":1510013280,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"惊！阿里双11数据中心来了一位顶级“刺客”？","digest":"2秒杀掉异常机器，命中率高达94%！","content":"","fileid":100002577,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486226&idx=1&sn=2a1477e810b885c1236a2351c5aebf3f&chksm=e929361dde5ebf0bb7c33f39d10f29bedc58d97b9d0fa7d559d6efb7efa75e442479598cba22&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naLz98fXEfibYsfQ8USCaEpYDia3VXg0l8w2GdMhgEIgC6DWbudl0gMla1RQHibZ2mbicZZllY4DiaRFgmw\/0?wx_fmt=jpeg","subtype":9,"is_multi":1,"multi_app_msg_item_list":[{"title":"想找回丢在出租车的手机？你需要融合异构数据的城市级查询和推理","digest":"每一次查找、定位、匹配，都对应了复杂的查询语句和计算。","content":"","fileid":100002573,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486226&idx=2&sn=607bf03db305fb7725806387b24085f2&chksm=e929361dde5ebf0b8cbf23b023beca79101539ead1136bdc373e5ea1ee45ee3e59b395dea6b7&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naLz98fXEfibYsfQ8USCaEpYDDReGU76pLO7yMk4rib7dz1oJgkiaI8KpRibYj9iatW7bNMFBvic9QWEWzdQ\/0?wx_fmt=jpeg","author":"了不起的","copyright_stat":11,"del_flag":1}],"author":"","copyright_stat":100,"del_flag":1}},{"comm_msg_info":{"id":1000000268,"type":49,"datetime":1509934924,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"中国首个！阿里巴巴获机器视觉顶级会议ACM MM2020主办权","digest":"阿里巴巴iDST副院长、IEEE院士华先胜博士成为 2020年ACM Multimedia 大会主席，阿里巴巴成为首个获得ACM MM主办权的中国企业！","content":"","fileid":100002563,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486215&idx=1&sn=5f6801e32364ba089fb481dcd82b132d&chksm=e9293608de5ebf1e4f933c10c82b5444921b416ac66fa5cfefa15102ac3fadaee96a164bc13b&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naLz98fXEfibYsfQ8USCaEpYDiakicicSutJVDhBHBqGoCX2O7EL4icLLOsSM3zFcZW42ROEzzQa80K4zDg\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"","copyright_stat":100,"del_flag":1}},{"comm_msg_info":{"id":1000000267,"type":49,"datetime":1509667680,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"阿里EB级大数据体系，如何做到秒级响应、高效赋能？","digest":"阿里资深技术专家姚滨晖，告诉你一个世界级的大数据架构体系。","content":"","fileid":100002554,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486203&idx=1&sn=1674d92fb12cec6b0d41a0124bb86776&chksm=e92937f4de5ebee204eaec75589a5444b620eca96a3ffc557dad74a7ec2545567f70d0275a4a&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naIicBdJM1Rbx7iaGOiavRErc6pPY6cNyS1jqSNAexM4qZN0grOicXXjWH9ZJcHPcrRSO0DSibUFGib7EJSw\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"姚滨晖","copyright_stat":100,"del_flag":1}},{"comm_msg_info":{"id":1000000266,"type":49,"datetime":1509616500,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"双11要来了，阿里招了一批身怀绝技的技术新童鞋！","digest":"阿里妹激动地狂打call！","content":"","fileid":100002548,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486197&idx=1&sn=7c52f13abdc0301aad1e6f52c3d94e54&chksm=e92937fade5ebeecc86cefa58985f332c8da877486ad1db246fcb955d1028ef5c98c7b8b8904&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naIicBdJM1Rbx7iaGOiavRErc6pxwHeh4yJpZuVt3aeuXZib0TjNogA6iakbPKI6XY2EGdGFu9iaOUIvz7pA\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"宁函夏","copyright_stat":101,"del_flag":1}},{"comm_msg_info":{"id":1000000265,"type":49,"datetime":1509466417,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"技术变化那么快，程序员如何做到不被淘汰？","digest":"技术日新月异，奋力追赶的我们，究竟是技术的主人还是奴隶？程序员的真正价值又是什么？","content":"","fileid":100002530,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486179&idx=1&sn=78c7e7c118a6316e2a85c413f2df0e30&chksm=e92937ecde5ebefac076a1b18fdcbda36660d04b18e42c15eb1d72d03bb2eba55f76a3c662ef&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naKjayChjib4yFEflFtibR9R9hBpfKZku9yqpnJtxtjcEmpVkPop2Z7juJ46hDDq6nHIricTDLTLibES1w\/0?wx_fmt=jpeg","subtype":9,"is_multi":0,"multi_app_msg_item_list":[],"author":"空融","copyright_stat":100,"del_flag":1}},{"comm_msg_info":{"id":1000000264,"type":49,"datetime":1509408480,"fakeid":"3239545440","status":2,"content":""},"app_msg_ext_info":{"title":"云栖大会100位顶级大咖演讲PPT+视频全分享！","digest":"深入了解世界上规模最大、应用最丰富、场景最复杂的技术及业务。","content":"","fileid":100002521,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486172&idx=1&sn=a518b4317f13d344a621ef7a6fa97b55&chksm=e92937d3de5ebec5d9314d29511dcb05cb888ea64196ef44eb8e494dd7dfb589c733e76c125c&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naLIdDqP1K8ic6IcdLICNibkC6YcuD6NTcAXKPL7QhUff9CyU1baVaaXvnwxR0CeRcO7lYZEPEtbjd8Q\/0?wx_fmt=jpeg","subtype":9,"is_multi":1,"multi_app_msg_item_list":[{"title":"城市大脑技术厉害了！阿里 iDST 三篇相关论文入选ACM MM","digest":"此次入选的三篇论文涉及的交通事故、人流轨迹、交通数据样本等技术问题均来自“城市大脑”实际应用场景。","content":"","fileid":100002522,"content_url":"http:\/\/mp.weixin.qq.com\/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486172&idx=2&sn=1a7f69f2e034cc713832a36d1d90ace3&chksm=e92937d3de5ebec5918f50534db495ea22d11d7be76dc4276f4519c7dd62a82196a8fae9d6e3&scene=27#wechat_redirect","source_url":"","cover":"http:\/\/mmbiz.qpic.cn\/mmbiz_jpg\/Z6bicxIx5naLIdDqP1K8ic6IcdLICNibkC6UoMbGVyIyrrfpdr5LOZPeSsq2weCLvT36KRIn4QcwjmsGnq3R1nY0Q\/0?wx_fmt=jpeg","author":"","copyright_stat":100,"del_flag":1}],"author":"拥抱开源的","copyright_stat":100,"del_flag":1}}]}",
        "next_offset":20
    }</pre>
2. 翻到低，无数据时返回数据如下：
    <pre>
    {
        "ret":0,
        "errmsg":"ok",
        "msg_count":0,
        "can_msg_continue":0,
        "general_msg_list":"{"list":[]}",
        "next_offset":11
    }
    </pre>
3. 文章列表字段意义说明：
    <pre>
    "list": [ //最外层的键名；只出现一次，所有内容都被它包含。
        {//这个大阔号之内是一条多图文或单图文消息，通俗的说就是一天的群发都在这里
            "app_msg_ext_info":{//图文消息的扩展信息
                "content_url": "图文消息的链接地址",
                "cover": "封面图片",
                "digest": "摘要",
                "is_multi": "是否多图文，值为1和0",
                "multi_app_msg_item_list": [//这里面包含的是从第二条开始的图文消息，如果is_multi=0，这里将为空
                    {
                        "content_url": "图文消息的链接地址",
                        "cover": "封面图片",
                        "digest": ""摘要"",
                        "source_url": "阅读原文的地址",
                        "title": "子内容标题"
                    },
                    ...//循环被省略
                ],
                "source_url": "阅读原文的地址",
                "title": "头条标题"
            },
            "comm_msg_info":{//图文消息的基本信息
                "datetime": '发布时间，值为unix时间戳',
                "type": 49 //类型为49的时候是图文消息 爬虫只爬取type为49的， 其他消息如视频、语音、文本 格式和图文格式不一样且无意义
            }
        },
    ...//循环被省略
    ]

    </pre>

2.2.3文章详情

1. 由文章列表中可取出文章的url，地址如下<pre>https://mp.weixin.qq.com/s?__biz=MzIzOTU0NTQ0MA==&mid=2247486197&idx=1&sn=7c52f13abdc0301aad1e6f52c3d94e54&chksm=e92937fade5ebeecc86cefa58985f332c8da877486ad1db246fcb955d1028ef5c98c7b8b8904&scene=38&ascene=3&devicetype=iOS11.1.1&version=16051620&nettype=WIFI&abtest_cookie=AgABAAoADAAIAEuIHgCCiB4ArogeALqIHgDniB4A%2FIgeAA%2BJHgBGiR4AAAA%3D&fontScale=100&pass_ticket=1vn9nCwlFpfowKXpKyZHFzzB64gF3f62hcV6RIiZApKABY7R6EnSDiBuYcnK4sSD&wx_header=1 
</pre>
参数说明：

    1.1 __biz可以认为是微信公众平台对外公布的公众帐号的唯一id

    1.2 mid是图文消息id, 同一天的mid一样

    1.3 idx是发布的第几条消息(1就代表是头条位置消息)
    
    1.4  mid与idx拼接 确定唯一篇文章。评论点赞数以及评论信息都和该两个参数关联

2.2.4 点赞量、阅读量

1. 访问文章详情url时，微信客户端会主动发起阅读量和点赞量的请求，请求地址如下（该地址我们不需要关心，只需截获返回的数据包即可）：<pre>https://mp.weixin.qq.com/mp/getappmsgext?__biz=MzIzOTU0NTQ0MA==&appmsg_type=9&mid=2247486197&sn=7c52f13abdc0301aad1e6f52c3d94e54&idx=1&scene=38&title=%E5%8F%8C11%E8%A6%81%E6%9D%A5%E4%BA%86%EF%BC%8C%E9%98%BF%E9%87%8C%E6%8B%9B%E4%BA%86%E4%B8%80%E6%89%B9%E8%BA%AB%E6%80%80%E7%BB%9D%E6%8A%80%E7%9A%84%E6%8A%80%E6%9C%AF%E6%96%B0%E7%AB%A5%E9%9E%8B%EF%BC%81&ct=1509616500&abtest_cookie=AgABAAoADAAIAEuIHgCCiB4ArogeALqIHgDniB4A/IgeAA+JHgBGiR4AAAA=&devicetype=iOS11.1.1&version=&f=json&r=0.8818055899366186&is_need_ad=1&comment_id=2113125141&is_need_reward=0&both_ad=0&reward_uin_count=0&msg_daily_idx=1&is_original=0&uin=777&key=777&pass_ticket=1vn9nCwlFpfowKXpKyZHFzzB64gF3f62hcV6RIiZApKABY7R6EnSDiBuYcnK4sSD&wxtoken=3465907592&devicetype=iOS11.1.1&clientversion=16051620&appmsg_token=931_qHpqa2KzvFlDJD%252B7tv6FD3A49fuOZPxAU-vg52-Nbp1TT5RK8WtZThpX7XJbKewFocNg9T2Eb6idZ8_X&x5=0&f=json</pre>
   
2. 数据包如下
    <pre>
    {
        "advertisement_num":0,
        "advertisement_info":[
    
        ],
        "appmsgstat":{
            "show":true,
            "is_login":true,
            "liked":false,
            "read_num":38785, //阅读量
            "like_num":99, //点赞量
            "ret":0,
            "real_read_num":0
        },
        "comment_enabled":1,  # 当没有开评论区时， 无此参数
        "reward_head_imgs":[
    
        ],
        "only_fans_can_comment":false,
        "is_ios_reward_open":0,
        "base_resp":{
            "wxtoken":3465907592
        }
    }
    </pre>

2.2.5 评论信息

1. 访问文章详情url时，微信客户端会主动发起阅读量和点赞量的请求，若返回的数据包中有`"comment_enabled":1`参数，微信客户端会主动发起评论信息的请求，请求地址如下（该地址我们不需要关心，只需截获返回的数据包即可）：<pre>https://mp.weixin.qq.com/mp/appmsg_comment?action=getcomment&scene=0&__biz=MzIzOTU0NTQ0MA==&appmsgid=2247486197&idx=1&comment_id=2113125141&offset=0&limit=100&uin=777&key=777&pass_ticket=1vn9nCwlFpfowKXpKyZHFzzB64gF3f62hcV6RIiZApKABY7R6EnSDiBuYcnK4sSD&wxtoken=3465907592&devicetype=iOS11.1.1&clientversion=16051620&appmsg_token=931_qHpqa2KzvFlDJD%252B7tv6FD3A49fuOZPxAU-vg52-Nbp1TT5RK8WtZThpX7XJbKewFocNg9T2Eb6idZ8_X&x5=0&f=json</pre>
2. 数据包 <pre>
    {
    　　"base_resp":{
    　　　　"ret":0,
    　　　　"errmsg":"ok"
    　　},
    　　"enabled":1,
    　　"is_fans":1,
    　　"nick_name":"Boris",
    　　"logo_url":"http://wx.qlogo.cn/mmhead/Q3auHgzwzM5IFyicP5EmDhDiaib9UdIfANFw8Uc61g175790VALogVSpA/132",
    　　"my_comment":[
    
    　　],
    　　"elected_comment":[
    　　　　{
    　　　　　　"id":7,
    　　　　　　"my_id":6,
    　　　　　　"nick_name":"eiEio",
    　　　　　　"logo_url":"http://wx.qlogo.cn/mmhead/Q3auHgzwzM6LY14On7JcXHXlQXcwnWX2r6WrrvhPYb0QyKEoFLW0CA/132",
    　　　　　　"content":"期待着让小天巡给12306助力！",
    　　　　　　"create_time":1509616770,
    　　　　　　"content_id":"7018544699937914886",
    　　　　　　"like_id":10002,
    　　　　　　"like_num":42,
    　　　　　　"like_status":0,
    　　　　　　"is_from_friend":0,
    　　　　　　"reply":{
    　　　　　　　　"reply_list":[
    
    　　　　　　　　]
    　　　　　　},
    　　　　　　"is_from_me":0,
    　　　　　　"is_top":0
    　　　　},
    　　　　{
    　　　　　　"id":14,
    　　　　　　"my_id":6,
    　　　　　　"nick_name":"月",
    　　　　　　"logo_url":"http://wx.qlogo.cn/mmhead/PiajxSqBRaELM6Qia7UFsE8gw3PfhAwyVhDl4WGCAc7A7gC9fEeWXziaA/132",
    　　　　　　"content":"阿里妹，我爱你幺[阴险]",
    　　　　　　"create_time":1509616878,
    　　　　　　"content_id":"2543730304162463750",
    　　　　　　"like_id":10009,
    　　　　　　"like_num":2,
    　　　　　　"like_status":0,
    　　　　　　"is_from_friend":0,
    　　　　　　"reply":{
    　　　　　　　　"reply_list":[
    　　　　　　　　　　{
    　　　　　　　　　　　　"content":"[机智] 真有眼光！",
    　　　　　　　　　　　　"uin":3239545440,
    　　　　　　　　　　　　"create_time":1509617109,
    　　　　　　　　　　　　"reply_id":1,
    　　　　　　　　　　　　"to_uin":592258364,
    　　　　　　　　　　　　"reply_like_num":4
    　　　　　　　　　　}
    　　　　　　　　]
    　　　　　　},
    　　　　　　"is_from_me":0,
    　　　　　　"is_top":0
    　　　　}
    　　],
    　　"friend_comment":[
    
    　　],
    　　"elected_comment_total_cnt":35,
    　　"only_fans_can_comment":false
    }</pre>

3. 评论信息结构解析 
    <pre>
    {
        "base_resp":{
            "ret":0,
            "errmsg":"ok"
        },
        "enabled":1,
        "is_fans":1,
        "nick_name":"Boris", // 自己的用户名
        "logo_url":"http://wx.qlogo.cn/mmhead/Q3auHgzwzM5IFyicP5EmDhDiaib9UdIfANFw8Uc61g175790VALogVSpA/132", // 头像
        "my_comment":[
    
        ],
        "elected_comment":[
            {
                "id":499,
                "my_id":111,
                "nick_name":"王树磊¹³⁷⁹²⁹²⁸³⁰²", //评论信息
                "logo_url":"http://wx.qlogo.cn/mmhead/Tjnia6K0WAwz922ePc3NxIyCwMtDzNGZzOMKhylPk4Kr5ecrH3YHREg/132", // 头像
                "content":"憋走，你快给我解开，笑死了，小罗公司都是人才，兴哥最有才了",
                "create_time":1511267001, //时间
                "content_id":"7578315634530844783",
                "like_id":10001,
                "like_num":3014, //点赞数
                "like_status":0,
                "is_from_friend":0,
                "reply":{
                    "reply_list":[
                        {
                            "content":"我没才咋滴？", // 回复的信息
                            "uin":3264014358,
                            "create_time":1511267052, //时间
                            "reply_id":1,
                            "to_uin":1764464107,
                            "reply_like_num":1196 // 点赞
                        }
                    ]
                },
                "is_from_me":0,
                "is_top":0
            }
        ],
        "friend_comment":[
    
        ],
        "elected_comment_total_cnt":22,
        "only_fans_can_comment":false
    }
    </pre>

**数据请求总结**

1. 所有有用的请求 有在 mp.weixin.qq.com 这个域名下
2. 点击文章时， 会自动加载评论、观看量和评论内容
3. 前十文章 （html）url：https://mp.weixin.qq.com/mp/profile_ext?action=home
4. 后续文章  （json）url：https://mp.weixin.qq.com/mp/profile_ext?action=getmsg
5. 文章链接 ：html或者json获取
6. 阅读量、点赞量 （json）   url ：https://mp.weixin.qq.com/mp/getappmsgext
7. 评论信息（json） url：https://mp.weixin.qq.com/mp/appmsg_comment  （没开评论区的公众号貌似不请求该url）
8. 公众号信息可由3中返回的html中获取

3.技术思路
------
> 使用中间人的方式，截获微信服务端到微信客户端的数据，处理入库。然后修改返回的数据，注入js，传递给微信客户端，实现自动翻页，爬取更多。

### 3.1工具 ###
1. anyproxy
2. node-v6.11.0-win-x64
3. 微信客户端
4. python3.5

### 3.2 环境搭建###
3.2.1 anyproxy搭建

1. 安装anyproxy代理，下载地址：[https://github.com/liubo0621/node-v6.11.0-win-x64_wechat](https://github.com/liubo0621/node-v6.11.0-win-x64_wechat)
2. 下载完后将node.exe 所在目录设置添加到环境变量
3. cmd中输入anyproxy --root 生成证书
4. 启动anyproxy：anyproxy -i；参数-i是解析HTTPS的意思，浏览器中数据localhost:8002,若看到anyproxy的web界面，则启动成功
3. 手机端设置代理服务，ip为anyproxy所在电脑的ip，端口号为8001。注手机与电脑必须在同一网络下
4. 安装手机端证书：打开手机端浏览器，输入http://localhost:8002/qr_root 可以获取证书路径的二维码，下载安装。

3.2.2 python环境搭建

下载python3.5 安装包，双击 选择add to path， 然后一直下一步即可安装。安装完毕后，在cmd中输入python， 若出现python命令窗口，则说明安装成功。

### 3.3 代码及技术思路讲解 ###

3.3.1 anyroxy代码及思路讲解

1. 打开`\node-v6.11.0-win-x64_wechat\node_modules\anyproxy\lib\rule_default.js` 查看`replaceServerResDataAsync`方法，通过该方法，可以劫持服务端到客户端的数据，处理入库，然后篡改数据再给客户端。代码如下：
    <pre>
    replaceServerResDataAsync: function(req,res,serverResData,callback){
        try{
            function nextPageCallback(reponse){
                // 修改响应到客户端的数据 实现自动跳转到下个公众号
                if (reponse == "None"){
                    callback(serverResData);
                }else{
                    callback(reponse + serverResData);
                }
            }

            if(/mp\/profile_ext\?action=home/i.test(req.url) || /mp\/profile_ext\?action=getmsg/i.test(req.url)){ //文章列表 包括html格式和json格式
                httpPost(serverResData.toString(), "/wechat/get_article_list", req.url, nextPageCallback);
            }
            else if(/\/s\?__biz=/i.test(req.url) || /mp\/appmsg\/show\?__biz=/i.test(req.url) || /\/mp\/rumor/i.test(req.url)){ //文章内容；mp/appmsg/show?_biz 为2014年老版链接;  mp/rumor 是不详实的文章
                httpPost(serverResData.toString(), "/wechat/get_article_content", req.url, nextPageCallback);
            }
            else if (/mp\/getappmsgext/i.test(req.url)){ // 阅读量 观看量
                httpPost(serverResData.toString(), "/wechat/get_read_watched_count", req.url, nextPageCallback);
            }
            else if (/mp\/appmsg_comment/i.test(req.url)){ // 评论列表
                httpPost(serverResData.toString(), "/wechat/get_comment", req.url, nextPageCallback);
            }
            else{
                // 不是想捕获的数据 直接响应到客户端 不需要修改
                callback(serverResData);
            }

        }catch(e){
            console.log(e);
            callback(serverResData);
        }

    },
    </pre>
2. 发送数据到自己写的服务端，代码如下：
    <pre>
    // 发送数据到自己的服务端
    function httpPost(data, actionMethod, reqUrl, callback = "") {
        console.log('发送数据到服务端')
        console.log(reqUrl)
    
        var http = require('http');
        var data = {
            data:data,
            req_url:reqUrl
        };
        content = require('querystring').stringify(data);
        var options = {
            method: "POST",
            host: "localhost", //注意没有http://，这是服务器的域名。
            port: 6210,
            path: actionMethod, //处理请求的action
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                "Content-Length": content.length
            }
        };
        var req = http.request(options, function (res) {
            res.setEncoding('utf8');
            res.on('data', function (chunk) { // chunk 为假时不触发回调
                console.log('BODY: ' + chunk);
    
                if (callback){
                    callback(chunk) //chunk 为自己写的服务端返回的数据
                }
    
            });
        });
        req.on('error', function (e) {
            console.log('problem with request: ' + e.message);
        });
        req.write(content);
        req.end();
    }
    </pre>
3. 修改reponse头，去掉安全协议并且将json的数据响应格式改为html，否者向微信客户端注入的js不生效，如下：
    <pre>
    replaceResponseHeader: function(req,res,header){
        // 修改json格式的头为html格式， 否则javascript自动跳转脚本不生效
        if(/mp\/profile_ext/i.test(req.url)){ //文章列表 包括html格式和json格式
            header['content-type'] = 'text/html; charset=UTF-8'
        }
        // 修改文章内容的响应头，去掉安全协议，否则注入的<script>setTimeout(function(){window.location.href='url';},sleep_time);</script>js脚本不执行
        else if(/\/s\?__biz=/i.test(req.url) || /mp\/appmsg\/show\?__biz=/i.test(req.url) ){
            delete header['content-security-policy']
            delete header['content-security-policy-report-only']
        }
    },
    </pre>
4. 手机端会经常请求google，为防止异常，把请求替换为百度，如下：
    <pre>
    replaceRequestOption : function(req,option){
        // 将手机端google的请求改为百度，防止异常
        var newOption = option;
        if(/google/i.test(newOption.headers.host)){
            newOption.hostname = "www.baidu.com";
            newOption.port     = "80";
        }
        return newOption;
    },
    </pre>

3.3.2 数据处理服务端代码及思路讲解
>通过anyproxy，可截获数据到服务端，我们编写服务端，处理数据入库。如下

1. 使用webpy框架，搭建python数据处理服务端
2. 处理公众号信息，根据传过来的数据，使用正则提取即可
3. 处理文章列表

    （1）解析文章列表

    （2）将文章信息存入缓存区

    （3）将文章url添加到待抓取的url地址池队列

    （4）判断是否可以下拉显示更多，若可以，则将下拉显示更多的url也添加到待抓取的url地址池队列

    （5）判断url地址池队列是否为空，若空转到步骤6，不为空则抛出地址池队列的头地址，嵌入js，返回到anyproxy，anyproxy收到数据后，会继续将带有js的数据返回给微信客户端，这样我们便向客户端注入了js，可实现自动跳转。js自动跳转代码如下：
    <pre>
    &lt;script>setTimeout(function(){window.location.href='跳转地址';},延时xxx毫秒);&lt;/script>
    </pre>

    (6) 若队列为空，则去库中取下一个待爬取公众历史链接（需要biz参数）。通过步骤5方法嵌入js返回给客户端，实现自动爬取下一个公众号。公众号历史文章地址格式如下：
    <pre>https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=_biz参数&scene=124#wechat_redirect</pre>

4. 文章内容获取
    1. 步骤3已经向微信客户端注入了自动跳转文章详情url的js，到设定的延时后，我们会收文章详情的数据，正则提取文章正文信息，若正文信息存在，则追加到对应的文章信息缓存区。否则可能为被验证不实的文章，此时微信客户端不会发起点赞量、阅读量的请求，直接将该文章信息整体入库，再从缓存区中删除该文章信息。
    2. 如果url地址池最后一个地址是文章列表链接，则用正则从微信文章详情页提取appmsg_token参数，替换url地址池最后一个地址，防止appmsg_token过期、地址失效
    
5. 阅读量和点赞量获取
    1. 访问公众号文章内容时，客户端会主动发起点赞量和阅读量的请求，我们只需截获其返回的数据即可，取出点赞量、阅读量追加到对应的文章信息缓存区
    2. 通过步骤1返回的数据，可以判断是否有评论信息，若有则转到步骤5。若无，则直接入库，然后从缓存区中删除该文章信息。
    
6. 评论信息获取  

    1. 微信客户端会主动发起评论信息的请求。我们截获评论信息，追加到对应的文章信息缓存区，然后将该文章信息整体入库，再从缓存区中删除该文章信息。

### 3.4 放封策略 ###

3.4.1 降低访问频率

1. 文章之间访问间隔 10 ~ 15秒
2. 爬取35个公众号后休息1~1.5小时
3. 今日爬取到信息的公众号，不再爬取

3.4.2 监测公众号是否有更新，只爬取有更新的公众号

1. 通过搜狗：库中取到公众号后，先通过搜狗验证、该公众号是否有更新，若出现验证码，则更换cookie。若所有cookie均更换完毕且还是有验证码，则先禁用搜狗微信一天。第二天搜狗微信仍不能用，主动发微信通知维护人员更新cookie池
2. 通过微信公众平台验证： 此处需要登录，并且需要扫描二维码（未实用）
3. 通过微信客户端
4. 调用顺序 搜狗 -> 微信公众平台 -> 微信客户端

### 3.5 公众号biz参数批量获取 ###

1. 可通过微信公众平台，新建图文链接时，可以加入超链接。点击查找文章，输入公众号名，分析数据包可得`fakeid`参数，即为biz值。如图：
    ![](https://i.imgur.com/qcS8YCh.png)<center>**图1**</center>
    ![](https://i.imgur.com/NoJV5KX.png)<center>**图2**</center>

2.可通过搜狗微信搜索公众号，进入公众号详情页，查看源代码，正则提取`var biz =`参数得知。如图：
    ![](https://i.imgur.com/hSWzsZD.png)<center>**图1**</center>
    ![](https://i.imgur.com/8DUpVQt.png)<center>**图2**</center>
    ![](https://i.imgur.com/lNeJ8on.png)<center>**图3**</center>


----------
技术交流
----
若大家有什么疑问或指教，可加我微信，一起讨论问题。
<div> 
<img src='https://i.imgur.com/HkECUT2.jpg' align = 'center' width = "250">
</div>

