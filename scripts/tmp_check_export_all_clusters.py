import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    errors = []
    page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}"))
    page.on("pageerror", lambda err: errors.append(f"pageerror:{err}"))

    page.goto("http://127.0.0.1:8030/clusters", wait_until="networkidle")
    page.select_option("#domain-select", value="https://www.onliner.by")
    page.wait_for_timeout(1300)

    download_events = []
    page.on("download", lambda item: download_events.append(item.suggested_filename))

    page.click("#export-all-clusters-btn")
    page.wait_for_timeout(800)

    result = {
        "downloads": download_events,
        "status": page.inner_text("#clusters-status"),
        "errors": errors,
    }

    with open("/tmp/export_all_clusters_check.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    browser.close()
