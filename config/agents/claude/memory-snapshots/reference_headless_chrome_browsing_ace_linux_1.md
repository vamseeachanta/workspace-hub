---
name: reference_headless_chrome_browsing_ace_linux_1
description: ace-linux-1 is fully headless — Chrome page loads hang without --password-store=basic; Claude-in-Chrome extension cannot connect; Collide blocks headless at Cloudflare
metadata: 
  node_type: memory
  type: reference
  originSessionId: bef7bcd3-75db-455f-8193-f247ec2c5754
  modified: 2026-07-27T16:45:02.053Z
---

ace-linux-1 has **no display at all**: `DISPLAY`/`WAYLAND_DISPLAY` unset, no Xvfb, no x11vnc, no VNC server (only `tigervnc-viewer`, a client). `xdotool` and `tailscale` are present. Verified 2026-07-27.

Three stacked findings when driving Chrome from the CLI here:

1. **Chrome hangs forever on any real page load unless you pass `--password-store=basic`.** Symptom: `--dump-dom` returns 0 bytes and exits on timeout (124), no stderr; over CDP the tab's URL changes but `Runtime.evaluate` never answers. Cause is the cookie-store trying to unlock a login keyring that no daemon serves on a headless box. Adding `--password-store=basic` made the identical command return instantly. Working invocation:
   `google-chrome --headless=new --profile-directory=Default --password-store=basic --no-first-run --disable-gpu --no-sandbox --virtual-time-budget=25000 --dump-dom URL`
   Caveat: `basic` uses fallback encryption, so keyring-encrypted cookies in the profile may not decrypt.

2. **The Claude-in-Chrome extension cannot be reconnected via CLI on this box.** The extension IS installed and enabled in `~/.config/google-chrome/Default` (id `fcoeoabgfenejglbffodgkkbkcdhcgfn`, v1.0.81, `disable_reasons: []`). But it declares `sidePanel` + `nativeMessaging`, so pairing needs real browser UI; under `--headless=new` its service worker never starts and `tabs_context_mcp` reports "Browser extension is not connected." There is no CLI handshake — the extension only lives inside a running Chrome. A real fix needs a virtual display (`sudo apt install xvfb x11vnc`, both currently uninstalled) reached over Tailscale, or the Chrome Remote Desktop *host* deb (only the extension is installed, not the host).

3. **`app.collide.io` is behind Cloudflare bot-detection that stops headless Chrome.** WebFetch gets HTTP 403; headless Chrome with the logged-in profile renders only the "Just a moment… Performing security verification" interstitial and never reaches content, even at a 60 s virtual-time budget. Do NOT engineer around this — bypassing bot-detection is off-limits. To read a Collide thread, either have the user paste the text, or give Chrome a real display so the browser is genuinely interactive.

Trap to avoid: `pkill -f "<pattern>"` where the pattern also matches the agent's own Bash command line kills the shell (exit 144). Use `pkill -x chrome` instead.

Related: [[reference_headless_chrome_pdf_image_gotchas]], [[reference_ace_linux_1_display_nvidia_maxwell_dead]], [[reference_ace_linux_2_headless_vnc]], [[project_external_ssh_tailscale_fleet]]
