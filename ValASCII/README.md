# ValASCII

Valorant friend monitor, chat tool, ASCII art spammer, and daily shop viewer — all in one dark-themed desktop app.

---

## Requirements

- **Windows** (Riot Client only runs on Windows)
- **Python 3.10+**
- **Riot Client / VALORANT installed and running**

---

## Installation

1. Open a terminal in this folder.
2. Install the only external dependency:
   ```
   pip install requests
   ```
   Or just double-click **`launch.bat`** — it installs everything and starts the app automatically.

---

## How to start

```
python main.py
```

or double-click **`launch.bat`**.

> The app reads the Riot Client lockfile automatically. **Riot Client must be open** before you launch ValASCII. If it is not running, click **⟳ Reconnect** after you open it.

---

## Features

### Friend list & online alerts

- The left panel shows all your Riot friends, sorted by status.
- **Status indicators:**
  | Symbol | Meaning |
  |--------|---------|
  | `●` green | Online (Available) |
  | `◉` green | Online on mobile |
  | `●` yellow | Away |
  | `⊗` red | Do Not Disturb |
  | `○` grey | Offline |
- A **toast notification + alert sound** pops up in the bottom-right corner of your screen the moment a friend comes online.
- The friend list refreshes every **5 seconds** automatically.

### Messaging

1. Click a friend in the left panel — their name appears in the chat header.
2. Type a message in the input bar at the bottom and press **Enter** or click **SEND**.
3. The last 40 messages in the DM conversation are loaded automatically when you select a friend.

### ASCII Art Spammer

Located at the bottom of the right panel.

1. Pick an art piece from the **dropdown** (10 pre-loaded pieces from valoranttextart.com).
2. A live **preview** is shown below the controls.
3. Set how many times to send in the **× field** (e.g. `5`).
4. Make sure a friend is selected, then click **⚡ SPAM ART**.
   - Messages are sent one at a time with **50 ms** between each.
   - Progress is shown next to the button (`Sent 3/5`).
5. Click **■ STOP** at any time to cancel mid-spam.

**Included art:**
- Gorilla / Monkey
- Nerd
- Among Us
- GG EZ
- Delete Valo!
- Noob
- VALORANT
- Copium
- Middle Finger
- Duolingo (Do ur lessons)

### Daily Shop

Click the **🛒 SHOP** button in the top bar.

- Fetches the 4 daily skin offers straight from Riot's servers using your logged-in account.
- Shows each **skin name** and its **VP price**.
- Your **VP**, **Radianite**, and **Kingdom Credits** balances are shown at the bottom.
- Click **⟳** inside the shop window to refresh.

> The shop window requires an active internet connection in addition to Riot Client being open.

---

## Reconnecting

If Riot Client closes and reopens (e.g. after a game update), the lockfile changes. Click **⟳ Reconnect** in the top-right of the app to re-read it.

---

## Lockfile location (for reference)

```
%LOCALAPPDATA%\Riot Games\Riot Client\Config\lockfile
```

This file exists only while Riot Client is running. ValASCII reads it automatically — you never need to touch it.

---

## Disclaimer

This app uses Riot's **unofficial local API**, which is not publicly supported. It reads data the Riot Client already has on your machine and sends chat messages on your behalf. Use at your own risk. Built with APIS from https://valdocs.prometheuz.me/
