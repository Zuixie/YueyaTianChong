#!/usr/bin/python
# encoding=utf-8

import requests
import re
import json
import MySQLdb
import util
import sys
import getopt

reload(sys)
sys.setdefaultencoding("utf-8")

SOFT_VERSION = '0.0.2'
util.record_log('run 12306train version:' + SOFT_VERSION)

# this is city code version will update
# https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8950

databasename = '12306train'
databasename_test = '12306train_test'
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'}
    
class TrainInfo:
    def __init__(self, from_station_name, to_station_name, start_train_date): 
        self.from_sname = from_station_name
        self.to_sname = to_station_name
        self.start_train_date = start_train_date
        self.station_name_text = '--'
        self.from_scode = self.__get_station_code(self.from_sname) #'SZH' # TODO 
        self.to_scode = self.__get_station_code(self.to_sname) #'VRH' # TODO
    
    def __get_station_code(self, name):
        s = re.search(u'\|'+name+'\|(.*?)\|', self.__get_station_jstext(), re.S)
        if s == None:
            util.record_log('error: {0} is not found!!'.format(name))
            return ''
        else:
            return s.group(1)
        
    def __get_station_jstext(self):
        if self.station_name_text == '--':
            r = requests.get(self.__get_station_jsurl(), verify = False, headers = headers)
            self.station_name_text = r.text
        return self.station_name_text
                        
    def __get_station_jsurl(self): # 获取station name的url
        url = 'https://kyfw.12306.cn/otn/lcxxcx/init'
        r = requests.get(url, verify = False, headers = headers)
        s = re.search('src="((.*?)station_name(.*?))"', r.text)
        return 'https://kyfw.12306.cn' + s.group(1)

    def getdatas(self):
        params = {'to_station':'VRH', 'from_station':'SZH', 'query_date':'2016-06-08', 'purpose_codes':'ADULT'}
        
        params['to_station'] = self.to_scode
        params['from_station'] = self.from_scode
        params['query_date'] = self.start_train_date
        url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=' +\
        params['purpose_codes'] + '&queryDate=' + params['query_date'] + '&from_station=' + params['from_station'] + '&to_station=' + params['to_station']
        try:
            response = requests.get(url, verify=False, headers = headers)
            decode_json = json.loads(response.text)
            if decode_json == -1:
                return []
            elif decode_json['data']['flag']: # 判断是否获取成功
                return decode_json['data']['datas']
            else:
                util.record_log(decode_json['data']['message'])
                return []
        except Exception,e:
            util.record_log(e)
            return []
    
    def showdatas(self, datas):
        no = 0
        for data in datas:
            no += 1
            self.__showdata(data, no)
        
    def savedatas(self, datas, dbname):
        try:
            self.db = MySQLdb.connect('localhost', 'root', '123456', dbname, charset='utf8')
            cursor = self.db.cursor()
            for data in datas:
                self.__savedata(data, cursor)
        except Exception,e:
            util.record_log(e)
        finally:
            self.db.close()
        
    def __showdata(self, data, no):
        print '%2d %s:%s - %s \t %s'%(no, data['station_train_code'], data['start_time'], data['arrive_time'], data['ze_num'])
    
    def __savedata(self, data, cursor):
        sql = '''insert into train (start_station_name, end_station_name, 
        from_station_name, from_time, to_station_name, to_time, use_time, 
        train_code, first_seat_num, second_seat_num, no_seat_num, train_start_date, 
        record_date, record_time) 
        values ('{0}','{1}','{2}','{3}','{4}','{5}',{6},'{7}',{8},{9},{10},'{11}', curdate(), curtime())'''.format(data['start_station_name'], data['end_station_name'], data['from_station_name'], data['start_time'], data['to_station_name'], data['arrive_time'], util.str_num(data['lishiValue']), data['station_train_code'], util.str_num(data['zy_num']), util.str_num(data['ze_num']), util.str_num(data['wz_num']), util.format_date(data['start_train_date']) );
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception,e:
            util.record_log(e)
            self.db.rollback()

def usage():
    help = '''
    example: 12306train.py -f 苏州 -t 温州 -d 2016-06-08 -m show 
    -h help
    -v version
    -f input from station name
    -t input to station name
    -d input search date
    -m model input(test, official, show):
        test        -save data to test db
        official    -save data to official db
        show        -show data in terminal
    '''
    print help


if __name__ == '__main__':
    from_station = '苏州'
    to_station = '温州'
    date = '2016-06-08'
    model = 'show'
    try:
        opt, args = getopt.getopt(sys.argv[1:],'vhf:t:d:m:',['from=', 'to=', 'date=', 'model='])
    except getopt.GetoptError:
        util.record_log('input error!!!')
        sys.exit(-1)
    
    for name, value in opt:
        if name in ('-v', '--version'):
            print 'version:' + SOFT_VERSION
            sys.exit(0) 
        if name in ('-h', '--help'):
            usage()
            sys.exit(0)
        if name in ('-d', '--date'):
            date = value
        if name in ('-f', '--from'):
            from_station = value
        if name in ('-t', '--to'):
            to_station = value
        if name in ('-m', '--model'):
            model = value                    
        
    train = TrainInfo(from_station, to_station, date)
    datas = train.getdatas()
    if model == 'official':
        train.savedatas(datas, databasename)
    elif model == 'test':
        train.savedatas(datas, databasename_test)
    else:
        train.showdatas(datas)