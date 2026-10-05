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
        date.fromisoformat(w['planned_date'])
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
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · Voice UX Lab</title><meta name="description" content="The Voice UX Lab work archive and final project report: eight weeks of voice-first AI research, development, and learning."><link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#main">Skip to content</a><header><a class="wordmark" href="index.html">Voice UX Lab<span class="mark" aria-hidden="true">✳</span></a><nav aria-label="Main">{navigation}</nav><span class="cohort">2026 / Cohort 05</span></header><main id="main">{content}</main><footer><a href="index.html">Voice UX Lab</a><span>Eight weeks. A lasting record.</span><span>Independent study team · Seoul</span></footer></body></html>''', encoding='utf-8')

def intro(kicker, title, description):
    return f'<div class="intro"><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="lede">{e(description)}</p></div>'

def week_cards():
    return ''.join(f'''<a class="week-card" href="week-{w['number']:02}.html"><div class="card-top"><span>Week {w['number']:02}</span><span class="status">{e(w['status'].replace('-', ' '))}</span></div><h3>{e(w['title'])}</h3><p>{e(w['deliverable'])}</p><span class="card-date">{date.fromisoformat(w['planned_date']).strftime('%b %d, %Y')}</span></a>''' for w in DATA['weeks'])

def record(r):
    photos = ''.join(f'<figure><img src="{e(p["url"])}" alt="{e(p.get("alt", p["label"]))}" loading="lazy"><figcaption>{e(p["label"])}</figcaption></figure>' for p in r['photos'])
    subsections = ''.join(f'<h3>{label}</h3><ul>'+''.join(f'<li>{e(item)}</li>' for item in r[key])+'</ul>' for label,key in [('Agenda & timeline','agenda'),('Contributions','contributions'),('Decisions & rationale','decisions'),('Next steps','next_steps')])
    return f'''<article class="record"><p class="eyebrow">{e(r['date'])} / {e(r['start_time'])}–{e(r['end_time'])} KST</p><h2>{e(r['title'])}</h2><dl><dt>Attendees</dt><dd>{e(', '.join(r['public_attendees']))}</dd><dt>Venue</dt><dd>{e(r['venue'])}</dd></dl><p>{e(r['summary'])}</p>{subsections}<h3>Work products</h3><ul>{links(r['artifacts'])}</ul><h3>Activity photos</h3>{photos}</article>'''

def build():
    validate()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / 'styles.css', OUT)
    shutil.copy(ROOT / 'favicon.svg', OUT)
    if (ROOT / 'assets').exists(): shutil.copytree(ROOT / 'assets', OUT / 'assets')
    (OUT / '.nojekyll').touch()
    completed = sum(w['status'] == 'completed' for w in DATA['weeks'])
    records = [(w,r) for w in DATA['weeks'] for r in w['records']]
    latest = ''.join(f'<a class="entry" href="week-{w["number"]:02}.html"><span>{e(r["date"])}</span><h3>{e(r["title"])}</h3><span>Week {w["number"]:02}</span></a>' for w,r in sorted(records,key=lambda x:x[1]['date'],reverse=True)[:5]) or '<div class="empty"><h3>The work starts here.</h3><p>No activity records have been published yet. Explore the planned sessions below; meeting outcomes and evidence will be added after each activity.</p></div>'
    page('index.html','Work archive','Archive',intro('Research / Build / Reflect','Voice, in practice.','An eight-week study of voice-first AI. Follow our questions, experiments, decisions, and the work that becomes our final report.')+f'''<div class="facts"><div><span>Program window</span><strong>Oct 3 – Nov 30, 2026</strong></div><div><span>Weekly sessions</span><strong>8 planned · {completed} completed</strong></div><div><span>Working project</span><strong>Sona / Proposed</strong></div></div><section><div class="section-title"><h2>Latest work</h2><a href="weeks.html">All weeks</a></div>{latest}</section><section><div class="section-title"><h2>The eight-week journey</h2><span>Learning through making</span></div><div class="week-grid">{week_cards()}</div></section><a class="report-banner" href="report.html"><span class="eyebrow">From process to evidence</span><h2>A report that grows<br>with the work.</h2><p>Project demo, technical insights, evaluation, and every contributor’s reflection.</p><span class="pill">Read the report in progress</span></a>''')
    page('weeks.html','Weekly work','Weekly work',intro('Work archive','Week by week.','The proposed Wednesday sessions run from October 7 to November 25, 19:00–21:00 KST. Dates and venues remain subject to team confirmation.')+f'<div class="week-grid">{week_cards()}</div><aside class="note"><h2>What each record preserves</h2><p>Date and time, public-safe attendance, venue, agenda, work completed, individual contributions, decisions and rationale, photos, work products, and next steps. The public archive complements the official Notion activity log.</p></aside>')
    for w in DATA['weeks']:
        items = ''.join(f'<li>{e(item)}</li>' for item in w['activities'])
        body = intro(f'Week {w["number"]:02} / {w["status"].replace("-", " ")}',w['title'],w['deliverable'])
        body += f'<div class="facts"><div><span>Planned date</span><strong>{e(w["planned_date"])}</strong></div><div><span>Planned time</span><strong>19:00–21:00 KST</strong></div><div><span>Meeting format</span><strong>To confirm</strong></div></div><section class="reading"><h2>Session plan</h2><ul>{items}</ul><h2>Activity records</h2>'
        body += ''.join(record(r) for r in w['records']) if w['records'] else '<div class="empty"><h3>Awaiting the session record</h3><p>This page contains a plan, not a claim that the session took place. Outcomes, evidence, and reflections will appear after review.</p></div>'
        body += '</section><div class="pagination">'
        if w['number'] > 1: body += f'<a href="week-{w["number"]-1:02}.html">Previous week</a>'
        body += '<a href="weeks.html">All weeks</a>'
        if w['number'] < 8: body += f'<a href="week-{w["number"]+1:02}.html">Next week</a>'
        page(f'week-{w["number"]:02}.html',f'Week {w["number"]}: {w["title"]}','Weekly work',body+'</div>')
    page('project.html','Sona project','Project',intro('Working concept / Not yet implemented','Meet Sona.','A proposed voice-first field assistant for physical tasks when hands and eyes are occupied.')+'''<div class="project-hero"><span class="eyebrow">Research question</span><h2>When should an assistant<br>speak—and when should it listen?</h2><p>We plan to study turn-taking, interruption, response timing, proactive help, and recovery from misunderstanding.</p></div><section class="split"><div><h2>One experience.<br>Two perspectives.</h2></div><div><h3>Sona Mobile</h3><p>The proposed participant experience: a minimal, call-like voice interface for a physical task. Camera context is an optional extension.</p><h3>Sona Lab</h3><p>The proposed researcher console: configure experiments, observe transcripts and events, measure latency, and document what happened.</p></div></section><section class="split"><h2>Define before building.</h2><div><p>The team still needs to select the target user and task, agree the MVP scope, define success measures, and confirm the technical architecture.</p><p>Candidate evaluation dimensions include response latency, premature turn endings, interruption success, task completion, perceived control, visual grounding, and error recovery. No test results are available yet.</p><a class="pill" href="report.html">Follow the evidence</a></div></section>''')
    report_body = intro('Final project report / In progress','What we built.<br>What we learned.'.replace('<br>',' '),'A living report, assembled from the weekly archive. Sections remain pending until the team adds outcomes and supporting evidence.')
    report_body += '<div class="report-layout"><nav class="toc" aria-label="Report sections">'+''.join(f'<a href="#{s["id"]}">{i:02} {e(s["title"])}</a>' for i,s in enumerate(DATA['report'],1))+'</nav><div>'
    for i,s in enumerate(DATA['report'],1):
        report_body += f'<section class="report-section" id="{s["id"]}"><p class="eyebrow">{i:02} / {e(s["status"])}</p><h2>{e(s["title"])}</h2><p>{e(s["guidance"])}</p>'
        report_body += ''.join(f'<p>{e(p)}</p>' for p in s['paragraphs']) or '<p class="pending">Awaiting team content and evidence.</p>'
        if s['evidence']: report_body += f'<h3>Supporting evidence</h3><ul>{links(s["evidence"])}</ul>'
        report_body += '</section>'
    page('report.html','Final project report','Final report',report_body+'</div></div>')
    page('about.html','About the lab','About',intro('Voice UX Lab / Seoul','Learn together.<br>Make it tangible.'.replace('<br>',' '),'An independent study team exploring voice-first AI through a working prototype, shared experiments, and a documented learning journey.')+'''<section class="split"><h2>The program</h2><div><p>Voice UX Lab participates in OpenAI × IT’s Study, cohort 5. Public contributor profiles will be added with their consent.</p><p>The official activity window is October 3–November 30, 2026. The team’s proposed eight sessions run on Wednesdays from October 7 to November 25. The exact meeting format and venue are still to be confirmed.</p><p>This website documents the team’s own work. It is not an official OpenAI website.</p></div></section><section class="split"><h2>A durable archive</h2><div><p>Weekly records preserve the context behind our decisions. The final report brings together the problem, agent design, demo, development process, evaluation, learning, and individual reflections.</p><p>Only approved public summaries and artifacts belong here. Participant-only materials, raw research recordings, personal contact details, attendance administration, and consent records stay in private team storage.</p></div></section>''')
    print(f'Built {len(list(OUT.glob("*.html")))} pages in {OUT}')

if __name__ == '__main__': build()
