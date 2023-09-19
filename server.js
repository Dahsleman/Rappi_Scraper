const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs').promises; 
const cors = require('cors');
const config = require('./config');
const ip = require('ip');
const path = require('path');
const ExcelJS = require('exceljs');  
const { exec } = require('child_process');  
const app = express();

app.use(cors());
app.use(bodyParser.json());

app.get('/server-ip', (req, res) => {
  res.send(ip.address());
});

app.post('/run-python', async (req, res) => { 
  exec('python mvp.py 0', async (error, stdout, stderr) => { 
    if (error) {
      console.error(`Error executing script: ${error}`);
      res.status(500).json({ message: 'Failed to run script', error: stderr });
      return;
    }
    console.log(`stdout: ${stdout}`);
    const csvFilePath = './output.csv';
    const csvContent = await fs.readFile(csvFilePath, 'utf8');
    res.json({ message: 'Successfully ran script', output: stdout, csvContent });
  });
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/get-google-maps-key', (req, res) => {
  const { googleMapsApiKey } = config;
  res.json({ googleMapsApiKey });
});

app.post('/save-text', async (req, res) => {
  console.log('Saving text...');
  const text = req.body.text;

  try {
    await appendToExcelSheet(text, 'address'); 
    res.json({ message: 'Text saved' });
  } catch (error) {
    console.error('Error saving text:', error);
    res.status(500).json({ message: 'Failed to save text', error: error.message });
  }
});

app.post('/save-product', async (req, res) => {
  console.log('Saving text...');
  const product = req.body.product;

  try {
    await appendToExcelSheet(product, 'query'); 
    res.json({ message: 'Text saved' });
  } catch (error) {
    console.error('Error saving text:', error);
    res.status(500).json({ message: 'Failed to save text', error: error.message });
  }
});

async function readCsv() {
  const csvFilePath = './output.csv';
  try {
    const csvContent = await fs.readFile(csvFilePath, 'utf8');
    return csvContent;
  } catch (error) {
    console.error("Could not read CSV file:", error);
  }
}

app.get('/get-excel-output', async (req, res) => {
  try {
    const csvContent = await readCsv();
    res.status(200).json({ content: csvContent });
  } catch (error) {
    res.status(500).json({ message: 'Internal Server Error', error: error.toString() });
  }
});

async function appendToExcelSheet(text, tabName) {
  const workbook = new ExcelJS.Workbook();
  
  await workbook.xlsx.readFile('./Workbook.xlsx');
  
  let worksheet = workbook.getWorksheet(tabName);
  if (!worksheet) {
    worksheet = workbook.addWorksheet(tabName);
  }
  
  worksheet.spliceRows(2, 0, [text]);
  
  await workbook.xlsx.writeFile('./Workbook.xlsx');
}

app.listen(3000, () => {
  console.log(`Server running on http://${ip.address()}:3000`);
});
