#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'wudaown'

#
#   应朋友要求做了一个脚本从 www.177pic.info/ 下载所有中文漫画
#   已经挂服务器上面慢慢跑了，没有上面用处，一次性的东西
# 

import requests
from bs4 import BeautifulSoup
from io import BytesIO
import os


def getSource(url):     # 读取完整页面 返回一个漫画名称和下载地址的mapping
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'lxml')
    link = soup.find_all('h2')  # bs4 找 h2 tag
    dl = []
    title = []
    for x in link:
        title.append(x.contents[0]['title'][13:]) # h2 tag 下还有其他tag读取内容
        dl.append(x.contents[0]['href'])
    comic = dict(zip(dl,title))
    return(comic)

def getPageNumber(page_url):        #通过下载地址去的一共多少页面
    allPage = []
    p = requests.get(page_url)
    pagesoup = BeautifulSoup(p.text,'lxml')
    page = pagesoup.find(attrs={'class':'wp-pagenavi'}) # 直接透过attrs找需要内容
    number_of_page = int(page.contents[0].contents[-3].string)
    for i in range(number_of_page):
        allPage.append(page_url+'/'+str(i+1))
    return allPage


def getImglink(page):       # 去的图片直链
    imgdr = []
    p = requests.get(page)
    imgsoup = BeautifulSoup(p.text,'lxml')
    imglink = imgsoup.findAll('img')    # 找html中所有图片
    for y in imglink:
        if 'alt' in y.attrs:        # 剔除没有编号的图片
            imgdr.append(y['src'])
    return  imgdr



def downloadComic(comic_link):      # 下载图片
    imglist = []
    comic_page = getPageNumber(comic_link)
    for x in comic_page:
        tmp = getImglink(x)
        for y in tmp:
            imglist.append(y)
    for z in range(len(imglist)):      # 用range是因为要重命名图片为后面打包做准备
        img = requests.get(imglist[z-1])
        with open(str(z)+'.jpg', 'wb') as f: # 图片wb模式写入 binary
            f.write(img.content)
    os.chdir('..')

url = 'http://www.177pic.info/html/category/tt'
total_page = 125
url_list = []                                       # 一共125页
for i in range(total_page):
    url_list.append(url+'/page/'+str(i+1))

def main(url): # main模块
    for y in url:
        comic = getSource(y)
        for x in comic:
            os.mkdir(comic[x])
            os.chdir(comic[x])  # 建立漫画文件夹，利用mapping完成
            downloadComic(x)
            command = 'rar a -r -s -m5 -df \''+comic[x]+'.cbr\' \''+comic[x]+'\'' # 打包指令，直接打包成cbr
            os.system(command)  # 系统执行

if __name__ == '__main__':
    main(url_list)
