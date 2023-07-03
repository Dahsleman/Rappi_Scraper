const puppeteer = require('puppeteer');

async function scrapeNetworkDevTools() {
  // Launch a headless Chrome browser
  const browser = await puppeteer.launch();

  // Create a new page
  const page = await browser.newPage();

  // Enable request interception
  await page.setRequestInterception(true);

  // Create an array to store intercepted requests
  const interceptedRequests = [];

  // Listen for request events
  page.on('request', (request) => {
    interceptedRequests.push(request);
    request.continue();
  });

  // Navigate to the desired URL
  await page.goto('https://www.rappi.com.br/');

  // Perform other interactions or wait for the page to load as needed

  // Print the intercepted requests
  for (const request of interceptedRequests) {
    if (request.url() == 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-recent-top-searches' && request.method() == 'POST' ) {
        const headersJson = JSON.stringify(request.headers(), null, 2);
        const headers = JSON.parse(headersJson);
        const authorization = headers.authorization;
        console.log(authorization);
    }
  }

  // Close the browser
  await browser.close();
}

// Run the scraping function
scrapeNetworkDevTools();
