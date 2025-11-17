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
        # Uncomment this to have the payload saved.

        # Saves the found HTML payload to a file for debugging
        # This will overwrite 'scraped_covers.html' on every check
        # try:
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
    user = await client.fetch_user(USER_ID)

    print("Monitor task started")

    # This dictionary tracks the alert status FOR EACH JOB
    # e.g., {"artgerm_virgin": False, "villalobos_virgin": False}
    alert_states = {job_name: False for job_name in SEARCH_JOBS.keys()}

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                # This will return a set, e.g., {"artgerm_virgin"}
                found_jobs = await check_page(session)

                # Loop through all possible jobs to update their state
                for job_name in SEARCH_JOBS.keys():

                    # Check for NEW alerts
                    # If the job was found AND we haven't alerted for it yet
                    if job_name in found_jobs and not alert_states[job_name]:
                        # Sends a SPECIFIC message for this job
                        msg = f"Variant spotted! Found '{job_name}' at {URL}"
                        await user.send(msg)
                        alert_states[job_name] = True  # Mark THIS JOB as "alerted"
                        print(f"Keyword '{job_name}' found — alert sent.")

                    # Check for resets
                    elif job_name not in found_jobs and alert_states[job_name]:
                        print(f"'{job_name}' is no longer listed. Resetting alert.")
                        alert_states[job_name] = False  # Reset (for restocks)

            except Exception as e:
                print("Error checking page:", e)

            # Can change this for faster/slower updating. Keep in mind, too fast may get you IP banned from the site.
            await asyncio.sleep(60)


intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

client.run(TOKEN)