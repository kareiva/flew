import re
from app import app
from app.FlewLexer import FlewLexer

f = FlewLexer()
f.build(reflags=re.IGNORECASE)
f.test('''
        mycall ly2en
        date 2020-10-14 80m cw
        d4c 
        ly1000qt 589
        4z4dx
        ly2en   #ko24pq
    ''')