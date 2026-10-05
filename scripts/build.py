"""Build a dependency-free, relative-URL GitHub Pages archive."""
import json
import html
import shutil
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
DATA = json.loads((ROOT / 'content/archive.json').read_text())
e = lambda value: html.escape(str(value), quote=True)

def validate():
    assert len(DATA['weeks']) == 8
    assert [w['number'] for w in DATA['weeks']] == list(range(1, 9))
    for w in DATA['weeks']:
        date.fromisoformat(w['planned_date']) if w['planned_date'] else None
        assert w['status'] in ['planned', 'in-progress', 'completed']
        if w['status'] == 'completed':
            assert w['records'], 'Completed weeks need evidence records'
        for r in w['records']:
            for key in ['id', 'title', 'date', 'start_time', 'end_time', 'timezone', 'public_attendees', 'venue', 'summary', 'agenda', 'contributions', 'decisions', 'next_steps', 'photos', 'artifacts', 'publication_reviewed']:
                assert key in r, f'Missing record field: {key}'
            assert r['publication_reviewed'] is True, 'Publish only reviewed records'
            assert r['timezone'] == 'Asia/Seoul'
            assert r['photos'] and r['artifacts'], 'Records need photographs and work products'
            date.fromisoformat(r['date'])
            for asset in r['photos'] + r['artifacts']:
                assert asset.get('label') and asset.get('url')
                assert asset['url'].startswith(('https://', 'assets/')), 'Use HTTPS or local assets'
                assert asset.get('publication_approved') is True
    for section in DATA['report']:
        assert section['status'] in ['pending', 'draft', 'verified']
        if section['status'] == 'verified':
            assert section['evidence'], 'Verified claims need evidence links'

def links(items):
    return ''.join(f'<li><a href="{e(i["url"])}">{e(i["label"])}</a></li>' for i in items)

def page(filename, title, active, content):
    nav = [('index.html', 'Archive'), ('weeks.html', 'Weekly work'), ('project.html', 'Project'), ('report.html', 'Final report'), ('about.html', 'About')]
    navigation = ''.join(f'<a href="{href}" {"aria-current=\"page\"" if label == active else ""}>{label}</a>' for href, label in nav)
    (OUT / filename).write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · Voice UX Lab</title><meta name="description" content="The Voice UX Lab work archive and final project report: eight weeks of voice-first AI research, development, and learning."><link data-language="en" rel="alternate" hreflang="en" href="{filename}"><link data-language="ko" rel="alternate" hreflang="ko" href="{filename.replace('.html', '.ko.html')}"><link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#main">Go to content</a><header><a class="wordmark" href="index.html">Voice UX Lab<span class="mark" aria-hidden="true">✳</span></a><nav aria-label="Main">{navigation}</nav><span class="cohort">2026 / Cohort 05</span></header><main id="main">{content}</main><footer><a href="index.html">Voice UX Lab</a><span>Eight-week work archive</span><span>Study team · Seoul</span><details class="language-picker"><summary aria-label="Select language">EN / English</summary><div class="language-options"><a data-language="en" href="{filename}" lang="en" hreflang="en">EN English</a><a data-language="ko" href="{filename.replace('.html', '.ko.html')}" lang="ko" hreflang="ko">KR 한국어</a></div></details></footer></body></html>''', encoding='utf-8')

def intro(kicker, title, description):
    return f'<div class="intro"><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="lede">{e(description)}</p></div>'

def week_cards():
    return ''.join(f'''<a class="week-card" href="week-{w['number']:02}.html"><div class="card-top"><span>Week {w['number']:02}</span><span class="status">{e('Plan' if w['status']=='planned' else w['status'].replace('-', ' '))}</span></div><h3>{e(w['title'])}</h3><p>{e(w['deliverable'])}</p><span class="card-date">{date.fromisoformat(w['planned_date']).strftime('%b %d, %Y') if w['planned_date'] else 'Date not available'}</span></a>''' for w in DATA['weeks'])

def record(r):
    photos = ''.join(f'<figure><img src="{e(p["url"])}" alt="{e(p.get("alt", p["label"]))}" loading="lazy"><figcaption>{e(p["label"])}</figcaption></figure>' for p in r['photos'])
    subsections = ''.join(f'<h3>{label}</h3><ul>'+''.join(f'<li>{e(item)}</li>' for item in r[key])+'</ul>' for label,key in [('Agenda & timeline','agenda'),('Contributions','contributions'),('Decisions & rationale','decisions'),('Next steps','next_steps')])
    return f'''<article class="record"><p class="eyebrow">{e(r['date'])} / {e(r['start_time'])}–{e(r['end_time'])} KST</p><h2>{e(r['title'])}</h2><dl><dt>Attendees</dt><dd>{e(', '.join(r['public_attendees']))}</dd><dt>Venue</dt><dd>{e(r['venue'])}</dd></dl><p>{e(r['summary'])}</p>{subsections}<h3>Work products</h3><ul>{links(r['artifacts'])}</ul><h3>Activity photos</h3>{photos}</article>'''

def build(localize=True):
    validate()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / 'styles.css', OUT)
    shutil.copy(ROOT / 'favicon.svg', OUT)
    if (ROOT / 'assets').exists(): shutil.copytree(ROOT / 'assets', OUT / 'assets')
    (OUT / '.nojekyll').touch()
    completed = sum(w['status'] == 'completed' for w in DATA['weeks'])
    records = [(w,r) for w in DATA['weeks'] for r in w['records']]
    latest = ''.join(f'<a class="entry" href="week-{w["number"]:02}.html"><span>{e(r["date"])}</span><h3>{e(r["title"])}</h3><span>Week {w["number"]:02}</span></a>' for w,r in sorted(records,key=lambda x:x[1]['date'],reverse=True)[:5]) or '<div class="empty"><h3>No activity records</h3><p>No activity records are available. The pages below contain the plan for each week.</p></div>'
    page('index.html','Work archive','Archive',intro('Voice UX study','Voice UX Lab','We will make a voice interface during this eight-week program. This website contains our plans, work records, and final report.')+f'''<div class="facts"><div><span>Program window</span><strong>Oct 3 – Nov 30, 2026</strong></div><div><span>Weekly sessions</span><strong>8 weeks · {len(records)} activity records</strong></div><div><span>Project concept</span><strong>Sona / Proposed</strong></div></div><section><div class="section-title"><h2>New work records</h2><a href="weeks.html">All weeks</a></div>{latest}</section><section><div class="section-title"><h2>Eight-week plan</h2><span>Week plans</span></div><div class="week-grid">{week_cards()}</div></section><a class="report-banner" href="report.html"><span class="eyebrow">Final report</span><h2>Final project report</h2><p>The report will contain the demo, design decisions, test results, and each team member’s comments.</p><span class="pill">Read the draft report</span></a>''')
    page('weeks.html','Weekly work','Weekly work',intro('Work archive','Weekly work','The team plan specifies Sunday meetings from 14:00 to 17:00 KST, near Yangjae Citizen’s Forest Station. The team uses Google Meet for online meetings. Individual meeting dates and the venue address are not available.')+f'<div class="week-grid">{week_cards()}</div><aside class="note"><h2>Activity record contents</h2><p>Each record contains the date, time, approved attendee names, location, activity details, photos, and work products. It also contains decisions, reasons, tasks, and plans for the next meeting. The team must also submit the official Notion activity log.</p></aside>')
    for w in DATA['weeks']:
        items = ''.join(f'<li>{e(item)}</li>' for item in w['activities'])
        body = intro(f'Week {w["number"]:02} / {('Plan' if w['status']=='planned' else w['status'].replace('-', ' '))}',w['title'],w['deliverable'])
        body += f'<div class="facts"><div><span>Session date</span><strong>{e(w["planned_date"] or 'Date not available')}</strong></div><div><span>Session time</span><strong>14:00–17:00 KST</strong></div><div><span>Meeting format</span><strong>In person / Google Meet</strong></div></div><section class="reading"><h2>Session plan</h2><ul>{items}</ul><h2>Activity records</h2>'
        body += ''.join(record(r) for r in w['records']) if w['records'] else '<div class="empty"><h3>No activity record</h3><p>This page contains the session plan. It does not give activity results. The team will add results after review.</p></div>'
        body += '</section><div class="pagination">'
        if w['number'] > 1: body += f'<a href="week-{w["number"]-1:02}.html">Previous week</a>'
        body += '<a href="weeks.html">All weeks</a>'
        if w['number'] < 8: body += f'<a href="week-{w["number"]+1:02}.html">Next week</a>'
        page(f'week-{w["number"]:02}.html',f'Week {w["number"]}: {w["title"]}','Weekly work',body+'</div>')
    page('project.html','Sona project','Project',intro('Proposed project','Sona','Sona is a proposed voice assistant. It will help users with physical tasks when they cannot use a screen or keyboard.')+'''<div class="project-hero"><span class="eyebrow">Research question</span><h2>When should the agent speak?</h2><p>We will examine speech timing, interruption, and error recovery. We will also examine when the agent should give help.</p></div><section class="split"><div><h2>Two proposed interfaces</h2></div><div><h3>Sona Mobile</h3><p>Sona Mobile is the proposed interface for users. Users will speak to the agent during a physical task. Camera input is optional.</p><h3>Sona Lab</h3><p>Sona Lab is the proposed interface for researchers. Researchers will select experiment settings and examine speech records, system events, and response times.</p></div></section><section class="split"><h2>Before development</h2><div><p>The team must select the user and task. It must specify the functions of the minimum viable product (MVP). It must also select the test measures and system design.</p><p>The tests can measure response time and task completion. They can also show whether users can interrupt the agent and correct errors. This archive has no test results.</p><a class="pill" href="report.html">Read the report</a></div></section>''')
    report_body = intro('Final report / Draft','Project report'.replace('<br>',' '),'The team will use the weekly records to complete this report. Each claim about a result must have evidence.')
    report_body += '<div class="report-layout"><nav class="toc" aria-label="Report sections">'+''.join(f'<a href="#{s["id"]}">{i:02} {e(s["title"])}</a>' for i,s in enumerate(DATA['report'],1))+'</nav><div>'
    for i,s in enumerate(DATA['report'],1):
        report_body += f'<section class="report-section" id="{s["id"]}"><p class="eyebrow">{i:02} / {e(s["status"])}</p><h2>{e(s["title"])}</h2><p>{e(s["guidance"])}</p>'
        report_body += ''.join(f'<p>{e(p)}</p>' for p in s['paragraphs']) or '<p class="pending">The team must add content and evidence.</p>'
        if s['evidence']: report_body += f'<h3>Supporting evidence</h3><ul>{links(s["evidence"])}</ul>'
        report_body += '</section>'
    page('report.html','Final project report','Final report',report_body+'</div></div>')
    about_extra = '''<section class="split"><h2>Voice as an interface</h2><div><p>The team will examine voice as an alternative to a screen and keyboard. The study includes real-time speech and tool calls.</p><p>The agent must identify the task and keep information from the conversation. When the user changes the task, the agent must change its response. Sona remains a proposed concept. The team will select the project topic in week 3.</p><h3>Tools & preparation</h3><p>The study uses the OpenAI Realtime API and Codex. Use a laptop with a microphone, speakers, and Wi-Fi. Make sure you have OpenAI, GitHub, and Notion accounts. Experience with Codex and ChatGPT Voice Mode can help.</p></div></section><section class="split"><h2>Shared learning</h2><div><p>IT’s Study is an AI study network. Team members examine technical questions and do exercises together.</p><p>Activity records will contain new knowledge, tools, questions, and discussion results. They will also contain preparation tasks for the next meeting.</p><h3>Study lead</h3><p>Hyung-Taik Choi is part of Hyundai Motor Group’s Robotics LAB. He does work on robotics technology, products, and user experience.</p><a href="https://linkedin.com/in/htcrefactor">Leader’s LinkedIn profile</a></div></section><section class="split"><h2>Project output plan</h2><div><ul><li>GitHub Pages project introduction and work archive</li><li>GitHub organization and repository</li><li>Developer documentation</li><li>Presentation slides</li><li>Demo videos</li></ul><p>The archive and repository are available. The team will add links to documents, slides, and demo videos when they are available.</p></div></section><section class="split"><h2>Activity-log guide</h2><div><p>The Notion guide specifies an offline team orientation and an offline last meeting. Each meeting must last at least 90 minutes. Each log must contain the date, time, attendees, location, activity details, and evidence.</p><p>Send the last activity log by December 7, 2026. After the first and last meeting reports, the leader must send an email to the organizer. This website does not replace the official Notion record.</p></div></section><section class="split"><h2>Source pages</h2><div><ul><li><a href="https://swits.notion.site/5-IT-s-Study-810d39944fb982f694e98115c6df0a25">IT’s Study cohort 5 activity hub</a></li><li><a href="https://swits.notion.site/UX-Voice-UX-Lab-Voice-First-AI-Agent-3bbd39944fb9809992f0dab0fa461c34">Voice UX Lab study brief</a></li><li><a href="https://swits.notion.site/3ebd39944fb98024b2c5fd33f27e8f96">Voice UX Lab activity-log guide</a></li></ul><p>We read the public source pages on October 5, 2026. The calendar entries were not available. We did not add session dates or activity results without source data.</p></div></section>'''
    page('about.html','About the lab','About',intro('Voice UX Lab / Seoul','About Voice UX Lab'.replace('<br>',' '),'We will examine voice interfaces and make an AI agent. This archive will contain our work records.')+'''<section class="split"><h2>The program</h2><div><p>Voice UX Lab is part of OpenAI × IT’s Study, cohort 5. Team members must give approval for their public profiles.</p><p>The program period is October 3 to November 30, 2026. The team plan specifies Sunday meetings from 14:00 to 17:00 KST, near Yangjae Citizen’s Forest Station. Google Meet is available for online meetings. Individual meeting dates and the venue address are not available.</p><p>This website contains the team’s work. It is not an official OpenAI website.</p></div></section><section class="split"><h2>Work archive</h2><div><p>Weekly records contain our work and the reasons for our decisions. The final report will contain the design, demo, results, and team members’ comments.</p><p>The team will publish only approved content. Private team storage contains restricted materials, raw recordings, contact details, attendance data, and consent records.</p></div></section>''' + about_extra)
    if localize:
        from i18n import korean_page
        for source in list(OUT.glob('*.html')):
            (OUT / source.name.replace('.html', '.ko.html')).write_text(korean_page(source.read_text()), encoding='utf-8')
    print(f'Built {len(list(OUT.glob("*.html")))} pages in {OUT}')

if __name__ == '__main__': build()
