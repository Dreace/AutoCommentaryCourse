# coding=utf-8
import json
import os
import random
import re
import traceback
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import bs4
import requests
import yaml

Max = 0
Min = 0
Summarize = ""


def login(session, username, password):
    try:
        login_url = "http://zxpj.nuc.edu.cn"
        vcode_url = "http://zxpj.nuc.edu.cn/kaptcha"
        flag = True
        while flag:
            vcode = session.get(vcode_url).content
            with open("vcode.jpg","wb") as vcode_file:
                vcode_file.write(vcode)
            vcode_image = mpimg.imread("vcode.jpg")
            plt.imshow(vcode_image)
            plt.axis('off')
            plt.show()
            vcode_text = raw_input("验证码：")
            post_data = {
                "username": username,
                "password": password,
                "kaptcha": vcode_text
            }
            html = session.post(login_url, data=post_data, timeout=5).content.decode("utf-8")
            if html.find(u"验证码错误") != -1:
                print ("验证码错误")
            else:
                flag = False
        if html.find(u"评课任务") != -1:
            return session, html
        elif html.find(u"账号密码错误") != -1:
            return False, "账号密码错误"
        else:
            return False, "登陆失败"
    except:
        print(traceback.format_exc())
        return False, ""


def start():
    global Max, Min, Summarize
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "Host": "zxpj.nuc.edu.cn",
        "Origin": "http://zxpj.nuc.edu.cn",
        "Referer": "http://zxpj.nuc.edu.cn/login",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/73.0.3683.86Safari/537.36"}
    base_url = "http://zxpj.nuc.edu.cn/login"
    proxies = {}
    if os.path.exists("config.yaml"):
        yaml_file = open("config.yaml", encoding='UTF-8')
        y = yaml.load(yaml_file)
        if not y["Campus Network"]:
            proxies = {"http": "http://47.101.211.35:888", "https": "http://47.101.211.35:888"}
        username = y["Username"]
        password = y["Password"]
        Max = y["Max"]
        Min = y["Min"]
        Summarize = y["Summarize"]
    else:
        s = raw_input("是否已连接校园网（Y/N）：")
        if s != "y" and s != "Y":
            print ("需要校园网环境")
            return
            proxies = {"http": "http://47.101.211.35:888", "https": "http://47.101.211.35:888"}
        username = raw_input("账号：")
        password = raw_input("密码：")
        Max = raw_input("最大随机分数（默认 99）：")
        if Max == "":
            Max = 99
        else:
            Max = int(Max)
        Min = raw_input("最小随机分数（默认 80）：")
        if Min == "":
            Min = 80
        else:
            Min = int(Min)
        Summarize = raw_input("总结（默认 “无”）：")
        if Summarize == "":
            Summarize = u"无"
    session = requests.session()
    session.proxies = proxies
    r = session.get(base_url)
    headers["Cookie"] = "shiroCookie=" + session.cookies["shiroCookie"]
    session.headers = headers
    session, res = login(session, username, password)
    if session:
        print("登陆成功")
        soup = bs4.BeautifulSoup(res, "html.parser")
        div = soup.find_all("div", class_="am-active")[0]
        xxqs = div.find_all(class_="xxq")
        if len(xxqs) < 1:
            print("没有未完成任务")
            return
        print("即将进行 %s 个评教" % len(xxqs))
        i = 1
        for x in xxqs:
            print("开始第 %s 个" % i)
            commentary_course(session, x.string)
            print("完成\n")
            i += 1
    else:
        print(res)


def commentary_course(session, id):
    base_url = "http://zxpj.nuc.edu.cn/evaluateRet/selectInfoByEid/" + id
    post_url = "http://zxpj.nuc.edu.cn/evaluateRet/addEvaluate"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "zxpj.nuc.edu.cn",
        "Referer": "http://zxpj.nuc.edu.cn/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
    headers["Cookie"] = "shiroCookie=" + session.cookies["shiroCookie"]
    session.headers = headers
    r = session.get(base_url, ).content.decode("utf-8")
    res = re.search(u"<strong>授课人：</strong>(.*?)</div>", r)
    print(u"授课人：%s" % res.group(1))
    res = re.search(u"<strong>所授课程：</strong>(.*?)</div>", r)
    print(u"所授课程：%s" % res.group(1))
    soup = bs4.BeautifulSoup(r, "html5lib")
    eid = soup.find_all(id="eid")[0]["value"]
    trs = soup.find_all("tr")[1:-1]
    content = []
    for tr in trs:
        # print(tr)
        a = tr.find(rowspan="1").string
        item = tr.find(class_="am-form-contentid")["value"]
        score = random.randint(Min, Max)
        print(u"%s：%s" % (a, score))
        content.append({int(item): score})
    info = {}
    info["content"] = content
    info["eid"] = eid
    info["summarize"] = Summarize
    info_json = json.dumps(info)
    session.headers = {"Accept": "application/json, text/javascript, */*; q=0.01",
                       "Accept-Encoding": "gzip, deflate",
                       "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                       "Connection": "keep-alive",
                       "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "DNT": "1",
                       "Host": "zxpj.nuc.edu.cn",
                       "Origin": "http://zxpj.nuc.edu.cn",
                       "Referer": "http://zxpj.nuc.edu.cn/evaluateRet/selectInfoByEid/104979",
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
                       "X-Requested-With": "XMLHttpRequest"}
    headers["Cookie"] = "shiroCookie=" + session.cookies["shiroCookie"]
    r = session.post(post_url, data=info_json)
    print(r.content)


if __name__ == "__main__":
    start()
    raw_input(u"按任意键退出")
