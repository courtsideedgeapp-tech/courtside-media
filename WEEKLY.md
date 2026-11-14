# Weekly runbook

Same setup as DAILY.md steps 1-2 and 7-8 (record.json, clone, push, raw URL check, Windsor post). Never name sportsbooks.

## Week in Review (Sundays ~2 PM ET) and Blowout Report (Saturdays ~12:45 PM ET)
1. Render both with `python3 -I studio/series.py weekly RECORD_JSON posts/weekly`. Files: week_review_END.mp4/.txt/.json and blowout_report_END.mp4/.txt/.json, where END is the last graded day.
2. For the one that belongs to today's run (Sunday: week_review, Saturday: blowout_report): skip if END is already in ledger.json under that key; otherwise post as a Reel with the .txt caption exactly, then add END to the ledger and push.
3. If blowout_report reports "skip" (fewer than 3 qualifying blowouts), say so and do not post.
4. Finish with ONE short message: what posted, media id, and the raw URL of the file for TikTok.
