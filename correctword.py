#/bin/python

import sqlite3
import re
import urllib
import requests
import json
import time
import wordsegment
from math import log10

words=frozenset()
with open("words.txt") as f:
    words=frozenset([line.strip() for line in f])


def correct_google(s):
    def extract_tag(s):
        flag=False
        ret=[]
        tmp=""
        for c in s:
            if flag and c=="<":
                ret.append(tmp)
                tmp=""
                flag=False
            if flag:
                tmp+=c
            if not flag and c==">":
                flag=True
        return ret

    url="http://www.google.co.jp/complete/search?client=serp&hl=zh-CN&gs_rn=64&gs_ri=serp&cp=13&gs_id=3ms&q=%s&xhr=t"
    url=url%urllib.quote(s)

    while True:
        try:
            req=requests.get(url, timeout=10)

            js=json.loads(req.text)
            flag=False
            if "o" in js[2]:
                s1=js[2]["p"]
                s2=js[2]["o"]
                t1=extract_tag(s1)
                t2=extract_tag(s2)
                for i in range(len(t1)):
                    if(t1[i].replace(" ","")==t2[i]):
                        print t1[i], t2[i]
                        s=s.replace(t1[i], t2[i])
                        flag=True
            break
        except Exception, ex:
            print str(ex)
            time.sleep(1)

    return flag,s

def correct_dict(s):
    prev=""
    w_list=s.split(" ")[0:-1]
    rst=[]
    flag=False
    for w in w_list:
        if not w.lower() in words and (prev+w).lower() in words:
            del rst[-1]
            rst.append(prev+w)
            flag=True
        else:
            rst.append(w)
        prev=w

    return flag, ' '.join(rst)

def correct_segmentation(s):

    def generate_sentense(words):
        yield words, 0
        for i in range(1,len(words)):
            tmp=words[:]
            tmp[i-1:i+1]=[tmp[i-1]+tmp[i]]
            yield tmp, i

    def score_sentense((words, pos)):
        words=['<s>',]+words
        ret=5 if pos==0 else 0
        prev="<s>"
        for i in range(1,len(words)):
            ret+=log10(wordsegment.score(words[i],prev))
            prev=words[i]
        return ret, pos

    lower_s = s.lower()
    words = lower_s.split(' ')

    max_s, pos=max(generate_sentense(words),key=score_sentense)
    max_s=" ".join(max_s)

    if pos!=0:
        ret=s.split(' ')
        ret[pos-1:pos+1]=[ret[pos-1]+ret[pos]]
        ret=' '.join(ret)
        print ret
        return True, ret

    return False, s

if __name__=="__main__":
    words_re=re.compile('(\w+\s+)+\w+')

    conn=sqlite3.connect('d:\dell\Documents\Anki\User 1\collection.anki2')
    for row in conn.execute('select id, flds from notes'):
        idd, fld = row
        s_list=[m.group(0) for m in words_re.finditer(fld)]
        flag = False
        for s in s_list:
            # corr, corr_s=correct_dict(s)
            corr, corr_s=correct_segmentation(s)

            if corr:
                flag=True
                fld=fld.replace(s,corr_s)
        if flag:
            conn.execute('update notes set flds=? where id=?', (fld, idd))
            conn.commit()


    conn.close()