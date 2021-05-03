from __future__ import print_function
import re
import sys
sys.path.append('..')
from HtmlTree import HtmlTree

class Html2MD(HtmlTree):
    """docstring for MarkdownBuilder"""
    TAGFUNCMAPPING = '_{}'

    def tranverse(self,node):
        childMD = list()
        for child in node.children:
            if Html2MD.isTag(child):
                childrenMD = self.tranverse(child)
                if childrenMD != '':childMD.append(childrenMD)
            elif Html2MD.isNavString(child):
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
        raise NotImplementedError





