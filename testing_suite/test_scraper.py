from bs4 import BeautifulSoup

# Copy any of your jobs from the bot you want to test
SEARCH_JOBS = {
    "artgerm_virgin": ["artgerm", "virgin"],
    "villalobos_virgin": ["villalobos", "virgin"],
}

FILES_TO_TEST = ["scraped_covers.html", "test_page.html"]

def run_test(file):
    print("-------------- Running offline unit test --------------")

    # Read all the saved HTML FILES_TO_TEST
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    soup = BeautifulSoup(text, "html.parser")

    # Uses the exact parsing logic from the current bot
    variants = soup.find_all("div", class_="variant-grid-item")

    found_jobs = set()
    print(f"\nFound {len(variants)} variant items. Checking all...")

    for variant in variants:
        title_tag = variant.find("h3")
        if not title_tag:
            continue

        variant_text = title_tag.get_text().lower()
        print(f" -- Checking: {variant_text}")

        for job_name, keywords in SEARCH_JOBS.items():
            if all(kw.lower() in variant_text for kw in keywords):
                print(f" Match found for job: '{job_name}'")
                found_jobs.add(job_name)

    print("\n Test Complete")
    if found_jobs == set():
        print("Final set of jobs is empty, no matching covers found for current jobs.\n\n")
    else:
        print(f"Final set of jobs found: {found_jobs}\n\n")

if __name__ == "__main__":
    for cover in FILES_TO_TEST:
        run_test(cover)