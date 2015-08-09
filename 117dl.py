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

def getPageNumber(page_url):    # 通过下载地址判断一共有多少页
    allPage = []
    p = requests.get(page_url)
    pagesoup = BeautifulSoup(p.text,'lxml')
    page = pagesoup.find(attrs={'class':'wp-pagenavi'}) # 直接查找attrs判断页面
    if page == None:    # 如果page值为空则返回默认页面
        number_of_page = 0
        allPage.append(page_url)
        return allPage
    else:
        number_of_page = int(page.contents[0].contents[-3].string)  # page不为空时返回多少页面
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

def getSourcePageNumber():
    source = requests.get('http://www.177pic.info/html/category/tt/page/1')
    sourcesoup = BeautifulSoup(source.text,'lxml')
    sourcepage = sourcesoup.find(attrs={'class':'wp-pagenavi'})
    source_page_number = int(sourcepage.contents[-2]['href'].splite('/')[-1])
    return source_page_number


def main(): # main 模块
    if os.path.exists('recode') == False:
        print('第一次运行，建立页面记录')
        os.popen('touch recode')    # 判断是否首次执行脚本
        with open ('recode','w') as f:
            f.write('http://www.177pic.info/html/category/tt/page/1')
    else:
        print('读取上次停止下载页面')
        with open('recode','r') as f:
            trecode = f.readline()  # 读取记录
            recode = trecode.split('/')
            print('上次停止在第{0}页'.format(recode))
    url = 'http://www.177pic.info/html/category/tt'
    total_page = getSourcePageNumber   
    url_list = []
    for i in range(int(recode[-1]), total_page):    # 根据记录选择开始页面
        url_list.append(url+'/page/'+str(i+1))
    tmp = os.popen('ls').readlines()
    allcomic = []
    for i in tmp:
        allcomic.append(i[:-1]) # 读取目录列表，保存以便判断漫画是否下载
    del tmp
    for y in url_list:
        print('正在下载: ',y)
        with open('recode','w') as f:
            f.write(y)
        comic = getSource(y)
        for x in comic:
            # print(comic[x],end=' ')
            # print((comic[x]+'.cbr'  in allcomic))
            if ((comic[x]+'.cbr') in allcomic) == True:
                print(comic[x],'已经存在。')
            else:
                print('正在下载: ',comic[x])
                if (os.path.exists(comic[x])) == True:
                    print('目录已经存在。')
                    os.chdir(comic[x])
                    downloadComic(x)
                    command = 'rar a -r -s -m5 -df \''+comic[x]+'.cbr\' \''+comic[x]+'\''
                    os.system(command)
                    os.system('clear')
                else:
                    os.mkdir(comic[x])
                    os.chdir(comic[x])
                    downloadComic(x)
                    command = 'rar a -r -s -m5 -df \''+comic[x]+'.cbr\' \''+comic[x]+'\''
                    os.system(command)
                    os.system('clear')

if __name__ == '__main__':
    main(url_list)
