# Content playbook

## Standing rules (from the owner)
- Results only, framed as research, never advice. No "tonight's picks", parlays, locks, or pick-of-the-day content. Today's picks stay in the app.
- Never name sportsbooks. No #NBABetting or #SportsBetting. Use #NBA #NBAStats #BasketballAnalytics #HeatCheck #CourtsideEdge #NBAHighlights (+ topic tags).
- Every morning: post last night's Heat Check results, win or loss, with one insight from the nightly grading (blowout minutes, total vs line, role changes). Report misses plainly.
- Every video has the beat (studio/beat.wav, original, no licensing issues). Never post silent video.
- Captions: fun, emojis, SEO-friendly, end with a question, and always "Research, not betting advice. Do the homework!"
- Faceless, 1080x1920, 15-20 seconds, clear (non-black) cover frame.

## Weekly rhythm (ET)
| When | Post | How |
|---|---|---|
| Daily ~8:30 AM | Heat Check recap | automatic: Instagram posts itself, TikTok file is queued |
| Sunday ~2 PM | Week in Review | automatic |
| Saturday ~12:45 PM | Blowout Report | automatic |
| Midday weekdays | Evergreen series (How I Research a Prop 1-5, Prop Myths) | scheduled one-offs, refill monthly |

## TikTok
TikTok has no automated posting for this account. The daily task writes the finished video + caption to `posts/<date>/` and notifies the owner; the owner picks the file in TikTok Studio, the assistant does caption, cover, sound, and schedule.

## Quality checks before a post
- Record, hits and misses match `data/record.json`
- Insight uses real numbers from the nightly grade, never invented
- No sportsbook names, no advice wording

- Every Instagram Reel MUST be posted with cover_url (a settled hook frame as JPEG). Frame 0 is near-black because elements animate in. Covers for the evergreen series live in covers/<name>.jpg; weekly/daily renders write <name>_cover.jpg next to the mp4.

- Evergreen: see EVERGREEN.md (Sunday creator + Mon/Wed/Fri publisher share evergreen/queue.json). Banned terms are enforced by `studio/series.py spec`.

- TikTok sounds: rotate, never the same sound within the last 5 posts (see tiktok_sounds.json; log each use). Whole Crew was used for the Nov 13-22 batch, so pick something different from now on.
- Cover rule: make_cover shifts content down 170px so logo and headline survive Instagram's 3:4 profile-grid crop. Posted Reels keep old covers (Windsor cannot change them).
