"""Advanced anti-bot configuration and stealth scripts."""

# Stealth JavaScript to inject into browser context
STEALTH_JS = """
// Hide webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Override plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {
            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        }
    ]
});

// Override languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en', 'ru']
});

// Override platform
Object.defineProperty(navigator, 'platform', {
    get: () => 'Win32'
});

// Override hardwareConcurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8
});

// Override deviceMemory
Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8
});

// Add chrome object
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};

// Override permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// Override toString methods
const originalToString = Function.prototype.toString;
Function.prototype.toString = function() {
    if (this === window.navigator.permissions.query) {
        return 'function query() { [native code] }';
    }
    return originalToString.call(this);
};

// Hide automation in iframe
Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
    get: function() {
        return window;
    }
});

// Mock battery API
navigator.getBattery = () => Promise.resolve({
    charging: true,
    chargingTime: 0,
    dischargingTime: Infinity,
    level: 1.0
});

// Mock connection API
Object.defineProperty(navigator, 'connection', {
    get: () => ({
        effectiveType: '4g',
        rtt: 100,
        downlink: 10,
        saveData: false
    })
});
"""

# Additional browser args for better stealth
STEALTH_BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--no-sandbox",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-infobars",
    "--window-size=1920,1080",
    "--start-maximized",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
]
