# -*- coding: utf-8 -*-

# 我的Anki插件
# 作者：Glyme

# 在线词典模块->句酷词典插件

import os
import httplib
import urllib
import json
import re
from xml.dom.minidom import parseString
import odutils
from odutils import jinjaEnv

# 当前引擎名(以文件名作为引擎名)
engine = os.path.basename(__file__).replace(".py", "")
# 引擎显示名
name = u"句酷"

# 引擎类
class JukuDictEngine:

    def __init__(self):
        self.engine = engine
        self.name = name
        self.urlreg = re.compile(
            '\{url=.+?\}|\{highlight\}|\{/url\}|\{/highlight\}')
        # 引擎的Html模板
        self.htmlTemplate = jinjaEnv.from_string(u'{% for s in data.sent|toList %}<div style="color: #01259a">{{s.eng}}</div><div style="color: #000000">{{s.chr}}</div><br/>{% endfor %}')
        # 保存查询结果
        self.data = {}

    # 句酷单词查询
    def query(self, word, forceQuery=False):
        if word == None or word.strip() == "":
            return
        # 如果不要求强制查询，则优先本地数据库中查询；否则，优先从网络上查询
        if not forceQuery:
            js = odutils.getDictByKey("dict_query_%s_%s" % (self.engine, word))
            if js:
                self.data = json.loads(js)
                return
        # ------从句酷网站上查询------
        conn = httplib.HTTPConnection('xml.jukuu.com')
        params = urllib.urlencode({'q': word})
        headers = {
            "Referer": "http://www.jukuu.com/"}
        ok = False
        try:
            conn.request("GET", "/xml2lingose.php?" + params, None, headers)
            res = conn.getresponse()
            if res.status == 200:
                rootele = parseString(res.read()).documentElement
                # ------提取XML数据------
                rootele = odutils.xml2json(rootele)
                self.data = {'key': 'word', 'sent': []}
                for item in rootele['result']['item']:
                    self.data['sent'].append(
                        {'chr': self.urlreg.sub('', item['chr']), 'eng': self.urlreg.sub('', item['eng'])})

                odutils.setDictByKey(
                    "dict_query_%s_%s" % (self.engine, word), json.dumps(self.data))
                ok = True
        except:
            pass
        finally:
            conn.close()
        # 网络查询失败
        if not ok and forceQuery:
            js = odutils.getDictByKey("dict_query_%s_%s" % (self.engine, word))
            if js:
                self.data = json.loads(js)
                ok = True
        # 最终还是失败
        if not ok:
            self.data = {}

    # 生成用来渲染的Html
    def html(self):
        if self.data:
            return self.htmlTemplate.render(data=self.data)
        else:
            raise Exception("no good!")


