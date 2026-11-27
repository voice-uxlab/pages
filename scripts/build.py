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
            assert r['summary'].strip(), 'Records need a substantive public summary'
            date.fromisoformat(r['date']) if r['date'] else None
            for asset in r['photos'] + r['artifacts']:
                assert asset.get('label') and asset.get('url')
                assert asset['url'].startswith(('https://', 'assets/')), 'Use HTTPS or local assets'
                assert asset.get('publication_approved') is True
    case = DATA['case_study']
    assert all(case[name]['sections'] and case[name]['links'] for name in ['project', 'research'])
    assert [event['week'] for event in case['timeline']] == list(range(1, 9))
    for event in case['timeline']:
        date.fromisoformat(event['date'])
    for section in DATA['report']:
        assert section['status'] in ['pending', 'draft', 'verified']
        if section['status'] == 'verified':
            assert section['evidence'], 'Verified claims need evidence links'

def links(items):
    return ''.join(f'<li><a href="{e(i["url"])}">{e(i["label"])}</a></li>' for i in items)

def page(filename, title, active, content):
    nav = [('index.html', 'Archive'), ('weeks.html', 'Weekly work'), ('project.html', 'Project'), ('research.html', 'Research'), ('report.html', 'Final report'), ('about.html', 'About')]
    navigation = ''.join(f'<a href="{href}" {"aria-current=\"page\"" if label == active else ""}>{label}</a>' for href, label in nav)
    (OUT / filename).write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · Voice UX Lab</title><meta name="description" content="The Voice UX Lab work archive and final project report: eight weeks of voice-first AI research, development, and learning."><link data-language="en" rel="alternate" hreflang="en" href="{filename}"><link data-language="ko" rel="alternate" hreflang="ko" href="{filename.replace('.html', '.ko.html')}"><link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#main">Go to content</a><header><a class="wordmark" href="index.html">Voice UX Lab<span class="mark" aria-hidden="true">✳</span></a><nav aria-label="Main">{navigation}</nav><span class="cohort">2026 / Cohort 05</span></header><main id="main">{content}</main><footer><a href="index.html">Voice UX Lab</a><span>Eight-week work archive</span><span>Study team · Seoul</span><details class="language-picker"><summary aria-label="Select language">EN / English</summary><div class="language-options"><a data-language="en" href="{filename}" lang="en" hreflang="en">EN English</a><a data-language="ko" href="{filename.replace('.html', '.ko.html')}" lang="ko" hreflang="ko">KR 한국어</a></div></details></footer></body></html>''', encoding='utf-8')

def intro(kicker, title, description):
    return f'<div class="intro"><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="lede">{e(description)}</p></div>'

def orientation_card():
    return ('<a class="entry orientation-entry" href="orientation.html">'
            '<span>2026-10-11</span><h3>Team orientation</h3><span>Kickoff deck</span></a>')

def week_cards():
    return ''.join(f'''<a class="week-card" href="week-{w['number']:02}.html"><div class="card-top"><span>Week {w['number']:02}</span><span class="status">{e('Plan' if w['status']=='planned' else w['status'].replace('-', ' '))}</span></div><h3>{e(w['title'])}</h3><p>{e(w['deliverable'])}</p><span class="card-date">{date.fromisoformat(w['planned_date']).strftime('%b %d, %Y') if w['planned_date'] else 'Date not available'}</span></a>''' for w in DATA['weeks'])

def record(r):
    photos = ''.join(f'<figure><img src="{e(p["url"])}" alt="{e(p.get("alt", p["label"]))}" loading="lazy"><figcaption>{e(p["label"])}</figcaption></figure>' for p in r['photos'])
    subsections = ''.join(f'<h3>{label}</h3><ul>'+''.join(f'<li>{e(item)}</li>' for item in r[key])+'</ul>' for label,key in [('Agenda & timeline','agenda'),('Contributions','contributions'),('Decisions & rationale','decisions'),('Next steps','next_steps')])
    timing = f"{r['date']} / {r['start_time']}–{r['end_time']} KST" if r['date'] and r['start_time'] and r['end_time'] else (r['date'] or 'Date not available')
    details = ''.join(report_section(s) for s in r.get('sections', []))
    if r.get('structured_report'):
        subsections = ''
    return f'''<article class="record"><p class="eyebrow">{e(timing)}</p><h2>{e(r['title'])}</h2><dl><dt>Venue</dt><dd>{e(r['venue'])}</dd></dl><p>{e(r['summary'])}</p>{subsections}{details}{('<h3>Work products</h3><ul>'+links(r['artifacts'])+'</ul>') if r['artifacts'] else ''}{('<h3>Activity photos</h3>'+photos) if r['photos'] else ''}</article>'''

def report_table(table):
    def cell(value):
        if isinstance(value, list):
            return '<ol>'+''.join('<li>'+e(item)+'</li>' for item in value)+'</ol>'
        return e(value)
    head = '<thead><tr>'+''.join('<th scope="col">'+e(h)+'</th>' for h in table['headers'])+'</tr></thead>'
    rows = '<tbody>'+''.join('<tr>'+''.join('<td aria-label="'+e(label)+'">'+cell(c)+'</td>' for label,c in zip(table['headers'], row))+'</tr>' for row in table['rows'])+'</tbody>'
    return '<div class="report-table" role="region" tabindex="0" aria-label="'+e(table['label'])+'"><table>'+head+rows+'</table></div>'

def report_section(s, level=3):
    paragraphs = ''.join('<p>'+e(p)+'</p>' for p in s.get('paragraphs', []))
    items = '<ul>'+''.join('<li>'+e(i)+'</li>' for i in s['items'])+'</ul>' if s.get('items') else ''
    tables = ''.join(report_table(t) for t in s.get('tables', []))
    after = ''.join(report_section(part, min(level+1, 6)) for part in s.get('after', []))
    return '<section class="record-section"><h'+str(level)+'>'+e(s['title'])+'</h'+str(level)+'>'+paragraphs+items+tables+after+'</section>'

def topic_sections(sections):
    return ''.join(report_section(s, level=2) for s in sections)

def timeline():
    return '<ol class="timeline">' + ''.join(
        f'<li><time datetime="{e(event["date"])}">{e(event["date"])}</time>'
        f'<div><h3><a href="week-{event["week"]:02}.html">{e(event["title"])}</a></h3>'
        f'<p>{e(event["description"])}</p></div></li>'
        for event in DATA['case_study']['timeline']) + '</ol>'

def architecture_overview():
    # High-level responsibilities only. Avoid operational or credential detail.
    return '''<section class="architecture-panel"><h3>Architecture overview</h3>
    <div class="architecture-grid">
      <div><strong>Mobile web</strong><span>React / TypeScript</span></div>
      <div><strong>Speech and reasoning</strong><span>OpenAI Realtime / WebRTC</span></div>
      <div><strong>Speech synthesis</strong><span>Typecast</span></div>
      <div><strong>Application state and reports</strong><span>FastAPI / PostgreSQL</span></div>
    </div></section>'''

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
    latest = ''.join(f'<a class="entry" href="week-{w["number"]:02}.html"><span>{e(r["date"] or "Date not available")}</span><h3>{e(r["title"])}</h3><span>Week {w["number"]:02}</span></a>' for w,r in sorted(records,key=lambda x:x[1]['date'] or '',reverse=True)[:5]) or '<div class="empty"><h3>No activity records</h3><p>No activity records are available. The pages below contain the plan for each week.</p></div>'
    page('index.html','Work archive','Archive',
         intro('Voice UX study','Voice UX Lab','We built a voice-first prototype during this eight-week program. This archive documents the work and our learning.')
         + f'''<div class="facts"><div><span>Program window</span><strong>Oct 3 – Nov 30, 2026</strong></div>
         <div><span>Weekly sessions</span><strong>8 weeks · {len(records)} activity records</strong></div><div><span>Project concept</span><strong>Ten Minutes / Working prototype</strong></div></div>
         <div class="feature-grid">
           <a class="feature-tile project-tile" href="project.html"><span class="eyebrow">Current project</span><h2>Ten Minutes</h2><p>{e(DATA["case_study"]["project"]["description"])}</p><span class="pill">Explore the project</span></a>
           <a class="feature-tile research-tile" href="research.html"><span class="eyebrow">Study findings</span><h2>Voice UX research</h2><p>{e(DATA["case_study"]["research"]["description"])}</p><span class="pill">Read the research</span></a>
         </div>
         <section><div class="section-title"><h2>Development milestones</h2><span>As of November 27, 2026</span></div>{timeline()}</section>
         <section><div class="section-title"><h2>New work records</h2><a href="weeks.html">All weeks</a></div>{latest}</section>
         <section><div class="section-title"><h2>Eight-week plan</h2><span>Week plans</span></div><div class="week-grid">{week_cards()}</div></section>
         <a class="report-banner" href="report.html"><span class="eyebrow">Final report</span><h2>Final project report</h2><p>The report documents work through November 27. Results and limitations are separated from plans.</p><span class="pill">Read the current draft report</span></a>''')
    page('weeks.html','Weekly work','Weekly work',intro('Work archive','Weekly work','Meetings are in person near Yangjae Citizen’s Forest Station. Weeks 1 and 2 ran from 14:00 to 18:00 KST. Weeks 3–8 run from 14:00 to 17:00 KST.')+orientation_card()+f'<div class="week-grid">{week_cards()}</div><aside class="note"><h2>Activity record contents</h2><p>Each record contains the date, time, approved attendee names, location, activity details, photos, and work products. It also contains decisions, reasons, tasks, and plans for the next meeting. The team must also submit the official Notion activity log.</p></aside>')
    for w in DATA['weeks']:
        items = ''.join(f'<li>{e(item)}</li>' for item in w['activities'])
        body = intro(f'Week {w["number"]:02} / {('Plan' if w['status']=='planned' else w['status'].replace('-', ' '))}',w['title'],w['deliverable'])
        body += f'<div class="facts"><div><span>Session date</span><strong>{e(w["planned_date"] or 'Date not available')}</strong></div><div><span>Session time</span><strong>14:00–{'18:00' if w["number"] <= 2 else '17:00'} KST</strong></div><div><span>Meeting format</span><strong>In person</strong></div></div><section class="weekly-records">'
        if w['status'] != 'completed': body += f'<h2>Session plan</h2><ul>{items}</ul>'
        body += '<h2>Activity records</h2>'
        body += ''.join(record(r) for r in w['records']) if w['records'] else '<div class="empty"><h3>No activity record</h3><p>This page contains the session plan. It does not give activity results. The team will add results after review.</p></div>'
        body += '</section><div class="pagination">'
        if w['number'] > 1: body += f'<a href="week-{w["number"]-1:02}.html">Previous week</a>'
        body += '<a href="weeks.html">All weeks</a>'
        if w['number'] < 8: body += f'<a href="week-{w["number"]+1:02}.html">Next week</a>'
        page(f'week-{w["number"]:02}.html',f'Week {w["number"]}: {w["title"]}','Weekly work',body+'</div>')
    project = DATA['case_study']['project']
    research = DATA['case_study']['research']
    project_body = intro(project['kicker'],project['title'],project['description'])
    project_body += f'<p class="status-note">{e(project["status"])}</p>'
    project_body += topic_sections(project['sections'])
    project_body += '<section class="resource-list"><h2>Project resources</h2><ul>'+links(project['links'])+'</ul></section>'
    project_body += '<aside class="note"><p>The early concept and historic meeting decisions remain in the weekly archive.</p><a class="pill" href="weeks.html">All weeks</a></aside>'
    page('project.html','Ten Minutes','Project',project_body)
    research_body = intro(research['kicker'],research['title'],research['description'])
    research_body += topic_sections(research['sections'])
    research_body += '<section class="resource-list"><h2>Related records</h2><ul>'+links(research['links'])+'</ul></section>'
    page('research.html','Voice UX research','Research',research_body)
    report_body = intro('Final report / Draft','Project report'.replace('<br>',' '),'Study records and technical artifacts inform this draft. Claims about outcomes must have evidence.')
    report_body += '<div class="report-layout"><nav class="toc" aria-label="Report sections">'+''.join(f'<a href="#{s["id"]}">{i:02} {e(s["title"])}</a>' for i,s in enumerate(DATA['report'],1))+'</nav><div>'
    for i,s in enumerate(DATA['report'],1):
        report_body += f'<section class="report-section" id="{s["id"]}"><p class="eyebrow">{i:02} / {e(s["status"])}</p><h2>{e(s["title"])}</h2>'
        report_body += ''.join(f'<p>{e(p)}</p>' for p in s['paragraphs']) or '<p class="pending">The team must add content and evidence.</p>'
        if s['id'] == 'architecture': report_body += architecture_overview()
        report_body += ''.join(report_section(part, level=3) for part in s.get('sections', []))
        if s['evidence']: report_body += f'<h3>Supporting evidence</h3><ul>{links(s["evidence"])}</ul>'
        report_body += '</section>'
    page('report.html','Final project report','Final report',report_body+'</div></div>')
    about_extra = '''<section class="split"><h2>Voice as an interface</h2><div><p>The team explored real-time speech, application-controlled actions and the balance between voice and screen interaction.</p><p>The agent must identify the task and keep information from the conversation. At the third meetup, the team selected voice tarot.</p><h3>Tools & preparation</h3><p>The project uses OpenAI Realtime, Typecast, React, FastAPI and PostgreSQL. Codex supported collaborative development.</p></div></section><section class="split"><h2>Shared learning</h2><div><p>IT’s Study is an AI study network. Team members examine technical questions and do exercises together.</p><p>Team members explored different workstreams and learned from collaborative design and software development.</p></div></section><section class="split"><h2>Project output plan</h2><div><ul><li>GitHub Pages project introduction and work archive</li><li>GitHub organization and repository</li><li>Developer documentation</li><li>Presentation slides</li><li>Demo videos</li></ul><p>The archive, public repository and technical documentation are available. Approved media and presentation materials will be added when available.</p></div></section><section class="split"><h2>Activity-log guide</h2><div><p>The Notion guide specifies an offline team orientation and an offline last meeting. Each meeting must last at least 90 minutes. Each log must contain the date, time, attendees, location, activity details, and evidence.</p><p>Send the last activity log by December 7, 2026. After the first and last meeting reports, the leader must send an email to the organizer. This website does not replace the official Notion record.</p></div></section><section class="split"><h2>Source pages</h2><div><ul><li><a href="https://swits.notion.site/5-IT-s-Study-810d39944fb982f694e98115c6df0a25">IT’s Study cohort 5 activity hub</a></li><li><a href="https://swits.notion.site/UX-Voice-UX-Lab-Voice-First-AI-Agent-3bbd39944fb9809992f0dab0fa461c34">Voice UX Lab study brief</a></li><li><a href="https://swits.notion.site/3ebd39944fb98024b2c5fd33f27e8f96">Voice UX Lab activity-log guide</a></li></ul><p>The initial archive used public source pages from October 5, 2026. Later meeting records use supplied transcripts and confirmed activity details.</p></div></section>'''
    page('about.html','About the lab','About',intro('Voice UX Lab / Seoul','About Voice UX Lab'.replace('<br>',' '),'We built a voice-first prototype during this eight-week program. This archive documents the work and our learning.')+'''<section class="split"><h2>The program</h2><div><p>Voice UX Lab is part of OpenAI × IT’s Study, cohort 5. Team members must give approval for their public profiles.</p><p>The program runs from October 3 to November 30, 2026. Meetings are in person near Yangjae Citizen’s Forest Station. Weeks 1 and 2 ran from 14:00 to 18:00 KST. Weeks 3–8 run from 14:00 to 17:00 KST.</p><p>This website contains the team’s work. It is not an official OpenAI website.</p><p>The final regular meeting is planned for November 29; the official activity period ends November 30. The cohort presentation is scheduled for December 16.</p></div></section><section class="split"><h2>Work archive</h2><div><p>Public records include reviewed meeting summaries and asynchronous project milestones.</p><p>The team will publish only approved content. Private team storage contains restricted materials, raw recordings, contact details, attendance data, and consent records.</p></div></section>''' + about_extra)
    if localize:
        from i18n import korean_page
        for source in list(OUT.glob('*.html')):
            (OUT / source.name.replace('.html', '.ko.html')).write_text(korean_page(source.read_text()), encoding='utf-8')
    from build_orientation import publish_orientation
    publish_orientation(ROOT, OUT, localize)
    print(f'Built {len(list(OUT.glob("*.html")))} pages in {OUT}')

if __name__ == '__main__': build()

