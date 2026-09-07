# Agent handoff — TFT compatibility work, 2026-09-07

## User decision and restart boundary
Work is paused at the user's request. Wait for a future BlueStacks compatibility update. Do not restart the bot, emulator, login attempts, install upgrades, or schedule monitoring unless the user asks. No matching Alune Python or BlueStacks Player/Manager processes were running at the final process check.

## Repository and upstream
- Local repository: E:\Programming Projects\TFT\Alune\Alune (moved from Downloads).
- User remote: https://github.com/zifanzhou1024/Alune.git, branch main.
- Original upstream: https://github.com/TeamFightTacticsBots/Alune.git.
- Original main c1418c50db45069cc3a378ba9f3068d63de2dde6 was merged in 53745dc, preserving local revival/event handling and watchdog changes. This handoff accompanies the subsequent compatibility commit.

## Changes and validation
- Use ADB input tap: stationary swipes were ignored by the current TFT client.
- Resolve the installed launcher activity, retaining the old activity as fallback. TFT 18.1 uses com.epicgames.unreal.SplashActivity; the old hardcoded activity returned Android error type 3.
- Retry empty/invalid screenshots three times, then raise a recoverable ADB timeout.
- Add current Play, Normal, Start, Normal-lobby, and cancel-queue image templates while retaining previous templates.
- Resume queue acceptance when starting in an existing queue; choose the matching cancel control on timeout.
- Live test successfully navigated Play -> Normal -> Start -> queue acceptance -> match loading. Full gameplay was NOT verified.
- Eight regression tests cover controls, launcher resolution, screenshot failures, lobby and queue behavior. Formatting/import/syntax/dependency checks passed during development.
- Existing trait/game assets target Set 17; Set 18 gameplay compatibility remains outstanding. Do not describe these changes as complete Set 18 support.

## Crash evidence: independent of the bot
Installed BlueStacks was 5.22.260.1025. NVIDIA RTX 4060 Laptop driver was 616.64; Intel Iris Xe is also available.

Pie64 (Android 9/API 28, TFT 18.1-5423749): Vulkan & OpenGL caused two host emulator crashes during match loading. Windows dumps show exception 0xc0000005 in NVIDIA nvgpucomp64.dll, offset 0x1a3242. Player.log reports VM shutdown after an unhandled exception.

Switching Pie64 to OpenGL only kept the emulator alive, but TFT repeatedly crashed on RHIThread with SIGSEGV in libEGL_emulation.so (eglDestroyImageKHR+306), followed by libEGL.so/libhoudini.so. A crash at 01:27:27 preceded the bot test at 01:28:02. The Logging in screen was a symptom preceding native crashes, not evidence that another login retry would help.

Existing Rvc64 (Android 11/API 30, older TFT 18.1-5402721) crashed with the bot stopped at 01:32:03 in libhoudini.so +0x1246cf during NativeBridgeLoadLibraryExt. Different TFT builds mean this was not an exact controlled comparison.

Failure locations implicate emulator graphics/native translation compatibility; they do not prove the precise underlying vendor defect. No emulator, TFT APK, or GPU upgrades were installed. Pie64 retains OpenGL-only rendering. Both instances use localhost ADB port 5555; only start one at a time.

## Local artifacts and configuration (intentionally not committed)
- alune-output/compatibility-test-notes.md: detailed chronology; its old current-state paragraphs may be stale. This handoff supersedes them.
- alune-output/config.yaml: migrated to v15/Set 17, normal mode; screen_record.enabled=false after streaming timeouts; original config backup is local.
- alune-output/current.png and other probe/queue captures: development screenshots.
- tmp/capture.py, tmp/live.py, tmp/entry_test.py: local test helpers, not maintained project entrypoints.
- D:\Program Files\BlueStacks_nxt\Logs\Player.log
- D:\Program Files\BlueStacks_nxt\Dumps\HD-Player\HD-Player.exe_12024_2026-09-07_01-14-02.dmp
- D:\Program Files\BlueStacks_nxt\Dumps\HD-Player\HD-Player.exe_42344_2026-09-07_01-20-43.dmp
Do not commit ADB keys, local config, full screenshots, or crash dumps.

## Resume only when requested
1. Check current official BlueStacks/TFT release notes for compatibility fixes. As of this investigation, BlueStacks 5.22.262 (Aug 31) offered unspecified fixes, not a documented TFT fix. No confirmed Windows alternative-emulator fix was found.
2. Update/test TFT and emulator with Alune stopped; require stable login and match loading before bot testing. Consider an Intel GPU comparison to isolate NVIDIA compiler failures; this is an untested hypothesis.
3. A physical Android device over USB avoids these emulator components and is supported by upstream, but has not been tested here.
4. Once the client is stable, test the bot and assess remaining Set 18 recognition/trait changes. Avoid bot foreground recovery during browser authentication.

From the repository, use the fresh Python 3.12 environment (older moved environments used Python 3.13):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Only after the user requests resuming:
.\.venv\Scripts\python.exe main.py
```

## Sources consulted
- https://support.bluestacks.com/hc/en-us/articles/34359017537549-BlueStacks-5-22-Release-Notes
- https://teamfighttactics.leagueoflegends.com/en-sg/news/game-updates/teamfight-tactics-patch-18-1/
- https://nvidia.custhelp.com/app/answers/detail/a_id/5906 (616.86 hotfix did not list this failure)
- https://www.reddit.com/r/TeamfightTactics/comments/1vz1y3o/tft_does_not_work_on_emulators_anymore/ (anecdotal cross-emulator failures, not a verified fix)
