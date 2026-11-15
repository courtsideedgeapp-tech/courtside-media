# Evergreen content runbook

Two scheduled tasks share a queue file, `evergreen/queue.json`.
- CREATOR (Sundays ~6:11 PM ET): tops the queue up to 3 pending videos for the next Mon/Wed/Fri slots.
- PUBLISHER (Mon/Wed/Fri ~12:31 PM ET): posts the item dated today to Instagram AND TikTok, then marks it posted.

Never name sportsbooks. Results-only, framed as research, never advice. No tonight's picks, parlays, locks, or #NBABetting / #SportsBetting. Post only to Instagram account id 17841480704510652 (courtside.edge.app) with the Windsor.ai for Social Media connector. Never print or store secrets. Work without asking questions.

## Queue format
`{"items":[{"date":"2026-11-23","id":"myth_rest_days","title":"...","type":"myth|howto|stat","mp4":"evergreen/myth_rest_days.mp4","cover":"evergreen/myth_rest_days_cover.jpg","caption":"evergreen/myth_rest_days.txt","status":"pending|posted","media_id":null}]}`
`topics_used` (same file) lists topic ids already covered so nothing repeats.

## CREATOR steps
1. Read `data/record.json` from the Courtside Edge artifact (https://claude.ai/artifact/BjcjLESc4j84Qu8nPBQGZp) with the Artifact tool's read action (ToolSearch `select:Artifact` if deferred), saving with out_dir. Attach the repo (add_repo, access push, courtsideedgeapp-tech/courtside-media) and clone it.
2. Read `evergreen/queue.json`. Count items with status pending dated today or later. If 3 or more, stop with "queue full".
3. Slots: the next Mon/Wed/Fri dates (America/Toronto) strictly after the latest date already in the queue and after 2026-11-22; fill until 3 pending exist.
4. For each slot pick the type in rotation (look at the last items): myth, howto, stat. Pick a topic NOT in `topics_used` (bank below; add your own in the same spirit).
5. Ground every video in a REAL example from record.json when the topic allows it (a final-score blowout and a starter's minutes, a total vs its line, a Heat Check result). Re-check every number against the record before using it. Never use data about games not yet played. A pure concept video is fine when no real example fits, but never invent a number.
6. Write a spec JSON `evergreen/<id>.json` and render: `python3 -I studio/series.py spec evergreen/<id>.json evergreen/<id>.mp4`. Slide kinds: hook (lines, colors, size, sub), text (head, lines max 4, foot), stat (kick, name, big, bigsub, lines), rows (kick, 3 rows of [title, sub, big, label]). Colors are names: GOLD, INK, RED, GREEN, OR, MUTED. Keep 3-4 slides, 14-20 seconds total. Hook = short punchy claim; last slide = THE TAKEAWAY. The renderer rejects banned terms and requires "Research, not betting advice" in the caption. Caption: emoji-filled, fun, SEO-friendly, a question at the end, 6-8 hashtags (#NBA #NBAStats #BasketballAnalytics #CourtsideEdge #LearnBasketball plus topic tags).
7. Look at the cover jpg (Read tool) for overflow or clipping; fix the spec and rerun if needed.
8. Add the items to the queue (status pending), append topic ids to topics_used, commit (all files) and `git push origin HEAD:main`. Verify each mp4 and cover returns 200 at https://raw.githubusercontent.com/courtsideedgeapp-tech/courtside-media/main/evergreen/<file>.
9. Finish with ONE short message: the three videos (date, title, type) and the TikTok-ready raw URLs.

## PUBLISHER steps
1. Attach the repo (add_repo push) and clone. Read `evergreen/queue.json`. Today = `TZ=America/Toronto date +%F`.
2. Find the item with date == today and status pending. None: stop with "nothing due".
3. Verify mp4 and cover URLs return 200. Post: execute_action, connector "instagram", action "create_video_post", account "17841480704510652", params video_url (raw mp4 URL), cover_url (raw cover jpg URL, REQUIRED, never post without it), caption (the .txt file exactly), share_to_feed true.
4. TikTok via the ScheduleNChill connector (ToolSearch "schedulenchill"): get_accounts (tiktok account, currently id 372), get_tiktok_creator_info (can_post must be true), upload_media source "url" = raw mp4 URL (filename = the mp4 name, alt_text = title, folder "evergreen"), schedule_post when "now", account_ids [id], media_ids [media_id], content = the .txt caption exactly, platform_options [{account_id, options:{privacy_level:"PUBLIC_TO_EVERYONE", allow_comment:true, allow_duet:false, allow_stitch:false}}]. After ~60 s get_post must show published; retry_post once if failed. No TikTok sound needed (video has its own beat). A TikTok failure must not undo the Instagram post.
5. Set status posted, media_id and tiktok_post_id, commit, push.
6. Finish with ONE short message: title, Instagram media id, TikTok post id and status.

## Topic bank (pick unused; add more in the same spirit)
Myths: rest days mean a star sits; home court boosts every stat; back-to-backs always hurt; last game predicts the next; season average is the truth; a big game total lifts everyone; revenge games; starters always play 30+; a hot shooter stays hot; one big game changes a role.
How-to: read a box score in 10 seconds; role beats raw numbers; pace and game totals; variance (why one game proves nothing); foul trouble; garbage time; usage vs minutes; sample size; home/away splits; what a minutes restriction does.
Stat of the week: the biggest minutes drop in a blowout; the closest total vs its line; the week's most surprising result (hit or miss), explained with the minutes or game script.
