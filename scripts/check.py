"""Check the generated site's links, fragments, and document essentials."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import build

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1 = 0
        self.main = 0
        self.lang = False
        self.viewport = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'html': self.lang = bool(a.get('lang'))
        if tag == 'meta' and a.get('name') == 'viewport': self.viewport = True
        if tag == 'h1': self.h1 += 1
        if tag == 'main': self.main += 1
        if tag == 'img': assert a.get('alt'), 'Image needs alt text'
        for attr in ['href','src']:
            if attr in a: self.links.append(a[attr])

build.validate()
docs = {}
for path in build.OUT.glob('*.html'):
    doc = Document()
    doc.feed(path.read_text())
    assert doc.h1 == 1 and doc.main == 1 and doc.lang and doc.viewport, path.name
    docs[path.name] = doc
assert len(docs) == 13
checked = 0
for name, doc in docs.items():
    for link in doc.links:
        parts = urlsplit(link)
        if parts.scheme or parts.netloc: continue
        assert not parts.path.startswith('/'), 'Root-relative URLs break project sites'
        target = unquote(parts.path) or name
        assert (build.OUT / target).exists(), f'{name}: missing {target}'
        if parts.fragment:
            assert parts.fragment in docs[target].ids, f'{name}: missing fragment {link}'
        checked += 1
assert not list(build.OUT.rglob('*.md')), 'Only public site output may be deployed'
assert not list(build.OUT.rglob('*.json')), 'Private or authoring records must not leak into output'
print(f'Passed: {len(docs)} documents, {checked} local links/assets/fragments; /pages/ compatible.')
