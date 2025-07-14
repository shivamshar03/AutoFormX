import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz

# ---------- CONFIG ----------
CSV_PATH = "form_data.csv"


FORM_URL = "https://shivam-sharma.vercel.app/collaborate"
MAX_RETRIES = 1
SCREENSHOT_DIR = "error_screenshots"
HEADLESS = False
# ----------------------------

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
df = pd.read_csv(CSV_PATH)

options = webdriver.ChromeOptions()
if HEADLESS:
    options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def extract_form_fields(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    fields = []

    for tag in soup.find_all(["input", "textarea", "select"]):
        field_type = tag.get("type", "text")
        if field_type in ["hidden", "submit", "button", "file"]:
            continue

        field = {
            "tag": tag.name,
            "type": field_type,
            "name": tag.get("name"),
            "id": tag.get("id"),
            "placeholder": tag.get("placeholder"),
            "aria_label": tag.get("aria-label"),
            "label_text": None
        }

        if field["id"]:
            label_tag = soup.find("label", attrs={"for": field["id"]})
            if label_tag:
                field["label_text"] = label_tag.get_text(strip=True)

        fields.append(field)

    return fields

def match_field_to_column(field, csv_columns):
    candidates = list(filter(None, [
        field.get("name"),
        field.get("placeholder"),
        field.get("aria_label"),
        field.get("label_text")
    ]))
    for c in candidates:
        best_match = process.extractOne(c, csv_columns, scorer=fuzz.token_sort_ratio)
        if best_match and best_match[1] > 70:
            return best_match[0]
    return None

def click_label_by_text(driver, text):
    xpath_variants = [
        f"//*[contains(text(), '{text}')]",
        f"//label[contains(normalize-space(), '{text}')]",
        f"//div[contains(normalize-space(), '{text}')]",
        f"//span[contains(normalize-space(), '{text}')]",
        f"//button[contains(normalize-space(), '{text}')]"
    ]
    for xpath in xpath_variants:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                driver.execute_script("""
                    const el = arguments[0];
                    el.scrollIntoView({behavior: 'smooth'});
                    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                    el.click();
                """, el)
                time.sleep(0.3)
                print(f"✅ Simulated click for: {text}")
                return True
        except:
            continue
    return False

def fill_form(driver, row, idx):
    try:
        driver.get(FORM_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(1)
        form_fields = extract_form_fields(driver)
        csv_columns = df.columns.tolist()
        filled_availability = False

        for field in form_fields:
            matched_column = match_field_to_column(field, csv_columns)
            if not matched_column or pd.isna(row.get(matched_column, None)):
                continue

            value = str(row[matched_column]).strip()

            try:
                if field["tag"] == "input":
                    if field["type"] in ["text", "email", "url"]:
                        if field["name"]:
                            el = driver.find_element(By.NAME, field["name"])
                            el.clear()
                            el.send_keys(value)
                            print(f"✅ Filled '{matched_column}' via name")
                    elif field["type"] in ["radio", "checkbox"]:
                        for val in value.split(","):
                            if not click_label_by_text(driver, val.strip()):
                                print(f"⚠️ Checkbox not matched: {val.strip()}")
                            time.sleep(0.3)
                elif field["tag"] == "textarea":
                    if field["name"]:
                        el = driver.find_element(By.NAME, field["name"])
                        el.clear()
                        el.send_keys(value)
                        print(f"✅ Filled textarea '{matched_column}'")
                elif field["tag"] == "select":
                    try:
                        sel = Select(driver.find_element(By.NAME, field["name"]))
                        sel.select_by_value(value.lower())  # FIXED: using option value
                        print(f"✅ Selected '{matched_column}' as '{value.lower()}'")
                        if matched_column.lower() == "availability":
                            filled_availability = True
                    except Exception as e:
                        if matched_column.lower() == "availability":
                            filled_availability = False
                        print(f"⚠️ Could not select dropdown '{matched_column}' - {e}")
            except Exception as e:
                print(f"⚠️ Error filling '{matched_column}' - {e}")

        # Skills (checkbox-like)
        if "Skills" in csv_columns:
            for skill in str(row["Skills"]).split(","):
                if not click_label_by_text(driver, skill.strip()):
                    print(f"⚠️ Skill checkbox not found: {skill.strip()}")
                time.sleep(0.5)

        # Submit
        try:
            submit_xpaths = [
                "//button[contains(text(),'Submit')]",
                "//button[contains(text(),'Send')]",
                "//button[contains(text(),'Request')]",
                "//button"
            ]
            submit_clicked = False
            for xpath in submit_xpaths:
                try:
                    btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", btn)
                    submit_clicked = True
                    break
                except:
                    continue

            if not submit_clicked:
                print("⚠️ Submit button not found.")

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Thank') or contains(text(), 'successfully') or contains(text(), 'response')]")))
                print(f"✅ Confirmation detected for Row {idx+1}")
            except:
                print(f"ℹ️ No confirmation message after submission for Row {idx+1}")

        except Exception as e:
            print(f"⚠️ Submit button failed: {e}")

        print(f"✅ Row {idx+1} submitted successfully.")
        return True

    except Exception as e:
        print(f"❌ Row {idx+1} failed - {e}")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"error_row_{idx+1}.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        return False

# Run automation
failed_rows = []
for idx, row in df.iterrows():
    if not fill_form(driver, row, idx):
        failed_rows.append((idx, row))

# Retry failed rows
for attempt in range(1, MAX_RETRIES + 1):
    if not failed_rows:
        break
    print(f"\n🔁 Retry attempt {attempt}")
    remaining = []
    for idx, row in failed_rows:
        if not fill_form(driver, row, idx):
            remaining.append((idx, row))
    failed_rows = remaining

driver.quit()

# Final report
if failed_rows:
    print("\n❌ Final failed rows:")
    for idx, _ in failed_rows:
        print(f"  - Row {idx+1}")
else:
    print("\n✅ All rows submitted successfully.")
