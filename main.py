from html2md import MarkdownBuilder
import urllib2
import urlparse


class myMDB(MarkdownBuilder):
    def _h(self, lv,node, childMD):
        return '#' * lv + ' ' + '\n'.join(childMD)

    def _ol(self,node, childMD):
        return '\n'.join([u'{}. {}'.format(i + 1, v) for i, v in enumerate(childMD)])

    def _ul(self,node, childMD):
        return '\n'.join([u'* {}'.format(v) for v in childMD])

    def _img(self,node,childMD):
        return u'![{}]({})'.format(node.get('alt'),urlparse.urljoin(url,node.get('src')))

    def _a(self,node,childMD):
        return u'[{}]({})'.format('\n'.join(childMD),node.get('href'))

    def _p(self,node,childMD):
        return ' '.join(childMD)

    def _li(self,node,childMD):
        return self._p(node,childMD)

    def _span(self,node,childMD):
        return self._p(node,childMD)

if __name__ == '__main__':
    url = 'https://support.apple.com/zh-cn/HT204088'
    # html = urllib2.urlopen(url).read()

    with open('./text.txt','r') as f:
        html = f.read()
        # f.write(html)

    mdb = myMDB(html)
    r = mdb.tranverse(mdb.soup.body)

    print(r.encode('utf-8'))