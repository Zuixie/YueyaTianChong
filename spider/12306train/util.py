#! /usr/bin/env python

import datetime
import time

# moudel 
# str to num

def str_num(str):
    try:
        return int(str)
    except ValueError:
        return 0

def format_date(datestr, formatstr='%Y%m%d'):
    date = datetime.datetime.strptime(datestr, formatstr)
    return date.strftime('%Y-%m-%d')

def record_log(e):
    print '%s: %s'%(time.strftime('%Y-%m-%d %X', time.localtime(time.time())), e)         

if __name__ == '__main__':
    s = '20160608'
    print format_date(s)
