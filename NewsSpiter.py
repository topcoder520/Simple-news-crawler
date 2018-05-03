#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2018/5/2 0002 下午 1:30
# @Author : HaJi
# @File : NewsSpiter.py
from lxml import etree
import requests
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header

#-----------爬取网页内容-------------------

def getHTML(url):
    try:
        r = requests.get(url,timeout=30)
        r.raise_for_status()
        html = r.content.decode('utf-8')
        return html
    except Exception as e:
        print(e)
        return ''

def getDomElements(html,xpath):
    dom_tree = etree.HTML(html)
    elements = dom_tree.xpath(xpath)
    return elements


def getContent(url):
    html = getHTML(url)
    links = getDomElements(html, "//div[@class='newsList']/ul/li/a/@href")
    titles = getDomElements(html, "//div[@class='newsList']/ul/li/a/text()")
    content=""
    for index in range(len(links)):
        content = content+str(index+1)+'、'+titles[index] + ':<a href="'+links[index]+'" target="_blank" style="display:block;">' + links[index]+"</a>"
    return content

#----邮件发送方式有两种：25接口发送 以及ssl 465接口第三方账户发送。我这里使用的第三方账户，因为在25接口已经被阿里云和腾讯云服务器给封了，不能使用。
# --------------------邮件发送代码--------------------------
mailto_list = ['xxxx','xxxxx']  # 收件人(列表)
mail_host = "smtp.163.com"  # 使用的邮箱的smtp服务器地址，这里是163的smtp地址
mail_user = "xxxxxx"  # 第三方邮箱的用户名，例如163邮箱的用户名
mail_pass = "xxxx"  # 密码
mail_postfix = "163.com"  # 邮箱的后缀，网易就是163.com


def send_mail(to_list, sub, content):
    me = "早点新闻" + "<" + "xxxx" + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype='html',_charset='utf-8')
    msg['Subject'] = Header(sub,'utf-8')
    msg['From'] = Header(me,'utf-8')
    msg['To'] = Header(";".join(to_list),'utf-8')  # 将收件人列表以‘；’分隔
    try:
        server = smtplib.SMTP_SSL(mail_host,465)
        server.login(mail_user, mail_pass)  # 登录操作
        server.sendmail(me, to_list, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print('发送邮件失败:'+str(e))
        return False

#--------------------页面的URL---------------------------
def getUrl():
    now = datetime.datetime.now()
    yestoday = now + datetime.timedelta(days=-1)
    yeay = yestoday.year
    month  = yestoday.month
    day = yestoday.day
    if month < 10:
        month = '0'+str(month)
    if day < 10:
        day = '0'+str(day)

    url = 'http://news.ifeng.com/listpage/11502/{0}{1}{2}/1/rtlist.shtml'.format(yeay,month,day)
    print(url)
    return url


#----------------------计时器  每天发送一次邮箱-----------------------
def timer(h=0,m=0):
    while True:
        while True:
            now = datetime.datetime.now()
            if now.hour == h and now.minute == m:
                break
            time.sleep(20)

        content = getContent(getUrl())
        if len(content)==0:
            content = "获取凤凰网即时新闻失败，请查看后台代码是否有错！或者凤凰网即时新闻的页面是否改版!"

        if send_mail(mailto_list, "早点新闻邮件", content):  # 邮件主题和邮件内容
            # 这是最好写点中文，如果随便写，可能会被网易当做垃圾邮件退信
            print("done!")
        else:
            print("failed!")
        time.sleep(70)

#----------调用------------
try:
    timer(15,30) # 每天爬去新闻并发送邮件的时间
except Exception as e:
    print('exception:'+str(e))
