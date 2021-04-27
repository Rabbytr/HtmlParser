# HtmlParser

自己写的HtmlTree修修改改不如直接把bs4核心拷到项目里面

### Example

见`main.py`文件，继承类`MarkdownBuilder`

```python
class yourMDB(MarkdownBuilder):
    def _h(self, lv,node, childMD):
        return '#' * lv + ' ' + '\n'.join(childMD)

		def _p(self,node,childMD):
        return ' '.join(childMD)
      
     ...
```

* 在子类中实现对**不同标签**的特殊处理



> `def` `_tagname`(`node:bs4.Tag`,`childMD:'子节点返回的字符串'`)->`String`

#### 使用

```
mdb = myMDB(html)
markdownString = mdb.tranverse(mdb.soup.body)
```

目前代码还比较粗糙

`tranverse(mdb.soup.body)`这种垃圾api让人看着想揍人