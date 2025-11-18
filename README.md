# Midtown Comic Monitor Bot

This bot monitors a specific Midtown Comics product page for new, unlisted variants. It will send you a Discord DM when it finds an item that matches your keywords.

This bot is designed to be very specific: it only looks at the **"Available in Multiple Covers"** grid on a *single product page*.

## Setup (First-Time Only)

1.  **Install Python:** Make sure you have Python 3.8+ installed.
2.  **Install Libraries:** Open a terminal/command prompt and run:
       ```bash
       pip install discord.py aiohttp beautifulsoup4 python-dotenv
       ``` 
    You can also use the Conda environment that I used via Anaconda prompt or a terminal window:
       ```bash
       conda env create -f environment.yml
       conda activate midtown-watcher
       ```
3. **Create `.env` File:**
      * In the same folder as the bot, create a file named `.env` (no other name).
      * I have included a `.env.example`, you can just delete the `.example` part and use this exact file.
      * Paste your Token and User ID into it like this:
    <!-- end list -->
    ```ini
    DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
    DISCORD_USER_ID=YOUR_USER_ID_HERE
    ```

## How to Monitor a New Comic

To make this bot monitor a different comic, you only need to change **two** things in the Python file.

### 1\. The `URL`

This is the *main product page* for the comic.

> **Where to find it:** Go to Midtown Comics and find the main page for the comic you want to watch (e.g., "X-Men \#1"). Copy the URL from your browser's address bar.

```python
# Find this line and replace the link
URL = "https://www.midtowncomics.com/product/2492904"
```

### 2\. The `SEARCH_JOBS`

This is your "wishlist." The bot will scan all the variant titles and send an alert if it finds a title that contains **ALL** of the keywords in one of your jobs.

> **How it works:** A job like `"artgerm_virgin": ["artgerm", "virgin"]` will *only* send an alert if it finds a variant title that contains **BOTH** "artgerm" **AND** "virgin". This stops it from alerting you on a comic that's *already* listed (like "Cover E Artgerm").

```python
# Find this dictionary and edit it
SEARCH_JOBS = {
    # This job looks for "artgerm" AND "virgin"
    "artgerm_virgin":    ["artgerm", "virgin"],
    
    # This job looks for "villalobos" AND "virgin"
    "villalobos_virgin": ["villalobos", "virgin"],
    
    # You can add more jobs here
    # "New_Job_Name": ["keyword1", "keyword2"],
}
```

**Remember:** The keywords are not case-sensitive.

## How to Run the Bot

1.  Open your terminal or command prompt.
2.  Navigate to the bot's folder.
3.  Run the bot:
    ```bash
    python main.py
    ```
4.  It will log in and print `Monitor task started`.
5.  **You must keep this terminal window open** for the bot to continue running.

## Dev Specific Notes

Python's `asyncio` is effectively the same as the JavaScript Event Loop. It is single-threaded cooperative multitasking.
The bot maintains a WebSocket connection with Discord. The "Heartbeat" is just a standard Ping running on a `setInterval`.
If you see these `"RESUMED"` Logs, don't worry. It usually means a system stutter momentarily blocked the main thread (blocking the Event Loop), causing the WebSocket `ping` to timeout. The bot auto-recovers immediately.

### Blocking vs. Non-Blocking
Just like you wouldn't block the main UI thread in JS, you cannot block the loop here.

* ❌ **Bad:** `time.sleep(60)`
    * **Why:** This pauses the *entire* thread. It stops the Event Loop, kills the Heartbeat `setInterval`, and causes a connection timeout.
* ✅ **Good:** `await asyncio.sleep(60)`
    * **Why:** This yields control back to the loop (like a Promise/`setTimeout`), allowing the bot to keep the WebSocket alive while waiting.