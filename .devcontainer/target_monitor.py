import time
import json
import requests
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import random
from datetime import datetime

# -------------------------
# Configuration
# -------------------------
PRODUCTS = [
    {
        "name": "Scarlet & Violet Booster Bundle",
        "tcin": "94300074",
        "cart_limit": 2
    },
    {
        "name": "2024 Pokémon Paldea Adventure Chest",
        "tcin": "89952654",
        "cart_limit": 2
    },
    {
        "name": "Trick or Trade Mimikyu & Pikachu Mini Booster Packs",
        "tcin": "1005019724",
        "cart_limit": 2
    },
    {
        "name": "Magic the Gathering Marvel's Spider-Man Bundle Gift Edition",
        "tcin": "94898406",
        "cart_limit": 2
    },
    {
        "name": "Stanley Halloween 20 oz Quencher - Spellcast Black",
        "tcin": "94609474",
        "cart_limit": 2
    },
    {
        "name": "Stanley Halloween 20 oz Quencher - Spellcast Pink",
        "tcin": "94609478",
        "cart_limit": 2
    },
    {
        "name": "Stanley Halloween 20 oz Quencher - Hypnotic Green",
        "tcin": "94609490",
        "cart_limit": 2
    },
    {
        "name": "Pokémon TCG: Scarlet & Violet—Prismatic Evolutions Booster Bundle",
        "tcin": "93954446",
        "cart_limit": 2
    },
    {
        "name": "Pokémon TCG: Scarlet & Violet—Prismatic Evolutions Surprise Box",
        "tcin": "94336414",
        "cart_limit": 2
    },
    {
        "name": "Pokémon TCG: Scarlet & Violet— Destined Rivals Elite Trainer Box",
        "tcin": "94300069",
        "cart_limit": 2
    },
    {
        "name": "Pokémon TCG: Scarlet & Violet - Prismatic Evolutions Premium Figure Collection",
        "tcin": "94864079",
        "cart_limit": 2
    },
    {
        "name": "Pokémon TCG: Mega Latias ex Box",
        "tcin": "94681763",
        "cart_limit": 2
    },
    {
        "name": "Pokémon TCG: Scarlet & Violet— Destined Rivals Booster Bundle",
        "tcin": "94300067",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94681777",
        "tcin": "94681777",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94681773",
        "tcin": "94681773",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94270152",
        "tcin": "94270152",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94898411",
        "tcin": "94898411",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94898402",
        "tcin": "94898402",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94681766",
        "tcin": "94681766",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94681782",
        "tcin": "94681782",
        "cart_limit": 2
    },
    {
        "name": "Product TCIN 94721096",
        "tcin": "94721096",
        "cart_limit": 2
    }
]

DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discordapp.com/api/webhooks/1421254695644696667/i7WP5OliQKlyfm1ywlQAwpebazBchPCtHb777JzSENt9utRJyWf7TGZerFjXRRya2eJT"
)
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "3"))
CONFIRMATION_COUNT = int(os.getenv("CONFIRMATION_COUNT", "1"))
MAX_RETRIES = 2
TIMEOUT_DURATION = 3  # Reduced from 10 to 3

BLOCKING_PHRASES = [
    "sold out", "out of stock", "coming soon", "not available to ship",
    "temporarily out of stock", "available starting", "select a size",
    "choose a size", "make a selection", "see details", "available for store"
]

# Random user agents pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

# -------------------------
# Logging Setup
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('target_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -------------------------
# Selenium Setup
# -------------------------
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--disable-css")
    chrome_options.add_argument("--aggressive-cache-discard")
    chrome_options.add_argument("--memory-pressure-off")
    # Randomize user agent
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # Additional stealth options
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    return chrome_options

def create_driver():
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # Set faster page load strategy
        driver.implicitly_wait(1)  # Reduced from default
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        raise

# -------------------------
# Helper Functions
# -------------------------
def parse_json_stock_from_page(driver):
    try:
        # Reduced wait time and more targeted search
        script_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
        )
        script_content = script_element.get_attribute("innerHTML")
        if not script_content:
            return None
        data = json.loads(script_content)
        return data
    except:
        return None

def find_variant_by_tcin(data, tcin):
    if isinstance(data, dict):
        if str(data.get("tcin")) == str(tcin):
            return data
        for key in ["variants", "child_items", "items"]:
            if key in data and isinstance(data[key], list):
                for v in data[key]:
                    found = find_variant_by_tcin(v, tcin)
                    if found:
                        return found
        for v in data.values():
            found = find_variant_by_tcin(v, tcin)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_variant_by_tcin(item, tcin)
            if found:
                return found
    return None

def check_json_shipping_availability(product_node):
    if not product_node:
        return False, "No JSON data"
    try:
        fulfillment = product_node.get('fulfillment', {})
        shipping_available = False
        fulfillment_details = []

        if isinstance(fulfillment, dict):
            for key, value in fulfillment.items():
                if 'ship' in key.lower():
                    fulfillment_details.append(f"{key}: {value}")
                    if isinstance(value, dict):
                        if value.get('available', False) or value.get('available_to_promise_quantity', 0) > 0:
                            shipping_available = True
                    elif value in [True, 'available', 'in_stock']:
                        shipping_available = True

        atp_network = product_node.get('available_to_promise_network', {})
        if isinstance(atp_network, dict):
            for network_key, network_value in atp_network.items():
                if 'ship' in network_key.lower() and network_value:
                    shipping_available = True
                    fulfillment_details.append(f"network_{network_key}: {network_value}")

        atp_qty = product_node.get('available_to_promise_quantity', 0)
        if atp_qty > 0:
            shipping_available = True
            fulfillment_details.append(f"available_qty: {atp_qty}")

        return shipping_available, f"JSON fulfillment: {'; '.join(fulfillment_details) if fulfillment_details else 'no shipping data'}"

    except Exception as e:
        return False, f"JSON error: {str(e)}"

def page_contains_blocker(driver):
    try:
        page_text = driver.page_source.lower()
        for phrase in BLOCKING_PHRASES:
            if phrase in page_text:
                return True, phrase
        return False, None
    except:
        return False, None

def shipping_button_enabled(driver, product):
    selectors = [
        f"#addToCartButtonOrTextIdFor{product['tcin']}",
        "button[data-test='fulfillment-cell-shipping']",
        "button[data-test='shipItButton']",
        "button[data-test='addToCartButton']"
    ]
    matched_texts = []
    for selector in selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                if btn.is_displayed() and btn.is_enabled():
                    text = btn.text.strip()
                    if not any(block in text.lower() for block in ["coming", "not available", "sold out", "temporarily out of stock"]):
                        matched_texts.append(text)
        except:
            continue
    return len(matched_texts) > 0, matched_texts

def extract_price(driver):
    selectors = [
        "span[data-test='product-price']",
        "span[data-test='current-price']",
        "span[class*='Price']",
        ".h-display-xs",
        "[data-test='product-price-value']"
    ]
    for selector in selectors:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
            text = elem.text.strip()
            if text and '$' in text:
                return text
        except:
            continue
    return "N/A"

def extract_image_url(driver, product_node):
    if product_node:
        if product_node.get("primary_image_url"):
            return product_node["primary_image_url"]
        enrichment = product_node.get("enrichment")
        if enrichment and isinstance(enrichment, dict):
            images = enrichment.get("images", {})
            if images.get("primary_image_url"):
                return images["primary_image_url"]
    for selector in ['meta[property="og:image"]', "img.slideImage", "[data-test='product-image'] img", ".ProductImages img"]:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            if elems:
                return elems[0].get_attribute("content") if selector.startswith('meta') else elems[0].get_attribute("src")
        except:
            continue
    return None

def check_stock(driver, product, retry_count=0):
    try:
        url = f"https://www.target.com/p/-/A-{product['tcin']}"
        driver.get(url)
        
        # Much faster page load detection - just wait for body, then proceed
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Minimal sleep - just enough for critical elements to load
        time.sleep(0.1)  # Reduced from 0.3

        debug = {"json_present": False, "json_shipping": False, "blocking_phrase": None, "button_texts": [], "reason": None, "retry_count": retry_count}
        
        # Try to get JSON data quickly
        data = parse_json_stock_from_page(driver)
        product_node = find_variant_by_tcin(data, product['tcin'])
        debug["json_present"] = bool(product_node)

        # Get other data in parallel-ish fashion
        price = extract_price(driver)
        image_url = extract_image_url(driver, product_node)
        button_available, button_texts = shipping_button_enabled(driver, product)
        debug["button_texts"] = button_texts
        json_shipping_available, json_details = check_json_shipping_availability(product_node)
        debug["json_shipping"] = json_details

        if button_available:
            debug["reason"] = "button_visible_clickable"
            return True, price, image_url, debug
        elif json_shipping_available:
            debug["reason"] = "json_shipping_available"
            return True, price, image_url, debug

        skip_blocker = "stanley" in product["name"].lower()
        if not skip_blocker:
            blocker_found, phrase = page_contains_blocker(driver)
            debug["blocking_phrase"] = phrase
            if blocker_found:
                debug["reason"] = "blocking_phrase_found"
        else:
            debug["reason"] = "stanley_product_no_blocker_check"

        debug["reason"] = debug.get("reason", "no_shipping_available")
        return False, price, image_url, debug

    except Exception as e:
        if retry_count < MAX_RETRIES:
            # Shorter retry delay
            time.sleep(0.5 * (retry_count + 1))  # Reduced from 1.5
            return check_stock(driver, product, retry_count + 1)
        return False, "N/A", None, {"error": str(e), "retry_count": retry_count}

def format_price(price_str):
    if not price_str or price_str == "N/A":
        return "N/A"
    try:
        clean_price = price_str.replace('$', '').replace(',', '')
        price_float = float(clean_price)
        return f"${price_float:.2f}"
    except:
        return price_str if price_str.startswith("$") else f"${price_str}"

def send_discord_alert(product, price, image_url):
    try:
        tcin = product["tcin"]
        formatted_price = format_price(price)
        embed = {
            "title": product['name'],
            "url": f"https://www.target.com/p/-/A-{tcin}",
            "color": 0x00FF00,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {"name": "💰 Price", "value": formatted_price, "inline": True},
                {"name": "🚢 Type", "value": "Shipping Available", "inline": True},
                {"name": "🔢 TCIN", "value": str(tcin), "inline": True},
                {"name": "📊 Stock", "value": "1+", "inline": True},
                {"name": "🛒 Cart Limit", "value": str(product["cart_limit"]), "inline": True},
                {"name": "📱 Open in App", "value": f"[Click Here](https://www.target.com/p/-/A-{tcin})", "inline": True},
            ],
            "footer": {"text": "Target Stock Monitor - Shipping Only"},
        }
        if image_url:
            embed["thumbnail"] = {"url": image_url}
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)  # Reduced timeout
        logger.info(f"Alert sent for {product['name']}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Discord alert for {product['name']}: {e}")
        return False

# -------------------------
# Main Monitor Loop
# -------------------------
def monitor():
    logger.info("Starting Target stock monitor - SHIPPING ONLY...")
    logger.info(f"Monitoring {len(PRODUCTS)} products every {CHECK_INTERVAL} seconds")
    consecutive_stock = {p["tcin"]: 0 for p in PRODUCTS}

    # Create drivers with staggered initialization to avoid simultaneous requests
    drivers = []
    for i in range(len(PRODUCTS)):
        drivers.append(create_driver())
        if i < len(PRODUCTS) - 1:  # Don't sleep after the last driver
            time.sleep(0.2)  # Small stagger

    try:
        while True:
            start_time = time.time()
            
            # Add small random delays between requests to appear more human
            shuffled_products = list(enumerate(PRODUCTS))
            random.shuffle(shuffled_products)  # Randomize order each cycle
            
            with ThreadPoolExecutor(max_workers=len(PRODUCTS)) as executor:
                future_to_product = {}
                
                for driver_idx, product in shuffled_products:
                    # Small random delay before each request
                    if future_to_product:  # Don't delay the first one
                        time.sleep(random.uniform(0.1, 0.3))
                    
                    future = executor.submit(check_stock, drivers[driver_idx], product)
                    future_to_product[future] = product

                for future in as_completed(future_to_product):
                    product = future_to_product[future]
                    try:
                        in_stock, price, image_url, debug = future.result()
                        timestamp = time.strftime("%H:%M:%S")
                        status_emoji = "SHIP" if in_stock else "NO"
                        status_text = "SHIPPING AVAILABLE" if in_stock else "NO SHIPPING"

                        log_msg = (
                            f"[{timestamp}] {product['name']}: {status_text} {status_emoji} | "
                            f"Price: {price} | Reason: {debug.get('reason', 'unknown')}"
                        )
                        if debug.get('button_texts'):
                            log_msg += f" | Buttons: {debug['button_texts']}"
                        logger.info(log_msg)

                        if in_stock:
                            consecutive_stock[product["tcin"]] += 1
                            if consecutive_stock[product["tcin"]] >= CONFIRMATION_COUNT:
                                logger.info(f"Confirmed shipping availability for {product['name']} - sending alert")
                                send_discord_alert(product, price, image_url)
                                consecutive_stock[product["tcin"]] = 0
                        else:
                            consecutive_stock[product["tcin"]] = 0

                    except Exception as e:
                        logger.error(f"Error processing result for {product['name']}: {e}")

            elapsed_time = time.time() - start_time
            sleep_time = max(0, CHECK_INTERVAL - elapsed_time)
            
            # Add small random variation to sleep time to avoid predictable patterns
            if sleep_time > 0:
                jitter = random.uniform(-0.2, 0.2)  # ±0.2 second jitter
                sleep_time = max(0.5, sleep_time + jitter)  # Ensure minimum 0.5s sleep
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    finally:
        for driver in drivers:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    try:
        monitor()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
