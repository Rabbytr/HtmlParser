from __future__ import print_function
import re
import bs4

class MarkdownBuilder(object):
    """docstring for MarkdownBuilder"""
    TAGFUNCMAPPING = '_{}'

    def __init__(self, html):
        super(MarkdownBuilder, self).__init__()
        self.html = html
        self.soup = bs4.BeautifulSoup(self.html, features="html.parser")

    def tranverse(self,node):
        childMD = list()
        for child in node.children:
            if isinstance(child,bs4.Tag):
                childrenMD = self.tranverse(child)
                if childrenMD != '':childMD.append(childrenMD)
            elif isinstance(child,bs4.NavigableString):
                string = child.string.strip()
                if string == '':continue
                childMD.append(string)

        return self._tackleTag(node,childMD)

    def _tackleTag(self,node,childMD):
        tag_name = node.name
        func = self.__class__.__dict__\
            .get(self.__class__.TAGFUNCMAPPING.format(tag_name))
        if func:
            return func(self,node,childMD)
        elif self.__class__.__dict__\
                .get(self.__class__.TAGFUNCMAPPING.format('h')) \
                    and re.match(r'^h[1-7]$',tag_name):
            return self._h(int(tag_name[-1]),node,childMD)
        else:
            return self._normal_tag(node,childMD)

    def _normal_tag(self,node,childMD):
        return '\n'.join(childMD)





