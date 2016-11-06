import xmltodict
import sys
sys.path.append('../')
from db import Tag,Word

with open('wordbook.xml',encoding='utf8') as fd:
   doc=xmltodict.parse(fd.read())

for item in doc['wordbook']['item']:
   num=Tag.query_count(tag=item['tags'])
   if num==0:
       tag=Tag(tag=item['tags'])
       Tag.insert(tag)
   else:
       tag=Tag.query_one(tag=item['tags'])
   word=Word(word=item['word'],explanation=item['trans'])
   word.tags.append(tag)
   Word.insert(word)
