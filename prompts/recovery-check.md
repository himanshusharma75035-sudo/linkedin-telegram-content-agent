# Duplicate-Safe Recovery Automation

Run this automation every Tuesday and Thursday at 12:20 PM.

Use the current date in the user's timezone. First inspect the primary
automation memory and today's local sent/outbox/failed artifacts.

## Recovery Rules

1. If a LinkedIn sent artifact already exists for today, do nothing.
2. If a LinkedIn outbox or failed artifact exists, do not generate another
   post. Trigger one local delivery pass and let the worker continue retrying.
3. If only Telegram has today's post, recover the matching text and queue only
   the missing LinkedIn profile target.
4. Only when no post was generated or queued anywhere today in the 12:00 slot,
   generate a fresh global AI-news post and enqueue it for both destinations.

## Content Rules For A Missing Primary Run

- Use current global AI news from credible recent sources.
- On Tuesday, include Monday's news window as eligible coverage. On Thursday,
  include Wednesday's news window as eligible coverage.
- Choose one timely global AI development from the current day or previous day.
- Start with a strong, specific hook tied to the news.
- Keep it shorter and punchier than earlier long posts: target 900 to 1,400
  characters including hashtags, and never exceed 1,800 characters unless the
  story genuinely needs it.
- Explain what happened, why it matters, and one practical implication
  for business, finance, operations, risk, product, or governance.
- Mention the source of the information inside the post in a natural way, such
  as `Source: Reuters` or `Source: Axios`, and include the source link when
  practical while staying under the character limit.
- Avoid generic AI hype and motivational filler.
- Include the control or risk angle where relevant: data rights, model
  reliability, cost, regulation, enterprise adoption, safety, competition, or
  workflow impact.
- Keep the tone sharp, professional, slightly conversational, and highly
  engaging.
- Avoid generic openers.
- Use no more than one emoji.
- End with exactly 6 to 8 relevant hashtags, formatted vertically with each
  hashtag on its own separate line.
- Read prior automation memory and never repeat a recent news angle.
- Queue only the final publish-ready post.
