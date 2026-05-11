from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def initialize_driver():
    
    chrome_options = Options()
    # Optimized for speed and image loading
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.nawy.com")
    
    # Handle the privacy banner interceptor
    try:
        wait = WebDriverWait(driver, 5)
        cookie_accept = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'privacy-policy')]//following::button | //button[contains(text(), 'Accept')]")))
        cookie_accept.click()
    except:
        pass
    
    search_button = driver.find_element(By.XPATH, '//*[@id="header"]/div/div[2]/a[2]')
    search_button.click()
    time.sleep(3)
    return driver


def fetch_locations(driver):
    """
    Opens the 'see-more' location panel and returns ONLY the location names
    listed inside it — nothing else from the page.
    """
    area_button = driver.find_element(By.CLASS_NAME, "see-more")
    area_button.click()
    time.sleep(2.5)

    # The panel that appears after clicking "see-more"
    panel = driver.find_element(
        By.CSS_SELECTOR, '.sc-701c3092-0.ybvQU.checkbox-filter-options'
    )
    items = panel.find_elements(By.CLASS_NAME, 'input-container')

    locations = []
    for item in items:
        text = item.text.strip()
        if text:
            locations.append(text)

    return locations


def select_locations(driver, loc_names: list):
    """
    Selects multiple locations in a single filter session.

    For each name in loc_names:
      1. Types the name into the search bar
      2. Clicks the matching checkbox label
      3. Clears the search bar before moving to the next name

    After all names are processed, clicks Apply once so the site filters
    by all selected locations simultaneously.

    Called by the GUI (apps.py) with the full list of checked locations.
    """
    if not loc_names:
        print("  No locations provided — skipping selection.")
        return

    # ── Open the location panel ──────────────────────────────────────────────
    try:
        area_button = driver.find_element(By.CLASS_NAME, "see-more")
        area_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"  Warning: could not open see-more panel: {e}")
        return

    NEW_CAIRO_XPATH = (
        "/html/body/div/div[1]/div[5]/div/div[3]/div[1]"
        "/div/div[1]/div[2]/div/div[4]/div/div[2]/div[3]/div/div[1]/label"
    )
    SEARCH_BAR_CSS = '.sc-fb543f49-1.hiXIZJ'
    PANEL_CSS      = '.sc-701c3092-0.ybvQU.checkbox-filter-options'

    def _fresh_options():
        """Re-query the panel every call to avoid stale element references."""
        panel = WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, PANEL_CSS))
        )
        return panel.find_elements(By.CLASS_NAME, 'input-container')

    def _js_click(element):
        """Scroll into view then JS-click — bypasses overlay/intercept issues."""
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)

    def _clear_search():
        """Fully wipe the search bar so the next query starts clean."""
        try:
            bar = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_BAR_CSS))
            )
            bar.click()
            time.sleep(0.2)
            bar.send_keys(Keys.CONTROL + 'a')
            bar.send_keys(Keys.BACKSPACE)
            bar.clear()
            time.sleep(0.5)
            # If still not empty, triple-delete
            if bar.get_attribute('value'):
                bar.send_keys(Keys.CONTROL + 'a')
                bar.send_keys(Keys.DELETE)
                time.sleep(0.3)
        except Exception as e:
            print(f"    Warning: _clear_search failed: {e}")

    # ── Loop: search → wait for results to refresh → tick → clear → next ────
    for loc_name in loc_names:
        print(f"  Selecting location: {loc_name}")

        # 1. Type into the search bar
        try:
            search_bar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_BAR_CSS))
            )
            search_bar.clear()
            time.sleep(0.3)
            search_bar.send_keys(loc_name)
        except Exception as e:
            print(f"    Warning: could not type '{loc_name}' in search bar: {e}")
            continue

        # 2. Poll until the panel options refresh for this query (max 5 s).
        #    This is the key fix: we don't click until the new results are visible.
        deadline = time.time() + 5
        while time.time() < deadline:
            time.sleep(0.6)
            try:
                opts = _fresh_options()
                if loc_name.strip().lower() == "new cairo":
                    break  # XPath click doesn't need a text match
                if any(loc_name.lower() in o.text.lower() for o in opts):
                    break  # panel has updated for this search term
            except Exception:
                pass  # panel still re-rendering — keep polling

        # 3. Click the correct label
        try:
            if loc_name.strip().lower() == "new cairo":
                label = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, NEW_CAIRO_XPATH))
                )
                _js_click(label)
                print(f"    ✔ Ticked (New Cairo via fixed XPath)")
            else:
                opts = _fresh_options()  # re-fetch — avoids stale ref after polling
                matched = next(
                    (o for o in opts if loc_name.lower() in o.text.lower()), None
                )
                if matched:
                    try:
                        label = matched.find_element(By.TAG_NAME, 'label')
                    except Exception:
                        label = matched
                    _js_click(label)
                    print(f"    ✔ Ticked: {matched.text.strip()}")
                else:
                    print(f"    Warning: no match found for '{loc_name}' in panel.")
        except Exception as e:
            print(f"    Warning: location matching failed for '{loc_name}': {e}")

        # 4. Let the checkbox state register, then clear the bar for the next name
        time.sleep(0.8)
        _clear_search()
        time.sleep(0.8)  # Give the panel a moment to reset its list

    # ── Apply the filter once for all selected locations ─────────────────────
    try:
        add_btn = driver.find_element(By.CLASS_NAME, 'add-btn')
        add_btn.click()
        print(f"  Applied filter for {len(loc_names)} location(s).")
    except Exception as e:
        print(f"  Warning: could not click add-btn: {e}")

    time.sleep(3)


# Keep the old single-location signature as a thin wrapper so main.py still works
def select_location(driver, loc_name: str):
    """Backward-compatible wrapper — passes a one-item list to select_locations."""
    select_locations(driver, [loc_name])


def get_compound_links(driver):
    """
    Scrolls the results page to load all compound cards, returns a deduplicated
    list of compound URLs.  Returns an empty list (never raises) if nothing loads.
    """
    soup = bs(driver.page_source, 'html.parser')
    h1_element = soup.find('h1')

    num = 10  # safe default
    if h1_element and h1_element.find('span'):
        try:
            num = int(h1_element.find('span').get_text().split()[0])
        except (ValueError, IndexError):
            pass

    # If the page shows 0 results, bail out immediately
    if num == 0:
        print("  Location returned 0 results — skipping.")
        return []

    # Wait for the scrollable container
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-4898a223-0.dZedFG"))
        )
    except Exception as e:
        print(f"  Warning: results container not found: {e}")
        return []

    current_count = 0
    last_count    = -1
    last_change   = time.time()

    while current_count < num:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", container
        )
        time.sleep(3)
        soup  = bs(driver.page_source, 'html.parser')
        cards = soup.select('div.cards-container a[href*="/compound/"]')
        current_count = len(cards)
        print(f"  Compounds loaded: {current_count} / {num}")

        if current_count > last_count:
            last_count  = current_count
            last_change = time.time()
        else:
            if time.time() - last_change > 10:
                print("  Stagnation detected — stopping scroll.")
                break

        if current_count >= num:
            break

    all_links = []
    seen      = set()
    for card in cards:
        link = card['href']
        if link.startswith('/'):
            link = "https://www.nawy.com" + link
        if link not in seen:
            seen.add(link)
            all_links.append(link)

    return all_links


def scrape_property_details(driver, all_clinks):
    """
    Visits every compound link, collects individual property URLs, then scrapes
    each property page.

    Returns a dict with keys:
        compounds, ref_no, prices, areas, links, beds, baths, delivery, img
    The 'img' key maps compound_name -> [image_url, ...]
    """
    img  = {}
    data = {
        "compounds": [], "ref_no":    [], "prices":   [],
        "areas":     [], "links":     [], "beds":     [],
        "baths":     [], "delivery":  [],
    }

    # Guard: nothing to scrape
    if not all_clinks:
        print("  No compound links provided — skipping scrape.")
        data["img"] = img
        return data

    seen_properties = set()

    for compound_link in all_clinks:
        print(f"  Accessing compound: {compound_link}")
        try:
            driver.get(compound_link)
            time.sleep(2.5)
        except Exception as e:
            print(f"    Could not load compound page: {e}")
            continue

        soup = bs(driver.page_source, 'html.parser')
        property_urls = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/property/' in href or '/unit/' in href or '/p/' in href:
                full_url = (
                    "https://www.nawy.com" + href if href.startswith("/") else href
                )
                if full_url not in seen_properties:
                    seen_properties.add(full_url)
                    property_urls.append(full_url)

        if not property_urls:
            print(f"    No property URLs found in compound — skipping.")
            continue

        print(f"    Found {len(property_urls)} properties.")

        for url in property_urls:
            print(f"      Scraping: {url}")
            try:
                driver.get(url)
                time.sleep(1.5)
            except Exception as e:
                print(f"      Could not load property page: {e}")
                continue

            # ── Compound name ─────────────────────────────────────────────
            try:
                compound_name = driver.find_element(
                    By.CLASS_NAME, "headline-2"
                ).text.strip()
            except Exception:
                compound_name = "N/A"

            data["compounds"].append(compound_name)
            data["links"].append(url)

            # ── Floor-plan / property images ──────────────────────────────
            # Completely wrapped so ANY failure is silent
            try:
                # 1. Find all potential buttons with that specific class
                img_buttons = driver.find_elements(By.CSS_SELECTOR, "div.sc-8810fe67-0.kElvoW")

                for btn in img_buttons:
                    try:
                        # Check the text inside the button (where the 'Master Plan' or 'Floor Plan' span lives)
                        btn_text = btn.text.strip()
                        
                        if "Master Plan" in btn_text or "Floor Plan" in btn_text:
                            
                            btn.click()
                            time.sleep(2)  # Wait for the lightbox to open
                            
                            # Find the images inside the lightbox
                            floor_plan_elements = driver.find_elements(By.CSS_SELECTOR, "img.fslightboxs.fslightboxi.fslightbox-opacity-1")
                            
                            # Extract links
                            links_found = [el.get_attribute("src") for el in floor_plan_elements if el.get_attribute("src")]
                            
                            if links_found and compound_name != "N/A":
                                img.setdefault(compound_name, []).extend(links_found)
                                print(f"  Saved {len(links_found)} links from {btn_text}")

                            # IMPORTANT: Close the lightbox so you can click the next button
                            # Usually, pressing 'Escape' or clicking the background works
                            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                            time.sleep(1) 
            
                    except Exception as e:
                        print(f"Error processing button {btn_text if 'btn_text' in locals() else ''}: {e}")
            except Exception:
                pass  # find_elements itself failed — extremely rare, ignore

            # ── Price ─────────────────────────────────────────────────────
            try:
                data["prices"].append(
                    driver.find_element(By.CSS_SELECTOR, ".headline-1.price").text
                )
            except Exception:
                data["prices"].append("N/A")

            # ── Area ──────────────────────────────────────────────────────
            try:
                data["areas"].append(
                    driver.find_element(
                        By.XPATH,
                        "/html/body/div/div[1]/div[5]/div/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[2]"
                    ).text
                )
            except Exception:
                data["areas"].append("0")

            # ── Beds ──────────────────────────────────────────────────────
            try:
                data["beds"].append(
                    driver.find_element(
                        By.XPATH, "//div[contains(text(), 'Bed')]/following-sibling::div"
                    ).text
                )
            except Exception:
                data["beds"].append("0")

            # ── Baths ─────────────────────────────────────────────────────
            try:
                data["baths"].append(
                    driver.find_element(
                        By.XPATH, "//div[contains(text(), 'Bath')]/following-sibling::div"
                    ).text
                )
            except Exception:
                data["baths"].append("0")

            # ── Delivery ──────────────────────────────────────────────────
            try:
                data["delivery"].append(
                    driver.find_element(
                        By.XPATH, "//div[contains(text(), 'Delivery')]/following-sibling::div"
                    ).text
                )
            except Exception:
                data["delivery"].append("N/A")

            # ── Ref No. ───────────────────────────────────────────────────
            try:
                data["ref_no"].append(
                    driver.find_element(
                        By.XPATH, "//div[contains(text(), 'Ref')]/following-sibling::div"
                    ).text
                )
            except Exception:
                data["ref_no"].append("N/A")

    # Always attach the img dict before returning
    data["img"] = img
    return data
