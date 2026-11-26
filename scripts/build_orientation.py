"""Publish the archived October 11 deck without a separate hosted service."""
import html
import re
import shutil

COPY = {
    'en': dict(title='Team orientation', skip='Skip to slides', sections='Sections', description='Voice UX Lab kickoff deck from October 11, 2026. Read all 15 slides or use presentation mode.',
               language='Language', weeks='weeks.html', back='Back to weekly work',
               recap='week-01.html', recap_label='Read the Week 1 recap',
               project='project.html',
               historical='This deck records the team’s plans and proposals on October 11, 2026. The Week 1 recap records what happened.',
               noscript='Enable JavaScript to read or present the deck.'),
    'ko': dict(title='팀 오리엔테이션', skip='슬라이드로 이동', sections='섹션', description='2026년 10월 11일 Voice UX Lab 킥오프 자료. 15장 전체 보기와 발표 보기를 제공합니다.',
               language='언어 선택', weeks='weeks.ko.html', back='주간 활동으로 돌아가기',
               recap='week-01.ko.html', recap_label='1주차 활동 기록 보기',
               project='project.ko.html',
               historical='이 자료는 2026년 10월 11일 오리엔테이션 당시의 팀 계획과 제안입니다. 실제 모임 내용은 1주차 활동 기록에서 확인할 수 있습니다.',
               noscript='자료를 읽거나 발표하려면 JavaScript를 활성화해 주세요.'),
}

def publish_orientation(root, out, localize=True):
    source = root / 'orientation'
    template = (source / 'template.html').read_text(encoding='utf-8')
    shutil.copytree(source / 'assets', out / 'orientation')
    for lang, copy in COPY.items():
        if lang == 'ko' and not localize:
            continue
        values = {**copy, 'lang': lang}
        rendered = re.sub(r'\{\{([a-z_]+)\}\}', lambda m: html.escape(values[m[1]], quote=True), template)
        name = 'orientation.html' if lang == 'en' else 'orientation.ko.html'
        if not localize:
            rendered = rendered.replace('href="orientation.ko.html"', 'href="orientation.html"')
        (out / name).write_text(rendered, encoding='utf-8')
