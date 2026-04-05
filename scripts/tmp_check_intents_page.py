import json
from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page()
errors = []
page.on('console', lambda msg: errors.append(f'{msg.type}:{msg.text}') if msg.type == 'error' else None)
page.on('pageerror', lambda err: errors.append(f'pageerror:{err}'))

page.goto('http://127.0.0.1:8030/intents', wait_until='networkidle')
page.wait_for_timeout(1200)

title = page.title()
scope_opts = page.locator('#scope-select option').evaluate_all('els => els.map(el => el.textContent.trim())')
status_text = page.inner_text('#phrases-status')

# Add a test global phrase
page.select_option('#new-intent', 'transactional')
page.fill('#new-phrase', 'тестовая фраза')
page.click('#add-btn')
page.wait_for_timeout(900)

add_status_el = page.locator('#add-status')
add_status = add_status_el.inner_text() if add_status_el.count() else ''
phrases_text = page.inner_text('#phrases-container')[:400]
status_after = page.inner_text('#phrases-status') if page.is_visible('#phrases-status') else ''

result = {
    'title': title,
    'scope_options': scope_opts,
    'initial_status': status_text,
    'add_status': add_status,
    'phrases_preview': phrases_text,
    'status_after': status_after,
    'errors': errors,
}
open('/tmp/intents_page_check.json', 'w').write(json.dumps(result, ensure_ascii=False, indent=2))
browser.close()
p.stop()
print('Done')
