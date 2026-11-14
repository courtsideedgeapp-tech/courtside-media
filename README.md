# Courtside Edge media

Faceless content system for the Courtside Edge NBA props-research brand
(TikTok @courtside.edge.app, Instagram @courtside.edge.app).

- `studio/` renders the videos: `recap.py` (daily Heat Check recap), `series.py` (weekly videos + evergreen series), `beat.wav` (original beat), `fonts/`, `logo.png`
- `reels/` evergreen series videos (public links used for Instagram)
- `posts/<date>/` generated recaps and weekly videos with their captions
- `ledger.json` what has been posted, so nothing posts twice
- `DAILY.md` and `WEEKLY.md` exact runbooks for the scheduled tasks
- `PLAYBOOK.md` content rules and the weekly rhythm

Public repo on purpose: Instagram fetches videos from these links. Never commit anything private (keys, webhook URLs, personal data).
