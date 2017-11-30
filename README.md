微信公众号抓取
====
爬取范围
----
1. 公众号所有历史文章，及公众号信息
2. 文章信息包括：标题、作者、贴图、简介、内容、url、点赞数、评论数、评论信息
3. 公众号信息包括：账号名、认证信息、二维码、头像地址、简介

环境需求
----
1. nodejs
2. anyproxy
3. android模拟器
4. 微信app
5. python3.5
6. Elasticsearch2.4
7. oracle11g

环境配置
----
### 一、安装android模拟器（海马玩模拟器） ###
海马玩模拟器设置代理 需要长按链接的wifi那一栏，然后高级选项中可以设置代理


### 二、下载微信客户端 ###

### 三、安装证书 ###

### 四、安装nodejs ###
[https://nodejs.org/en/download/](https://nodejs.org/en/download/ "node官网")

### 五、安装anyproxy ###
1. 执行 `npm config set registry https://registry.npm.taobao.org` 设置npm淘宝镜像
2. 执行 `npm install -g anyproxy` 下载anyproxy
3. 替换node_modules\anyproxy\lib\rule_default.js

### 六、安装python3.5 ###

### 七、安装Elasticsearch2.4 ###
### 八、安装ES2.4 ###

数据结构
----
###一、 公众号表 ###
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


### 二、文章表 ###
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
