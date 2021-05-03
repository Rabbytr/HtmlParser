# -*- coding: utf-8 -*-
from __future__ import print_function
from HtmlTree import HtmlTree
import bs4
import re
import json
import urllib2
import urlparse
import sys
from copy import deepcopy
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf-8')

class JsonDict(object):
    @staticmethod
    def PageDict():
        return {
            'path': None,
            'query': None,
            'data_list':{
                'mainbody': [],
                'answer': [],
            },
        }

    @staticmethod
    def AnswerDict():
        return {
            'title':None,
            'answer_style':None,
            'step_answer':[],
            'step_answer_prefix':[],
            'long_answer':None,
            'intro_answer':[],
        }

    @staticmethod
    def afterProcess(page_dic):
        page_dic = deepcopy(page_dic)
        for ans in page_dic['data_list']['answer']:
            ans_content = None
            if len(ans.get('step_answer')) == 0:
                ans['long_answer'] = '\n'.join(ans['intro_answer'])
                ans['step_answer'] = ans['intro_answer'] = None
                ans['answer_style'] = 2
                ans_content = ans['long_answer']
            else:
                ans['answer_style'] = 3
                ans['step_answer_prefix'] = [u'step {}'.format(i+1) for i in range(len(ans.get('step_answer')))]
                ans['intro_answer'] = '\n'.join(ans['intro_answer'])
                ans['long_answer'] = None
                ans_content = ans['intro_answer'] + ' '.join(ans['step_answer_prefix'])

            page_dic['data_list']['mainbody'].append({'answer_content':ans_content})
        return page_dic

    @staticmethod
    def toJson(d):
        return json.dumps(d,ensure_ascii=False,indent=2)

class fuckMXX(HtmlTree):
    def XiaoMi(self):
        self.MainContent = self.soup.find('div',{"class": "mainWrapper"})
        hs = self.MainContent.find_all(re.compile(r'^h[23]$'))
        anses = [JsonDict.AnswerDict()]
        self._mi_tranverse(self.MainContent, anses)
        r = JsonDict.PageDict()
        r['data_list']['answer'] = anses[1:-1]
        print(JsonDict.toJson(JsonDict.afterProcess(r)))

    def HuaWei(self):
        title = self.soup.find('h1')
        ansdic = JsonDict.AnswerDict()
        ansdic['title'] = fuckMXX.gen2str(title.stripped_strings)
        self.MainContent = self.soup.find('div',id='jd-content')
        self._hw_tranverse(self.MainContent,ansdic)

        r = JsonDict.PageDict()
        r['data_list']['answer'] = [ansdic]
        print(JsonDict.toJson(JsonDict.afterProcess(r)))

    def _mi_is_que(self,node):
        if node.name in ['h2','h3']:
            return True
        elif node.name == 'h4' and ''.join(list(node.stripped_strings)).startswith(u'相关阅读'):
            return True
        return False

    def _mi_tranverse(self, node, anses):
        if isinstance(node,bs4.NavigableString):
            anses[-1]['intro_answer'].append(node)
            return
        tagname = node.name
        if self._mi_is_que(node):
            anses.append(JsonDict.AnswerDict())
            anses[-1]['title'] = ' '.join(list(node.strings))
            return
        elif tagname == 'li':
            anses[-1].get('step_answer').append(' '.join(list(node.stripped_strings)))
            return
        elif tagname == 'img':
            pass
        for child in node.children:
            self._mi_tranverse(child, anses)

    def _hw_tranverse(self, node, dic):
        if isinstance(node,bs4.NavigableString):
            if fuckMXX.usefulContent(node):dic['intro_answer'].append(node)
            return
        tagname = node.name
        if tagname == 'li':
            dic.get('step_answer').append(' '.join(list(node.stripped_strings)))
        for child in node.children:
            self._hw_tranverse(child,dic)

    @staticmethod
    def gen2str(g,sep=None):
        if sep == None:sep = ' '
        return sep.join(list(g))



if __name__ == '__main__':
    url = 'https://i.mi.com/guide/zh-CN/note/overview'
    # url = 'https://i.mi.com/guide/zh-CN/gallery/overview'
    # url = 'https://consumer.huawei.com/cn/support/content/zh-cn00733859/'

    html = urllib2.urlopen(url).read()

    # with open('./text.txt','r') as f:
    #     html = f.read()
        # f.write(html)

    fuck = fuckMXX(html)
    hostname = urlparse.urlparse(url).hostname
    if hostname == 'i.mi.com':
        fuck.XiaoMi()
    elif hostname == 'consumer.huawei.com':
        fuck.HuaWei()


