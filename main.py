import pandas as pd
import numpy as np
import time

from Scraping import initialize_driver, select_locations, get_compound_links, scrape_property_details
from Analysis import run_kde_analysis, run_network_analysis, run_3d_cloud_analysis
from UTILITY import clean_area_list, get_bracket, clean_currency_list


def collect_locations() -> list[str]:
    """
    Terminal prompt: lets the user build up a list of location names,
    then returns the full list when they're done.
    All the input() logic lives here — Scraping.py stays free of it.
    """
    locations = []
    print("\n── Location Selection ─────────────────────────────────────")
    print("Type each location name and press Enter.")
    print("Type 'done' when finished, or 'list' to see what's been added.\n")

    while True:
        entry = input("  Location (or 'done'): ").strip()

        if entry.lower() == "done":
            if not locations:
                print("  No locations added yet — please add at least one.")
                continue
            break

        if entry.lower() == "list":
            if locations:
                print(f"  Added so far: {', '.join(locations)}")
            else:
                print("  Nothing added yet.")
            continue

        if not entry:
            print("  Empty input skipped.")
            continue

        if entry in locations:
            print(f"  '{entry}' already in the list — skipped.")
            continue

        locations.append(entry)
        print(f"  ✔ Added '{entry}'  ({len(locations)} total)")

    print(f"\n  Final list: {', '.join(locations)}")
    print("───────────────────────────────────────────────────────────\n")
    return locations


def main():
    driver = initialize_driver()
    print("Step 1: Driver Initialized")

    # ── Collect locations from the terminal, then select them all at once ────
    loc_names = collect_locations()
    select_locations(driver, loc_names)
    print("Step 2: Location(s) Selected")

    # ── Scrape the combined results page ─────────────────────────────────────
    links = get_compound_links(driver)
    print(f"Step 3: Found {len(links)} compound links")

    scraped_data = scrape_property_details(driver, links)
    if not scraped_data["links"]:
        print("CRITICAL: No properties were scraped. Check your CSS selectors in Scraping.py.")
        driver.quit()
        return

    print("Step 4: Scraping Complete")
    driver.quit()

    # ── Build DataFrame ───────────────────────────────────────────────────────
    df = pd.DataFrame({
        "compound": scraped_data["compounds"],
        "ref no.":  scraped_data["ref_no"],
        "area":     scraped_data["areas"],
        "bed":      scraped_data["beds"],
        "bath":     scraped_data["baths"],
        "price":    scraped_data["prices"],
        "delivery": scraped_data["delivery"],
        "link":     scraped_data["links"],
    })
    df = df.drop_duplicates(subset=["ref no."], keep="first")
    df.index = range(1, len(df) + 1)
    df.index.name = "Index"

    # ── Save CSV ──────────────────────────────────────────────────────────────
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    csv_name  = f"prop_find_{timestamp}.csv"
    df.to_csv(csv_name, index=True, encoding="utf-8")
    print(f"\nCSV saved: {csv_name}")

    # ── Derived numeric columns ───────────────────────────────────────────────
    area_nums      = np.array(clean_area_list(scraped_data["areas"]), dtype=float)
    numeric_prices = np.array(clean_currency_list(scraped_data["prices"]), dtype=float)

    df["area_clean"]  = clean_area_list(df["area"].tolist())
    df["price_clean"] = clean_currency_list(df["price"].tolist())
    df["bed_clean"]   = pd.to_numeric(df["bed"], errors="coerce").fillna(0)

    # ── Analysis ──────────────────────────────────────────────────────────────
    print("\nGenerating KDE Heatmap…")
    run_kde_analysis(area_nums, numeric_prices)

    print("Building Compound Network…")
    run_network_analysis(
        scraped_data["compounds"],
        numeric_prices,
        clean_area_list(scraped_data["areas"]),
    )

    print("Generating 3D Point Cloud…")
    run_3d_cloud_analysis(df)

    print("\nDone.")


if __name__ == "__main__":
    main()