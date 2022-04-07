# -*- coding: utf8 -*-
import requests
import json
import time
import random

# 填写cookie即可运行
'''
1、浏览器登入哔哩网站
2、访问 http://api.bilibili.com/x/space/myinfo
3、F12看到cookie的值粘贴即可
'''
#下面填入复制的cookie值
cookies = "" 

header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Accept":"application/json, text/plain, */*",
    "Sec-Fetch-Site":"same-site",
    "Sec-Fetch-Mode":"cors",
    "Sec-Fetch-Dest":"empty",
    "Referer":"https://www.bilibili.com/video/BV1hV411U71U?spm_id_from=444.41.0.0",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Accept-Encoding":"gzip, deflate, br",
}

# cookie转字典
def extract_cookies(cookies):
    global csrf
    cookies = dict([l.split("=", 1) for l in cookies.split("; ")])
    csrf = cookies['bili_jct']
    return cookies

#获取硬币数
def getCoin():
    cookie = extract_cookies(cookies)
    url = "http://account.bilibili.com/site/getCoin"
    r = requests.get(url, cookies=cookie).text
    j = json.loads(r)
    money = j['data']['money']
    return int(money)

#获取个人信息
def getInfo():
    global uid
    url = "http://api.bilibili.com/x/space/myinfo"
    cookie = extract_cookies(cookies)
    r = requests.get(url, cookies=cookie).text
    j = json.loads(r)
    if j['code']==0 :
        uid = j['data']['mid']
        level = j['data']['level']
        current_exp = j['data']['level_exp']['current_exp']
        next_exp = j['data']['level_exp']['next_exp']
        sub_exp = int(next_exp)-int(current_exp)
        days = int(int(sub_exp)/65)
        coin = getCoin()
        msg = "Welcome! Current level is "+str(level) + " ,Current experience are " + \
            str(current_exp)+",Not far from upgrading "+str(sub_exp) + \
            " ,need "+str(days)+" days"+"Remaining silver coins are "+str(coin)
        print(msg)
        Task()
    else :
        #todo 可以推送一条消息
        print(j['message'])

#获取推荐列表
def getVideo():
    random_page = random.randint(0, 167)
    url = "http://api.bilibili.cn/recommend?page="+str(random_page)
    cookie = extract_cookies(cookies)
    r = requests.get(url, cookies=cookie).text
    j = json.loads(r)
    return j

# 投币 分享5次
def Task():
    coin_num = getCoin()
    num = 5 #投币个数
    if coin_num <= num:
        num = coin_num
    coin_count = 0
    share_count = 0  # 分享次数
    for i in range(0,15):
        j = getVideo()
        list_len = len(j['list'])
        random_list = random.randint(1, list_len-1)
        bvid = j['list'][random_list]['bvid']
        aid = j['list'][random_list]['aid']
        print(str(i)+' ---- '+str(bvid)+' ---- '+str(aid))
        view(bvid)
        time.sleep(3)
        if share_count < 5:
            share_count = share_count + 1
            shareVideo(bvid)

        else:
            print('have shared viedo five times!')
        time.sleep(3)
        if coin_count < num:#投币个数限制 为5个
            coin_code = addCoin(aid)
            if coin_code == -99:
                return
        if coin_code == 1:
            coin_count = coin_count+1
        if coin_count == num:
            getExpLog()
            break
        print('----------------------')

# 观看视频【不会点赞投币】
def view(bvid):
    playedTime = random.randint(10, 100)
    url = "https://api.bilibili.com/x/click-interface/web/heartbeat"
    data = {
        'bvid': bvid,
        'played_time': playedTime,
        'csrf': csrf
    }
    cookie = extract_cookies(cookies)
    r = requests.post(url,headers = {}, data=data, cookies=cookie).text
    j = json.loads(r)
    code = j['code']
    if code == 0:
        print('watching viedo successful!')

    else:
        print('watching viedo failed!')

# 分享视频
def shareVideo(bvid):
    url = "https://api.bilibili.com/x/web-interface/share/add"
    data = {
        'bvid': bvid,
        'csrf': csrf
    }
    cookie = extract_cookies(cookies)
    r = requests.post(url, data=data, cookies=cookie, headers=header).text
    j = json.loads(r)
    code = j['code']
    if code == 0:
        print('share  successful!')

    else:
        print('share failed!')


# 投币函数
def addCoin(aid):
    coinNum = getCoin()
    if coinNum == 0:
        print('not enough coin !')
        return -99
    url = "http://api.bilibili.com/x/web-interface/coin/add"
    data = {
        'aid': aid,
        'multiply': 1,
        'select_like': 0,
        'cross_domain':'true',
        'csrf': csrf
    }
    cookie = extract_cookies(cookies)
    r = requests.post(url, data=data, cookies=cookie, headers = header).text
    j = json.loads(r)
    code = j['code']
    if code == 0:
        print(str(aid)+' toaddcoin successful !')
        return 1
    else:
        print(str(aid)+' toaddcoin failed!')
        return 0

#读一遍经验值记录
def getExpLog():
    time.sleep(3)
    today = time.strftime("%Y-%m-%d")
    cookie = extract_cookies(cookies)
    url = "https://api.bilibili.com/x/member/web/exp/log?jsonp=jsonp"
    r = requests.get(url, cookies=cookie).text
    todayLog = {}
    j = json.loads(r)
    for i in range(len(j['data']['list'])):
        item = j['data']['list'][i]
        if item['time'].find(today)!=-1:
            if todayLog.get(item['reason']) == None:
                todayLog.setdefault(item['reason'],int(item['delta']))
            else:
                todayLog[item['reason']] = (todayLog[item['reason']] + int(item['delta']))
    print(todayLog)

if __name__ == '__main__':
    getInfo()