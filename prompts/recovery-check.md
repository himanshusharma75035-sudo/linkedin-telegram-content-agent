# Duplicate-Safe Recovery Automation

Run this automation at 12:20 PM on Monday and Wednesday.

Use the current date in the user's timezone. First inspect the primary
automation memory and today's local sent/outbox/failed artifacts.

## Recovery rules

1. If a LinkedIn sent artifact already exists for today, do nothing.
2. If a LinkedIn outbox or failed artifact exists, do not generate another
   post. Trigger one local delivery pass and let the worker continue retrying.
3. If only Telegram has today's post, recover the matching text and queue only
   the missing LinkedIn target.
4. Only when no post was generated or queued anywhere today, generate a fresh
   post and enqueue it for both destinations.

## Content rules for a missing primary run

- Write in first person as a senior Finance & Accounts professional in Indian
  fintech or a startup.
- Choose a specific, practical topic from Finance, Accounts, FP&A, GST, TDS,
  MIS, cash flow, AP/AR, month-end close, budgeting, forecasting, variance
  analysis, AI in finance, agentic automation, leadership, operations, audit,
  controls, or investor reporting.
- Give roughly 70% of newly generated recovery posts a substantive AI or
  agentic-automation perspective within a real finance workflow, including
  FP&A, forecasting, variance investigation, close, reconciliation, tax
  exception review, cash, AP/AR, controls, MIS, or investor reporting.
- Avoid generic AI claims. Include the workflow, data/control boundary, human
  review, audit trail, failure risk, and measurable finance outcome.
- Keep some posts focused on non-AI finance topics for balance.
- Read prior automation memory and never repeat a topic or angle.
- Use a strong hook, real scenario or insight, practical takeaway, and exactly
  6 to 8 relevant hashtags.
- Keep the post under 3,000 characters.
- Use a sharp, professional, slightly conversational tone.
- Avoid generic openers, motivational filler, and more than one emoji.
- Queue only the final publish-ready post.
