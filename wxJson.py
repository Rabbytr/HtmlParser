# -*- coding: utf-8 -*-
from __future__ import print_function
from HtmlTree import HtmlTree
import bs4
import re
import json
import urllib2
import urlparse
import sys
import time
import random
import logging
logging.basicConfig(level=logging.INFO)
from copy import deepcopy
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf-8')

class WXJson(object):
    DataListKey = ['h5_url', 'cpid', 'page_attribute', 'update',\
                   'content_id', 'page_type','category_id', '@type',\
                   'title', 'time_publish', 'time_modify','mainbody','answer','cover_img']
    @staticmethod
    def DataList():
        datalist = {i:None for i in WXJson.DataListKey}
        return datalist

    @staticmethod
    def ExtractInfo():
        return {
            'title':None,
            'answer_style':None,
            'step_answer':[],
            # 'step_answer_prefix':[],
            'long_answer':None,
            'intro_answer':[],
            'content':[],
            'imgurl':[],
        }

    @staticmethod
    def toJson(d):
        return json.dumps(d, ensure_ascii=False, indent=2)

class baseHtml2Json(HtmlTree):
    def __init__(self,*args,**kwargs):
        self.url = kwargs.get('url')
        kwargs.pop('url')
        super(baseHtml2Json, self).__init__(*args,**kwargs)

    def toJson(self):
        tmpinfos = self.getExtractInfos()
        result = list()
        for info in tmpinfos:
            datalist = WXJson.DataList()
            datalist['title'] = info['title']
            datalist['mainbody'] = [{'answer_content':''.join(info['content'])}]
            if 1:
                datalist['h5_url'] = datalist['content_id'] = self.url
                datalist['cpid'] = self.cpid
                datalist['page_attribute'] = datalist['update'] = 1
                datalist['page_type'] = 4
                datalist['category_id'] = 8
                datalist['@type'] = 'wxsearch_cpdata'
                datalist['time_publish'] = datalist['time_modify'] = int(time.time())
            answer = {}
            if len(info.get('step_answer')) == 0:
                answer['long_answer'] = ''.join(info['intro_answer'])
                answer['answer_style'] = 2
            else:
                answer['answer_style'] = 3
                answer['step_answer'] = info['step_answer']
                answer['step_answer_prefix'] = 'step'
                answer['intro_answer'] = ''.join(info['intro_answer'])
            datalist['answer'] = answer
            if len(info['imgurl']) != 0:
                datalist['cover_img'] = [{'cover_img_url':url,'cover_img_size':2} for url in info['imgurl']]
            else:
                del datalist['cover_img']
            result.append(datalist)
        # print (WXJson.toJson(result))
        return result

    def getExtractInfos(self):
        raise NotImplementedError

    @staticmethod
    def gen2str(g, sep=None):
        if sep == None: sep = ' '
        return sep.join(list(g))

class Xm2Json(baseHtml2Json):
    def getExtractInfos(self):
        self.cpid = 'auto_e19zniht4geblh5v0z'
        self.MainContent = self.soup.find('div',{"class": "mainWrapper"})
        hs = self.MainContent.find_all(re.compile(r'^h[23]$'))
        extinfos = [WXJson.ExtractInfo()]
        self._mi_tranverse(self.MainContent, extinfos)
        return [i for i in extinfos if len(i['content'])!=0 and i['title']!=u'相关阅读：']


    def _mi_is_que(self,node):
        if node.name in ['h2','h3']:
            return True
        elif node.name == 'h4' and ''.join(list(node.stripped_strings)).startswith(u'相关阅读'):
            return True
        return False

    def _mi_tranverse(self, node, extinfos):
        if isinstance(node,bs4.NavigableString):
            extinfos[-1]['intro_answer'].append(node)
            extinfos[-1]['content'].append(node)
            return
        tagname = node.name
        if self._mi_is_que(node):
            extinfos.append(WXJson.ExtractInfo())
            extinfos[-1]['title'] = ' '.join(list(node.strings))
            return
        elif tagname == 'li':
            s = ' '.join(list(node.stripped_strings))
            extinfos[-1].get('step_answer').append(s)
            extinfos[-1]['content'].append(s)
            return
        elif tagname == 'img':
            extinfos[-1].get('imgurl').append(urlparse.urljoin(self.url, node.get('src')))
        for child in node.children:
            self._mi_tranverse(child, extinfos)



class Hw2Json(baseHtml2Json):
    def getExtractInfos(self):
        self.cpid = 'auto_v28dvswtbwpup6j7tn'
        title = self.soup.find('h1')
        extinfo = WXJson.ExtractInfo()
        extinfo['title'] = Hw2Json.gen2str(title.stripped_strings)
        self.MainContent = self.soup.find('div', id='tkb-content')
        if self.MainContent is None:
            return list()
        self._hw_tranverse(self.MainContent, extinfo)
        # print (WXJson.toJson(extinfo))
        return [extinfo]

    def _hw_tranverse(self, node, dic):
        if isinstance(node,bs4.NavigableString):
            if Hw2Json.usefulContent(node):dic['intro_answer'].append(node)
            return
        tagname = node.name
        if tagname == 'li':
            dic.get('step_answer').append(' '.join(list(node.stripped_strings)))
        elif tagname == 'img':
            dic.get('imgurl').append(urlparse.urljoin(self.url,node.get('src')))
        elif tagname == 'style':
            return
        for child in node.children:
            self._hw_tranverse(child,dic)


class Ap2Json(baseHtml2Json):
    def getExtractInfos(self):
        self.cpid = 'auto_etipcnuy55pfi51479'
        self.MainContent = self.soup.find('body')
        if self.MainContent is None:
            return list()
        extinfos = [WXJson.ExtractInfo()]
        self._ap_tranverse(self.MainContent, extinfos)
        return [i for i in extinfos if len(i['content'])!=0 and i['title'] not in [u'进一步了解',u'Apple Footer',None]]

    def _ap_is_que(self,node):
        if node.name in ['h1','h2','h3']:
            return True
        # elif node.name == 'h4' and ''.join(list(node.stripped_strings)).startswith(u'相关阅读'):
        #     return True
        return False

    def _ap_tranverse(self, node, extinfos):
        if isinstance(node,bs4.NavigableString):
            if not Hw2Json.usefulContent(node):
                return
            extinfos[-1]['intro_answer'].append(node)
            extinfos[-1]['content'].append(node)
            return
        tagname = node.name
        if self._ap_is_que(node):
            extinfos.append(WXJson.ExtractInfo())
            extinfos[-1]['title'] = ' '.join(list(node.strings))
            return
        elif tagname == 'li':
            s = ' '.join(list(node.stripped_strings))
            extinfos[-1].get('step_answer').append(s)
            extinfos[-1]['content'].append(s)
            return
        elif tagname == 'img':
            w,h = node.get('width'),node.get('height')
            if ((w is not None) and int(w)>100) or ((h is not None) and int(h)>100):
                print (w,h)
                extinfos[-1].get('imgurl').append(urlparse.urljoin(self.url, node.get('src')))
        for child in node.children:
            self._ap_tranverse(child, extinfos)

if __name__ == '__main__':
    # url = 'https://i.mi.com/guide/zh-CN/note/overview'
    # # url = 'https://i.mi.com/guide/zh-CN/gallery/overview'
    # # url = 'https://consumer.huawei.com/cn/support/content/zh-cn00733859/'
    #
    # html = urllib2.urlopen(url).read()
    #
    # # with open('./text.txt','r') as f:
    # #     html = f.read()
    # # f.write(html)
    #
    # fuck = fuckMXX(html,url=url)
    #
    # fuck.toJson()

    MiUrl = list()
    HwUrl = list()
    ApURl = list()
    with open('urls.csv','r') as f:
        for line in f:
            url = line.split(',')[1]
            if not url.startswith('http'):continue
            hostname =  urlparse.urlparse(url).hostname
            if hostname == 'i.mi.com':MiUrl.append(url)
            elif hostname == 'consumer.huawei.com':HwUrl.append(url)
            elif hostname == 'support.apple.com':ApURl.append(url)

    MiUrl = [random.choice(MiUrl) for _ in range(5)]
    HwUrl = [random.choice(HwUrl) for _ in range(5)]
    ApURl = [random.choice(ApURl) for _ in range(5)]
    # for i in ApURl:print(i)

    results = list()

    for i,url in enumerate(MiUrl[:]):
        html = urllib2.urlopen(url).read()
        fuck = Xm2Json(html, url=url)
        r = fuck.toJson()
        results.extend(r)
        time.sleep(0.5)
        logging.info('XiaoMi: {:3}/{:3}'.format(i,len(MiUrl)))

    for i, url in enumerate(HwUrl[:]):
        html = urllib2.urlopen(url).read()
        fuck = Hw2Json(html, url=url)
        r = fuck.toJson()
        results.extend(r)
        time.sleep(0.5)
        logging.info('HwaWei: {:3}/{:3}'.format(i, len(HwUrl)))

    for i, url in enumerate(ApURl[:]):
        html = urllib2.urlopen(url).read()
        print(url)
        fuck = Ap2Json(html, url=url)
        r = fuck.toJson()
        results.extend(r)
        time.sleep(0.5)
        logging.info('Applee: {:3}/{:3}'.format(i, len(ApURl)))

    print(WXJson.toJson(results))
