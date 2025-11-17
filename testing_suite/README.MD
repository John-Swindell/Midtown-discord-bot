# README - Bot Testing Suite

This folder contains a simple testing suite to check your scraping logic *without* having to run the full Discord bot.

You can use this to:

1.  **Test new `SEARCH_JOBS`** against a fake, manually-created variant.
2.  **See what the bot *actually* sees** on the live website.

## Files in this Folder

  * `test_scraper.py`: This is the test script you will run.
  * `test_page.html`: Your "sandbox" file. It already includes the live data *plus* a fake "Artgerm Virgin" variant at the end so you can see a successful test.
  * `scraped_covers.html`: This file is **created by the main bot** (if you enable it). It contains the *raw HTML* the bot is scraping from the live website.
  * `example_fake_element.txt`: A template you can copy, paste, and edit inside `test_page.html` to create your own fake test variants.

-----

## How to Run the Tests

When you run the test script, it will automatically check **both** `test_page.html` (your manual tests) and `scraped_covers.html` (the live data).

### 1\. How to Test a New `SEARCH_JOBS` (Manual Test)

This is the most common test. Let's say you want to add a new job to your bot, like `["Campbell", "virgin"]`, and you want to be sure it works.

1.  **Update Test Jobs:** Open `test_scraper.py` and add your new job to the `SEARCH_JOBS` dictionary (it should match your main bot's list).
2.  **Add Fake Variant:** Open `example_fake_element.txt`. Copy the HTML.
3.  **Edit Sandbox:** Open `test_page.html` and paste the fake variant HTML at the very end (after the "Artgerm" one).
4.  **Modify Title:** Change the `<h3>...</h3>` text in the item you just pasted to match your test, e.g., `<h3>Cover X J Scott Campbell Virgin Cover</h3>`.
5.  **Run Test:** Open a terminal in this folder and run:
    ```bash
    python test_scraper.py
    ```
6.  **Check Output:** The test will run on both files. Look at the output for `test_page.html`. You should now see it find both `"artgerm_virgin"` and your new job.

### 2\. How to Test Against the *Live* Website Data

This test saves the *exact* HTML the bot is seeing to the `scraped_covers.html` file so you can inspect it.

1.  **Go to your *main bot file*** (the one in the parent folder, e.g., `main.py`).

2.  **Find the `check_page` function.**

3.  **Find the `--- TESTING SUITE START ---` block.**

4.  **Uncomment** the `try...except` block so it looks like this:

    ```python
    # --- TESTING SUITE START ---
    # Uncomment this to have the payload saved.

    # Saves the found HTML payload to a file for debugging
    # This will overwrite 'scraped_covers.html' on every check
    try:
        with open("./testing_suite/scraped_covers.html", "w", encoding="utf-8") as f:
            f.write(variant_grid.prettify())
    except Exception as e:
        print(f"Warning: Could not save payload file: {e}")
    # --- TESTING SUITE END ---
    ```

5.  **Run your *main bot*** (e.g., `python main.py`). Let it run for at least 60 seconds to complete one check.

6.  **Stop the bot.**

7.  A new file, `scraped_covers.html`, will now be in this folder with the latest data.

8.  **Run the test script** (`python test_scraper.py`). The output for `scraped_covers.html` will show you exactly what jobs (if any) the bot found on the live site.

> **IMPORTANT:** When you are done testing, **you must re-comment that block** in your main bot file. If you don't, it will constantly write to your hard drive every 60 seconds.