#! /usr/bin/python

import requests
import re
import time
import sys
import threading

## use to check guo.lu and download pic
# Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36


class Guolu:
    index_rul = 'http://guo.lu'
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'}

    def __init__(self, url):
        self.index_rul = url.strip()
    
    def getIndexHtml(self):
        return requests.get(self.index_rul, headers = self.headers).text
    
    def getIndexUrllist(self, html):
        links = re.findall('http://guo.lu/\d+', html, re.S)
        return {}.fromkeys(links).keys() # grep the same url
    
    def getPost0Source(self, index):
        return re.search('<div id="post0">(.*?)</div>', index, re.S).group(1)
    
    def getUpdataTime(self, post0):
        return re.search('<p>(.*?)</p>', post0, re.S).group(1)
    def getUpdataTitle(self, post0):
        return re.search('/>(.*?)</a>', post0, re.S).group(1)
    def getUpdataUrl(self, post0):
        return re.search('(http://guo.lu/\d+)', post0, re.S).group(1)

    def getDetailHtml(self, url):   
        return requests.get(url, headers = self.headers).text
    
    def getDetailImgUrls(self, html):
        picdiv = re.search('<div class="images">(.*?)</div>', html, re.S).group(1)
        return re.findall('href="(.*?)"', picdiv, re.S)
    
    def savePicture(self, url, path):
        print 'start downlload ' + url
        pic = requests.get(url, headers = self.headers).content
        fp = open(path + url.split('/')[-1] , 'wb')
        fp.write(pic)
        fp.close()
        print ' | end '+ url
    
if __name__ == '__main__':
    
    g = Guolu('http://guo.lu')
    html = g.getIndexHtml()
    post0 = g.getPost0Source(html)
    
    updatatime = g.getUpdataTime(post0)
    updatatitle = g.getUpdataTitle(post0)
    updataurl = g.getUpdataUrl(post0)
    
    print updatatitle
    print updatatime
    print updataurl
    
    argclen = len(sys.argv)
    if argclen >= 2:   
        stime = time.time()
    
        detail = g.getDetailHtml(updataurl)
        imgurls = g.getDetailImgUrls(detail)
        threads = []
        for imgurl in imgurls:
            t = threading.Thread(target=g.savePicture, args=(imgurl, sys.argv[1]))
            t.start()
            threads.append(t)
            #g.savePicture(imgurl, sys.argv[1])
        for th in threads:
            th.join()
        
        etime = time.time()
        print 'use time %f second'%(etime - stime)
