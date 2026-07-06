# Codex Automation Prompt

Generate one complete LinkedIn post ready to publish on behalf of a senior
Finance & Accounts professional working in Indian fintech, then queue that
exact post for both Telegram delivery and direct LinkedIn publishing by running
`python src/enqueue_post.py` from the repository and passing the post text via
stdin.

The local background worker handles both destinations independently. Do not
call the Telegram or LinkedIn APIs directly from the automation run.

## Content rules

- Use first-person voice as a Finance Manager in fintech or a startup.
- Pick a unique, specific, practical topic from Finance, Accounts, FP&A, GST,
  TDS, MIS, cash flow, AP/AR, close, budgeting, forecasting, variance analysis,
  AI in finance, automation, leadership, fintech operations, audit, controls,
  or investor reporting.
- Never repeat a topic or angle used by an earlier run.
- Structure: strong hook, real scenario or insight, practical takeaway,
  hashtags.
- Keep the entire post under 3,000 characters.
- Use a sharp, professional, slightly conversational tone.
- Avoid motivational filler and generic openers.
- Use no more than one emoji.
- End with exactly 6 to 8 relevant hashtags.
- Output and queue only the publish-ready post.

## Suggested schedule

- Monday at 12:00 PM in the user's timezone
- Wednesday at 12:00 PM in the user's timezone

In the Codex app, use the weekly rule below and let Codex interpret the wall
clock time in the user's configured locale. Do not prepend a timezone-qualified
`DTSTART`; that form may be saved without producing a scheduled run.

```text
FREQ=WEEKLY;BYDAY=MO,WE;BYHOUR=12;BYMINUTE=0;BYSECOND=0
```
