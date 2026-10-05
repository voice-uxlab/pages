# Content model and editorial workflow

## Week

`number`, `planned_date` (ISO date), `title`, `deliverable`, `activities`, `status` (`planned`, `in-progress`, `completed`), and `records`.

The plan and the actual activity records are separate. Set a week to completed only when its documented activity has occurred. Dates use Asia/Seoul; a changed meeting date belongs in the record and need not overwrite historical planning.

## Activity record

Use `content/record-template.json` as a starting point, fill all fields, then append it to the appropriate week's `records`. Do not publish an unfilled template.

| Field | Meaning |
| --- | --- |
| id | Stable slug, unique across the archive |
| title | What happened during the activity |
| date, start_time, end_time, timezone | Actual activity date/time, ISO date and 24-hour clock |
| public_attendees | Approved participant names or aliases |
| venue | Public-safe meeting location or online format |
| summary | Work completed and what was learned |
| agenda | Time blocks and activities |
| contributions | Work by each contributor, with outcomes |
| decisions | Decision, alternatives, rationale, and tradeoffs |
| next_steps | Next task, owner, and expected date |
| photos | Approved photo URLs, labels, meaningful alt text |
| artifacts | Approved output URLs and labels |
| publication_reviewed | Must be true before publication |

Photos and artifacts use `label`, `url`, and `publication_approved`. Photos also require `alt`. Supported URLs are HTTPS or paths under `assets/`. Assets must actually exist. Do not include identifiable participants without permission. Re-review an external resource's visibility before linking it.

The team's private administrative record separately tracks full attendance, log due dates, Notion submission and email notification, first/final meeting status, and evidence permissions. None of those private records should enter the public repository.

## Report section

`id`, `title`, `guidance`, `status`, `paragraphs`, `evidence`. Evidence entries use a label and URL, preferably a relevant `week-NN.html` or approved artifact. `verified` requires evidence. Drafts should distinguish observations, interpretation, and limitations. Keep unfinished sections visible as pending rather than fabricating results.

For final results-sharing, gather approved outputs and reflections for every contributor. Record meeting attendance and program completion separately in private administration. Finalize the code, setup documentation, slides, demo video, evaluation, and evidence index before marking the report complete.

## Publication workflow

1. Write the private full activity record and complete the official submission.
2. Prepare the public summary and approved evidence.
3. Update `archive.json` and relevant report sections.
4. Build and check the site; preview desktop and mobile layouts.
5. Review the content change in GitHub and merge to `main`.
6. Confirm the deployment succeeds and verify the live page.

Public publication does not satisfy any official Notion or email submission requirement.
