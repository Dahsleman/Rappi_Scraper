const puppeteer = require('puppeteer');

async function scrapeNetworkRequests() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Enable request interception
  await page.setRequestInterception(true);

  try{
    // Listen to the request event
  page.on('request', (request) => {
    if (request.method() == 'POST' && request.url() == 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-recent-top-searches') {
      // console.log('Request URL:', request.url());
      // console.log('Request Method:', request.method());
      // console.log('Request Headers:', request.headers());
      // console.log('--------------------'); 
      const headersJson = JSON.stringify(request.headers(), null, 2);
      const headers = JSON.parse(headersJson);
      const authorization = headers.authorization;
      console.log(authorization); 
      process.exit();
    }
    request.continue();
  });
  // Increase the navigation timeout to 120 seconds (60000 milliseconds)
  // await page.setDefaultNavigationTimeout(3000);

  // Navigate to the Rappi website
  await page.goto('https://www.rappi.com.br/');

  // Wait for the page to load
  await page.waitForNavigation();

  // Close the browser
  await browser.close();

  } catch (error){
    console.error('An error occurred:', error);
  }
}

scrapeNetworkRequests();
