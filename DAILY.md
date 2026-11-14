# Daily recap runbook (scheduled task, ~8:23 AM ET)

Goal: post last night's Heat Check results as an Instagram Reel, and stage the TikTok version.
Work without asking questions. Never name sportsbooks. Post only to Instagram account id 17841480704510652 (courtside.edge.app).

1. Get the data. Read `data/record.json` from the Courtside Edge artifact (https://claude.ai/artifact/BjcjLESc4j84Qu8nPBQGZp) with the Artifact tool's read action (load the tool with ToolSearch `select:Artifact` if deferred), saving to a file with out_dir.
2. Get the repo. Call add_repo (access push) for courtsideedgeapp-tech/courtside-media, then `git clone --depth 1` into the workspace path it returns.
3. Decide the date. YESTERDAY = `TZ=America/Toronto date -d yesterday +%F`. The latest graded day in record.json must equal YESTERDAY. If not, wait 20 minutes and re-read once. If still not graded, stop and report "grading not ready" (do not post an older day).
4. Skip if done. If YESTERDAY is in ledger.json `instagram.recap`, stop with "already posted".
5. Render. `pip install pillow --break-system-packages` if PIL is missing; ffmpeg must exist. Run
   `python3 -I studio/recap.py RECORD_JSON posts/YESTERDAY YESTERDAY`. It writes recap_DATE.mp4, recap_DATE.txt (caption), recap_DATE.json (facts), and two PNG frames, and recap_DATE_cover.jpg (the Instagram cover; frame 0 is near-black, so ALWAYS pass it).
6. Check. Read recap_DATE.json: hits/misses must match the record entry, and look at recap_DATE_results.png. Fix and rerun if anything is wrong.
7. Publish files. Add posts/DATE/*, commit, `git push origin HEAD:main`. Verify `curl -sI https://raw.githubusercontent.com/courtsideedgeapp-tech/courtside-media/main/posts/DATE/recap_DATE.mp4` returns 200 (retry for ~2 minutes).
8. Post to Instagram with the Windsor.ai for Social Media connector (ToolSearch "windsor"): execute_action, connector "instagram", action "create_video_post", account "17841480704510652", params video_url = the raw URL, caption = the contents of recap_DATE.txt exactly, share_to_feed true, cover_url = raw URL of recap_DATE_cover.jpg (same folder; verify it returns 200 too). Never post a Reel without cover_url.
9. Update ledger.json: append DATE to `instagram.recap`; set `tiktok_ready[DATE]` to the raw video URL. Commit and push.
10. Finish with ONE short message for the owner: the record (e.g. "3-0, season 46-23"), Instagram media id, and "TikTok-ready: <raw video URL>" (caption is in posts/DATE/recap_DATE.txt). If anything failed, say exactly what.
