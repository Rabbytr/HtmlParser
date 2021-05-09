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
import logging
logging.basicConfig(level=logging.INFO)
from copy import deepcopy
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf-8')

class WXJson(object):
    DataListKey = ['h5_url', 'cpid', 'page_attribute', 'update',\
                   'content_id', 'page_type','category_id', '@type',\
                   'title', 'time_publish', 'time_modify','mainbody','answer']
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
            'step_answer_prefix':[],
            'long_answer':None,
            'intro_answer':[],
            'content':[],
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
            datalist['mainbody'] = {'answer_content':''.join(info['content'])}
            if 1:
                datalist['h5_url'] = datalist['content_id'] = self.url
                datalist['cpid'] = 'auto_e19zniht4geblh5v0z'
                datalist['page_attribute'] = datalist['update'] = 1
                datalist['page_type'] = 4
                datalist['category_id'] = 8
                datalist['@type'] = 'wxsearch_cpdata'
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
            result.append(datalist)
        # print (WXJson.toJson(result))
        return result

    def getExtractInfos(self):
        raise NotImplementedError

class fuckMXX(baseHtml2Json):
    def getExtractInfos(self):
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
            pass
        for child in node.children:
            self._mi_tranverse(child, extinfos)

    @staticmethod
    def gen2str(g,sep=None):
        if sep == None:sep = ' '
        return sep.join(list(g))

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
    with open('urls.csv','r') as f:
        for line in f:
            url = line.split(',')[1]
            if not url.startswith('http'):continue
            if urlparse.urlparse(url).hostname == 'i.mi.com':
                MiUrl.append(url)

    results = list()
    for i,url in enumerate(MiUrl[:]):
        html = urllib2.urlopen(url).read()
        fuck = fuckMXX(html, url=url)
        r = fuck.toJson()
        results.extend(r)
        time.sleep(0.5)
        logging.info('{:3}/{:3}'.format(i,len(MiUrl)))
    print(WXJson.toJson(results))
