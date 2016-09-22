#/bin/python

import sqlite3
import re

words=frozenset()
with open("words.txt") as f:
	words=frozenset([line.strip() for line in f])

def correct_word(s):
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

words_re=re.compile('([a-z]+\s+)+([a-z]+\s*)+\s')

print correct_word('''li mp and soft''')

exit(0)
conn=sqlite3.connect('d:\dell\Documents\Anki\User 1\collection.anki2')
for row in conn.execute('select id, flds from notes'):
	idd, fld = row
	s_list=[m.group(0) for m in words_re.finditer(fld)]
	flag = False
	for s in s_list:
		corr, corr_s=correct_word(s)

		if corr:
			flag=True
			fld=fld.replace(s,corr_s)
	if flag:
		conn.execute('update notes set flds=? where id=?', (fld, idd))
		print fld

conn.commit()
conn.close()