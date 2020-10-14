#!/usr/bin/env python

import ply.lex as lex
import re

class FlewLexer(object):

    def __init__(self):
        self.call_count = 0

    tokens = (
        'H_MYCALL',
        'H_MYGRID',
        'CALL',
        'DATE',
        'BAND',
        'FREQ',
        'MODE',
        'GRID',
        'NAME',
        'TIME',
        'NUMBER'
    )

    t_BAND      = r'(160|80|60|40|30|20|15|12|10|6|2)[mM]'
    t_FREQ      = r'[0-9]\.[0-9]{1,3}'
    t_MODE      = r'(cw|ssb|rtty|fm|usb|lsb|ft8|jt65)'
    t_GRID      = r'#[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{0,2}[0-9]{0,2}'
    t_TIME      = r'[0-9]{2}\:{0,1}[0-9]{2}'
    t_NUMBER    = r'\d+'

    def t_H_MYCALL(self,t):
        r'mycall [a-zA-Z0-9]{1,3}[0123456789][a-zA-Z0-9]{0,3}[a-zA-Z]\n+'
        t.value = re.split(' |\n',t.value)[1]
        return t
    
    def t_H_MYGRID(self,t):
        r'mygrid [a-zA-Z]{2}[0-9]{2}[a-zA-Z]{2}[0-9]{0,2}'
        t.value = re.split(' |\n',t.value)[1]
        return t
    
    def t_CALL(self,t):
        r'\d?[a-z]{1,2}\d{1,4}[a-z]{1,3}'
        self.call_count += 1
        return t

    def t_DATE(self,t):
        r'date ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'
        t.value = re.split(' |\n',t.value)[1]
        return t

    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
    
    t_ignore  = ' \t'

    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self,data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: 
                break
            print(tok)