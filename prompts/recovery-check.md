# Duplicate-Safe Recovery Automation

Run this automation every day at 12:20 PM.

Use the current date in the user's timezone. First inspect the primary
automation memory and today's local sent/outbox/failed artifacts.

## Recovery Rules

1. If a LinkedIn sent artifact already exists for today, do nothing.
2. If a LinkedIn outbox or failed artifact exists, do not generate another
   post. Trigger one local delivery pass and let the worker continue retrying.
3. If only Telegram has today's post, recover the matching text and queue only
   the missing LinkedIn profile target.
4. Only when no post was generated or queued anywhere today, generate a fresh
   global AI-news post and enqueue it for both destinations.

## Content Rules For A Missing Primary Run

- Use current global AI news from credible recent sources.
- Choose one timely global AI development from the last few days.
- Start with a strong, specific hook tied to the news.
- Explain what happened, why it matters globally, and the practical implication
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
- Keep the post under 3,000 characters.
- Use no more than one emoji.
- End with exactly 6 to 8 relevant hashtags.
- Read prior automation memory and never repeat a recent news angle.
- Queue only the final publish-ready post.
