class NodeCode:
    # Define the Node.js code as a string
    CODE = """
        const puppeteer = require('puppeteer');
        async function scrapeNetworkRequests() {
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            await page.setRequestInterception(true);
            try{
                page.on('request', (request) => {
                    if (request.method() == 'POST' && request.url() == 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-recent-top-searches') {
                        const headersJson = JSON.stringify(request.headers(), null, 2);
                        const headers = JSON.parse(headersJson);
                        const authorization = headers.authorization;
                        console.log(authorization); 
                        process.exit();
                    }
                    request.continue();
                });
                await page.goto('https://www.rappi.com.br/');
                await page.waitForNavigation();
                await browser.close();
            } catch (error){
                console.error('An error occurred:', error);
            }
        }
        scrapeNetworkRequests();
        """