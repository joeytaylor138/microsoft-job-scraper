from playwright.sync_api import sync_playwright

URL = "https://apply.careers.microsoft.com/careers"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_timeout(5000)

    buttons = page.query_selector_all("button")
    for i, btn in enumerate(buttons):
        text = btn.inner_text().strip()
        aria = btn.get_attribute("aria-label")
        if aria and ('job' in aria.lower() or 'page' in aria.lower() or 'next' in aria.lower() or 'pagination' in aria.lower()):
            print(f"Button {i}: aria-label={aria!r}, text={text!r}")

    browser.close()