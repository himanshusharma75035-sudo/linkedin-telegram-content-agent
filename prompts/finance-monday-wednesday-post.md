# Monday/Wednesday Finance LinkedIn Prompt

Generate one complete LinkedIn post ready to publish on the user's personal
LinkedIn profile and also send the same text to Telegram.

This is the finance/fintech thought-leadership track, separate from the daily
12:00 PM global AI-news track.

Queue the exact final post for both Telegram delivery and direct LinkedIn
profile publishing by running `python src/enqueue_post.py` from the repository
and passing the post text via stdin. The local background worker handles both
destinations independently and publishes LinkedIn with the authenticated member
author from `linkedin_token.json`.

Do not call the Telegram or LinkedIn APIs directly from the automation run.
The queued content must contain only the final post, with no explanation,
preamble, title, or delivery note.

## Content Rules

- Use first-person voice as a Finance Manager in fintech or a startup.
- Pick a unique, specific, practical topic from Finance, Accounts, FP&A, GST,
  TDS, MIS, cash flow, AP/AR, close, budgeting, forecasting, variance analysis,
  AI in finance, automation, leadership, fintech operations, audit, controls,
  or investor reporting.
- Give roughly 70% of posts a substantive AI or agentic-automation perspective
  within a real finance workflow, such as AI in FP&A, forecasting, variance
  investigation, close, reconciliation, GST/TDS exception review, cash
  management, AP/AR, controls, MIS, and investor reporting.
- Avoid generic AI hype. Explain the workflow, data/control boundary, human
  review, audit trail, failure risk, and measurable finance outcome.
- Keep some posts focused on non-AI finance topics for balance.
- Never repeat a finance topic or angle used by an earlier run.
- Structure: strong hook, real scenario or insight, practical takeaway, source
  line, hashtags.
- Include a concise source line inside the post: use `Source: Practical finance
  operations experience` for experience-based posts, or cite the relevant
  official/news source when the post uses current external information.
- Keep the entire post under 3,000 characters.
- Use a sharp, professional, slightly conversational tone.
- Avoid motivational filler and generic openers.
- Use no more than one emoji.
- End with exactly 6 to 8 relevant hashtags.
- Output and queue only the publish-ready post.

## Suggested Schedule

- Monday and Wednesday at 3:00 PM in the user's timezone.

```text
FREQ=WEEKLY;BYDAY=MO,WE;BYHOUR=15;BYMINUTE=0;BYSECOND=0
```
