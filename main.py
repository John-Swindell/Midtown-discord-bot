import asyncio
import os
import aiohttp
import discord
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
USER_ID_STR = os.getenv("DISCORD_USER_ID")

if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment.")
if not USER_ID_STR:
    raise ValueError("DISCORD_USER_ID not found in environment.")

USER_ID = int(USER_ID_STR)
URL = "https://www.midtowncomics.com/product/2492904"

"""
Alright good sir, here is where you can define independent "search jobs"
Each job is a list of keywords that must ALL be present.
I'll add an example at the end
"""
SEARCH_JOBS = {
    "artgerm_virgin":    ["artgerm", "virgin"],
    "villalobos_virgin": ["villalobos", "virgin"],
    # Following this format, you can add any other specific variants you want in the future
    # "JSC_virgin": ["Campbell", "virgin"],
}

# Headers used to spoof a real browser, rather than self-identifying traffic as aiohttp.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class MyClient(discord.Client):
    async def setup_hook(self):
        # This is the way to properly monitor in Discord 2.x+
        self.monitor_task = asyncio.create_task(monitor(self))


async def check_page(session):
    async with session.get(URL) as resp:
        resp.raise_for_status()
        text = await resp.text()
        soup = BeautifulSoup(text, "html.parser")

        # Finds the container for all variant covers
        variant_grid = soup.find("div", id="variant-grid")
        if not variant_grid:
            print("Could not find variant-grid. Page structure may have changed.")
            return set()  # Return an empty set

        # --- TESTING SUITE START ---
        # Uncomment this to have the HTML payload saved.

        # This will overwrite 'scraped_covers.html' on every check
        # try:
        #     # Automatically create the directory if it doesn't exist
        #     os.makedirs("./testing_suite", exist_ok=True)
        #     with open("./testing_suite/scraped_covers.html", "w", encoding="utf-8") as f:
        #         f.write(variant_grid.prettify())
        # except Exception as e:
        #     print(f"Warning: Could not save payload file: {e}")
        # --- TESTING SUITE END ---

        # Gets all the individual variant items
        variants = variant_grid.find_all("div", class_="variant-grid-item")

        found_jobs = set()

        # Checks the text of EACH variant
        for variant in variants:
            # Find the title text within the item
            title_tag = variant.find("h3")
            if not title_tag:
                continue  # Skip this item if it has no <h3> title

            variant_text = title_tag.get_text().lower()

            # Check this one variant against ALL your jobs (SEARCH_JOBS)
            for job_name, keywords in SEARCH_JOBS.items():
                if all(kw.lower() in variant_text for kw in keywords):
                    found_jobs.add(job_name)

        return found_jobs


async def monitor(client: discord.Client):
    await client.wait_until_ready()

    try:
        user = await client.fetch_user(USER_ID)

        # Startup message
        print("Monitor task started")
        params_str = ", ".join(SEARCH_JOBS.keys())
        startup_msg = f"Monitoring started.\n> **Link:** {URL}\n> **Tracking:** {params_str}"
        await user.send(startup_msg)
        print("Startup message sent to user.")

        # This dictionary tracks the alert status FOR EACH JOB
        alert_states = {job_name: False for job_name in SEARCH_JOBS.keys()}

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            while not client.is_closed():
                try:
                    # This will return a set, e.g., {"artgerm_virgin"}
                    found_jobs = await check_page(session)

                    # Loop through all possible jobs to update their state
                    for job_name in SEARCH_JOBS.keys():

                        # Check for new alerts
                        if job_name in found_jobs and not alert_states[job_name]:
                            msg = f"Variant spotted! Found '{job_name}' at {URL}"
                            await user.send(msg)
                            alert_states[job_name] = True  # Mark THIS JOB specifically as "alerted"
                            print(f"Keyword '{job_name}' found — alert sent.")

                        # Check for resets
                        elif job_name not in found_jobs and alert_states[job_name]:
                            print(f"'{job_name}' is no longer listed. Resetting alert.")
                            alert_states[job_name] = False  # Reset (for restocks)

                except Exception as e:
                    # This catches temporary web errors and keeps the loop running
                    print(f"Error checking page (will retry): {e}")

                # Can change this for faster/slower updating
                await asyncio.sleep(60)

    except Exception as e:
        # This catches a major, unrecoverable crash (e.g., UID is wrong)
        print(f"Bot monitor has crashed: {e}")
        try:
            # Try to send a DM to let you know it's dead
            await user.send(f"Bot monitor has crashed.\n`{e}`")
        except Exception as e2:
            print(f"Could not send crash DM: {e2}")

    finally:
        # This runs on a clean shutdown (Ctrl+C)
        print("Monitor task shutting down.")
        if not client.is_closed():
            try:
                await user.send("Monitoring stopped.")
                print("Shutdown message sent.")
            except Exception as e:
                print(f"Could not send shutdown message (already disconnected): {e}")

intents = discord.Intents.default()
"""
In order to add the below permissions, you must enable "Message Content Intent" in the bot's portal: 
https://discord.com/developers/applications/
As of now, the bot only sends messages; it never reads the content of any message. 
Enabling these permissions will greatly increase the bot's capabilities, but you do not need them for now.

For instance, you can add a /check command to instantly check the book's status at any time, or a /jobs command to show 
all currently active jobs. If debugging permissions issues with the bot, starting by uncommenting these intents may help
"""
# intents.messages = True
# intents.dm_messages = True

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

client.run(TOKEN)