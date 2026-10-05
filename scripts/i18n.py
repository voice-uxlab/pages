"""Static Korean pages: native links preserve location and work without JavaScript."""
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import json

KO = json.loads((Path(__file__).resolve().parents[1] / 'content/ko.json').read_text())
BRANDS = {'Voice UX Lab','Sona Mobile','Sona Lab','✳','EN','KR','English','한국어'}

def translate(text):
    if not text.strip(): return text
    key = text.strip()
    if key in KO: return text.replace(key, KO[key])
    if key in BRANDS: return text
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', key): return text
    if key == '14:00–17:00 KST': return '14:00–17:00 한국 표준시'
    if key.endswith(' · Voice UX Lab'): return translate(key[:-15]) + ' · Voice UX Lab'
    m = re.fullmatch(r'Week (\d+): (.+)', key)
    if m: return f'{int(m[1])}주차: {translate(m[2])}'
    m = re.fullmatch(r'Week (\d+)( / (.+))?', key)
    if m: return f'{int(m[1])}주차' + (' / '+translate(m[3]) if m[3] else '')
    m = re.fullmatch(r'(\d{2}) / (.+)', key)
    if m: return m[1]+' / '+translate(m[2])
    m = re.fullmatch(r'(\d{2}) (.+)', key)
    if m: return m[1]+' '+translate(m[2])
    m = re.fullmatch(r'(\d+) planned · (\d+) completed', key)
    if m: return f'예정 {m[1]}회 · 완료 {m[2]}회'
    m = re.fullmatch(r'(Oct|Nov) (\d{2}), 2026', key)
    if m: return f'2026년 {10 if m[1]=="Oct" else 11}월 {int(m[2])}일'
    raise ValueError(f'Missing Korean translation: {key}')

class KoreanPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output=[]
        self.keep_text=False
    def handle_decl(self,decl): self.output.append('<!'+decl+'>')
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html': a['lang']='ko'
        if tag=='a' and 'data-language' in a: self.keep_text=True
        target = urlsplit(a.get('href', ''))
        if not target.scheme and not target.netloc and target.path.endswith('.html') and 'data-language' not in a:
            a['href'] = urlunsplit(target._replace(path=target.path.replace('.html', '.ko.html')))
        if tag=='meta' and a.get('name')=='description': a['content']=translate(a['content'])
        if 'aria-label' in a: a['aria-label']=translate(a['aria-label'])
        self.output.append('<'+tag+''.join(' '+k+(('="'+html.escape(v,quote=True)+'"') if v is not None else '') for k,v in a.items())+'>')
    def handle_endtag(self,tag):
        self.output.append('</'+tag+'>')
        if tag in ['a','summary']: self.keep_text=False
    def handle_data(self,text):
        self.output.append(html.escape(text if self.keep_text else translate(text),quote=False))

def korean_page(source):
    parser=KoreanPage()
    parser.feed(source)
    return ''.join(parser.output)
