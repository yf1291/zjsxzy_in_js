# encoding: utf-8
# 微指数爬虫
import requests
import urllib
import pandas as pd

WORDS_FILE = 'D:/workspace/zjsxzy_in_js/website/word_heat/data/words.txt'
DATA_DIR = 'D:/Data/wei_index/'

def search_name(name):
    url_format = "http://data.weibo.com/index/ajax/hotword?word={}&flag=nolike&_t=0"
    cookie_header = {
                     "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
                     "Referer":"http://data.weibo.com/index?sudaref=www.google.com"
                   }

    urlname = urllib.quote(name)
    first_requests = url_format.format(urlname)
    codes = requests.get(first_requests,headers=cookie_header).json()
    if codes["data"] == 'null':
        return None
    ids = codes["data"]["id"]

    header = {
        "Connection":"keep-alive",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept": "*/*",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Referer": "http://data.weibo.com/index/hotword?wid={}&wname={}".format(ids,urlname),
        "Content-Type": "application/x-www-form-urlencoded",
        "Host":"data.weibo.com"
    }

    #获取日期
    date_url = "http://data.weibo.com/index/ajax/getdate?month=60&__rnd=1498190033389"
    dc = requests.get(date_url,headers=header).json()
    edate, sdate = dc["edate"],dc["sdate"]

    #数据返回
    codes = requests.get("http://data.weibo.com/index/ajax/getchartdata?wid={}&sdate={}&edate={}"\
                         .format(ids,sdate,edate),headers=header).json()
    return codes

def main():
    with open(WORDS_FILE, 'r') as fp:
        words = fp.readlines()
    for word in words:
        res = search_name(word)
        word = word.strip().decode('utf-8')
        if res == None:
            print('error')
            continue
        print word
        # print res
        df = pd.DataFrame(res['yd'])
        df.index = pd.to_datetime(df['daykey'])
        fname = '%s/%s_yd.xlsx'%(DATA_DIR, word)
        df[['pc', 'mobile']].to_excel(fname)

        df = pd.DataFrame(res['zt'])
        df.index = pd.to_datetime(df['day_key'])
        fname = u'%s/%s_zt.xlsx'%(DATA_DIR, word)
        df[['value']].to_excel(fname)

if __name__ == '__main__':
    main()
