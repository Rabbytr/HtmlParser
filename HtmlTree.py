import bs4

class HtmlTree(object):
    def __init__(self, html):
        super(HtmlTree, self).__init__()
        self.html = html
        self.soup = bs4.BeautifulSoup(self.html, features="html.parser")

    @staticmethod
    def usefulContent(content):
        return False if content.strip() == '' else True

    @staticmethod
    def isTag(node):
        return True if isinstance(node,bs4.Tag) else False

    @staticmethod
    def isNavString(node):
        return True if isinstance(node, bs4.NavigableString) else False