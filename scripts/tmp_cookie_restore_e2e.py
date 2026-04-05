"""E2E test: cookie-based domain restoration on keywords and clusters pages."""
import json
from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
context = browser.new_context()
page = context.new_page()

# Step 1: main page, select domain → sets cookies
page.goto('http://127.0.0.1:8030/', wait_until='networkidle')
page.select_option('#saved-url-select', value='https://www.onliner.by')
page.wait_for_timeout(700)
cookies_set = {c['name']: c['value'] for c in context.cookies()}

# Step 2: navigate directly to /keywords (no query params — simulates navbar click)
page.goto('http://127.0.0.1:8030/keywords', wait_until='networkidle')
page.wait_for_timeout(1400)
kw_selected = page.eval_on_selector('#domain-select', 'el => el.value')
kw_status = page.inner_text('#workspace-status')

# Step 3: navigate directly to /clusters (no query params)
page.goto('http://127.0.0.1:8030/clusters', wait_until='networkidle')
page.wait_for_timeout(1400)
cl_selected = page.eval_on_selector('#domain-select', 'el => el.value')
cl_status = page.inner_text('#clusters-status')

result = {
    'cookies_after_main': list(cookies_set.keys()),
    'keywords_selected': kw_selected,
    'keywords_status': kw_status[:200],
    'clusters_selected': cl_selected,
    'clusters_status': cl_status[:200],
}
open('/tmp/cookie_restore_e2e.json', 'w').write(json.dumps(result, ensure_ascii=False, indent=2))
browser.close()
p.stop()
print('DONE')
