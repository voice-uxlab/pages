# Voice UX Lab — pages

The public work archive and final project report for Voice UX Lab. A dependency-free static site, designed for GitHub Pages at `/pages/`.

## Develop

Requires Python 3.13 or newer. No external packages or API keys.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. All internal URLs are relative, so the same output works at a GitHub project-site path.

## Update the archive

Edit `content/archive.json`. The eight week plans exist from the beginning; activity records are added only after a real session. See [the content guide](docs/content-guide.md) and [the record template](content/record-template.json). Use approved names or aliases, and publish only approved, redacted photos and work products. Add public media in `assets/` or link an approved HTTPS resource.

Each report section has a `pending`, `draft`, or `verified` status, paragraphs, and evidence links. A verified section must contain evidence. Keep the report tied to weekly records and avoid claiming planned capabilities or unmeasured results as achievements.

## GitHub deployment

Repository: https://github.com/voice-uxlab/pages

Website: https://voice-uxlab.github.io/pages/

The organization display name is **Voice UX Lab** and its handle is **voice-uxlab**. The public repository uses GitHub Free. Source content lives on `main`; the generated static site lives on `gh-pages`. GitHub Pages publishes from the root of `gh-pages`.

After reviewing and committing source changes on `main`, publish with:

```sh
python3 scripts/publish.py
```

This builds, checks, and pushes the generated site to `gh-pages`. It requires an authenticated GitHub account with write access and a configured Git author. Verify the Pages deployment after uploading; pushing `main` alone does not republish the site.

## Content boundaries

This public site complements official reporting; it does not replace it. Keep official attendance, participant details, submission receipts, consent records, raw research recordings, and participant-only orientation materials in private team storage. Ignored files in a public repository are not a safe private storage system. Do not add them to this repository at all.

## Navigation

- Archive: latest published activity and the eight-week journey.
- Weekly work: all planned sessions and reviewed activity records.
- Project: the Sona proposal, with implementation status stated explicitly.
- Final report: summary, problem, demo, architecture, development, evaluation, learning, contributions, limitations, and artifacts.
- About: context, team, and archive purpose.

The visual direction uses generous whitespace, plain typography, a quiet navigation rail, and editorial blocks inspired by the OpenAI homepage. No OpenAI logos, brand assets, or affiliation claims are used.

## Languages

Each English page has a Korean page with the suffix `.ko.html`. The footer menu has EN and KR links to the same page. Navigation keeps the selected language. The picker works without JavaScript. Each page has the correct HTML language and alternate-language links.

`content/ko.json` contains Korean translations. Add a translation for each new public text. The build stops if a translation is missing. Proper names do not need translation.

## English copy

Use ASD-STE100 Issue 9 for English content. Read [the copy guide](docs/english-copy.md). The site checks sentence length and paragraph length. These checks do not replace a vocabulary and meaning review.

## Public Notion sources

See [the source record](docs/sources.md). The site uses the public Sunday meeting plan and the eight-week curriculum. It does not assign dates without calendar data. The Sona concept is still a proposal.
