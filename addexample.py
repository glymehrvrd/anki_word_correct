#/bin/python

import sqlite3
import re
import urllib
import requests
import json
import time
import wordsegment
from math import log10
import onlinedict.juku

if __name__=="__main__":
    eng=onlinedict.juku.JukuDictEngine()

    conn=sqlite3.connect('d:\dell\Documents\Anki\User 1\collection.anki2')
    for row in conn.execute('select id, sfld, flds from notes'):
        idd, word, flds = row

        tryed = 0
        while True:
            try:
                eng.query(word)
                examples=eng.html()
            except Exception as e:
                if tryed >= 3:
                    break
                tryed = tryed + 1
                print "[error] " + word
                time.sleep(1)
            else:
                print "[info] " + word
                fld_list = flds.split('\x1f')
                if len(fld_list)>8:
                    for i in range(8,len(fld_list)):
                        del fld_list[8]
                fld_list.append(examples)

                conn.execute('update notes set flds=? where id=?', ('\x1f'.join(fld_list), idd))
                conn.commit()
                break

    conn.close()