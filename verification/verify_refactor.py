from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Login
    page.goto("http://localhost:5000/login")
    page.fill("input[name='telephone']", "0600000000")
    page.fill("input[name='pin']", "1234")
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard")
    print("Login successful")

    # Check Dashboard for data-width
    page.goto("http://localhost:5000/dashboard")
    page.wait_for_selector("[data-width]")
    print("Dashboard: data-width found")

    # Check Main Oeuvre for modal classes
    page.goto("http://localhost:5000/main_oeuvre")
    # Check for transition classes
    if page.locator(".transition-opacity").count() > 0:
        print("Main Oeuvre: transition classes found")
    else:
        print("Main Oeuvre: transition classes NOT found")

    # Check Finance Details for data-tab-target
    # Need a chantier ID first. Assuming 1 exists or link exists.
    # Go to finance index first
    page.goto("http://localhost:5000/finance")
    # Click first details link
    page.locator("a[href*='/finance/chantier/']").first.click()
    page.wait_for_selector("[data-tab-target]")
    print("Finance Details: data-tab-target found")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
