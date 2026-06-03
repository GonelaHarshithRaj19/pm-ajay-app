from html.parser import HTMLParser
from pathlib import Path

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.self_closing = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        if tag not in self.self_closing:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f'extra end tag </{tag}> at {self.getpos()}')
            return
        last, pos = self.stack.pop()
        if last != tag:
            self.errors.append(
                f'mismatched end tag </{tag}> at {self.getpos()}, expected </{last}> from {pos}'
            )

path = Path('templates/index.html')
html = path.read_text(encoding='utf-8')
parser = TagChecker()
parser.feed(html)
for err in parser.errors:
    print(err)
if parser.stack:
    print('unclosed tags:')
    for tag, pos in parser.stack[-50:]:
        print(tag, pos)
