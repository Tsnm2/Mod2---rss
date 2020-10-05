import time
from dateutil import parser
import FilterHTML
from bs4 import BeautifulSoup


class FeedEntry:

    # def __init__(self, feed_title, feed_url, entry_title, entry_url, entry_author, entry_content, entry_published):
    # self.feed_title = feed_title
    # self.feed_url = feed_url
    # self.entry_title = entry_title
    # self.entry_url = entry_url
    # self.entry_author = entry_author
    # self.entry_content = entry_content
    # self.entry_published = entry_published

    def __init__(self, name, url, entry):
        entry_attr = {}
        entry_attr_dict = {'title': ['title'],
                           'link': ['link'],
                           'author': ['author'],
                           'summary': ['summary'],
                           'published': ['published', 'readingdatetime']}
        for key in entry_attr_dict:
            for attr in entry_attr_dict[key]:
                try:
                    entry_attr[key] = entry[attr]
                    break
                except Exception:
                    entry_attr[key] = ""
                    continue
        self.feed_title = name
        self.feed_url = url
        self.entry_title = entry_attr['title']
        self.entry_url = entry_attr['link']
        self.entry_author = entry_attr['author']
        self.entry_content = entry_attr['summary']
        # self.entry_published = entry_attr['published']
        self.entry_published = int(time.mktime(parser.parse(entry_attr['published']).timetuple()))

    def generate_post(self, post_format):
        post_attributes = {
            'feed_title': self.feed_title,
            'feed_url': self.feed_url,
            'entry_title': self.entry_title,
            'entry_url': self.entry_url,
            'entry_author': self.entry_author,
            'entry_content': self.entry_content,
            'entry_published': self.entry_published,
            'newline': "\n"
        }
        if 'entry_content' in post_format:
            post_attributes['entry_content'] = self.content_filter(self.entry_content)
        return post_format.format(**post_attributes)

    def __str__(self):
        return f"Feed Title: {self.feed_title}" + \
               f"\nFeed URL: {self.feed_url}" + \
               f"\nEntry Title: {self.entry_title}" + \
               f"\nEntry URL: {self.entry_url}" + \
               f"\nEntry Author: {self.entry_author}" + \
               f"\nEntry Content: {self.entry_content}" + \
               f"\nEntry Published: {self.entry_published}"

    def content_filter(self, content):
        whitelist = {
            'a': {
                'href': 'url'
            },
            'b': {
            },
            'i': {
            },
            'code': {
            },
            'pre': {
            },
            'p': {
            },
            'br': {
            }
        }
        soup = BeautifulSoup(content, "html.parser")
        for elem in soup.find_all(["p", "br"]):
            elem.replace_with(elem.text + "\n\n")
        content = str(soup)
        filtered_html = FilterHTML.filter_html(content, whitelist)
        return filtered_html

    def markdown_escape(self, content):
        escape_dict = {
            '\\': '\\\\',
            '`': '\\`',
            '*': '\\*',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '[': '\\[',
            ']': '\\]',
            '(': '\\(',
            ')': '\\)',
            '#': '\\#',
            '+': '\\+',
            '-': '\\-',
            '.': '\\.',
            '!': '\\!'
        }
        for item in escape_dict:
            content = content.replace(item, escape_dict[item])
        return content

    def get_entry_published(self):
        return self.entry_published

    def get_entry_title(self):
        return self.entry_title

    def get_entry_content(self):
        return self.entry_content

    def get_entry_url(self):
        return self.entry_url


if __name__ == '__main__':
    url = "https://a.jiemian.com/index.php?m=article&a=rss"
    title = "Jiemian"
    post_format = "{entry_title} {entry_url}"
    chat_id = "0"
    fe = FeedEntry(title, url, "test", "https://test.com", "me", "content", "0")
    print(fe.generate_post("{feed_title} :{entry_author}"))
