# Validation plan — does anyone actually want this?

Goal: spend **days, not months**, to learn whether Mastr is worth building into a
business — *before* wiring payments. The landing page is the test instrument.

## Setup (≈ 1 hour)
1. **Make 2 real before/after demos.** Run a track through the engine, export
   ~20s MP3 clips, drop them in [`landing/demo/`](../landing/demo/). This is the
   single most persuasive thing on the page — don't skip it.
2. **Wire the waitlist form.** Create a free **[Formspree](https://formspree.io)**
   form, paste its endpoint into `landing/index.html` (`action="…"`). Submissions
   (email + "would you pay?" + genre) land in your inbox.
3. **Publish it.** Push → enable **Settings → Pages → Source: GitHub Actions** →
   the page is live at `https://rudraxdevelopment98-cell.github.io/shiva/`.
   (Optional: a real domain reads far more credible.)
4. Remove the yellow "validation page" banner before sharing.

## Run the test (1–2 weeks)
Share the link where your target audience already hangs out — **be specific**:
- Reddit: r/WeAreTheMusicMakers, r/edmproduction, r/podcasting, genre subs.
- Producer Discords / Facebook groups; your own network; X/TikTok with a demo clip.
- Comment helpfully, then link — don't just spam.

Pick **one niche** and speak to it (lo-fi, rap, podcast voice, etc.). A sharp
wedge converts far better than "for all music."

## What to measure
| Signal | Weak | Promising |
|---|---|---|
| Landing-page → email signup rate | < 5% | **> 15%** |
| “Would you pay?” → per-track or subscription | mostly “free only” | **≥ 30% pick a paid option** |
| Unprompted “when can I use this / take my money” | none | a few real ones |
| Qualitative replies | “meh, LANDR exists” | “I’d use this for every release” |

## Decision gate (be honest)
- **Green** (signups + paid intent + enthusiasm): wire Supabase + Stripe and open
  a paid beta to the waitlist. See [monetization.md](monetization.md).
- **Yellow** (some interest, weak pay intent): change the **wedge** (niche / price
  model — try pay-per-track) and retest. Cheap.
- **Red** (crickets after honest effort): it was a great build and a real skill
  gain — bank the engine as a portfolio piece and point the energy at a better
  wedge or idea. No shame, just data.

> The trap to avoid: building accounts + payments for an audience that hasn't said
> "I'd pay." Get that "yes" first.
