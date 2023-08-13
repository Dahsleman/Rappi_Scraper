#!/bin/bash

echo "install linux dependencies"

sudo apt-get update
sudo apt-get install libasound2 libgbm1 libnss3 libxss1

if command -v python3 &>/dev/null;then
        echo "Python is installed. Version:"
        python3 --version
else
        echo "Erro Python not installed"
        exit 1
fi

if command -v pip &>/dev/null; then
        echo "pip is installed. Version:"
        pip --version
else
        echo "pip is not installed."
        exit 1
fi

if command -v node &>/dev/null; then
        echo "Node.js is installed. Version:"
        node --version
else
        echo "Node.js is not installed."
        exit 1
fi


if command -v npm &>/dev/null; then
        echo "NPM is installed."
else
        echo "NPM is not installed."
        exit 1
fi

current_dir=$(pwd)

echo "============================="
echo "changing workdir"
cd rappi-search

echo "Installing python dependecies"
pip install -r requirements.txt

echo "============================="

echo "Installing node dependencies"
npm i

echo "============================"
echo "============================"

echo "Past this code into sudo crontab (sudo crontab -e)"

echo "*/1 * * * * python3 ${current_dir}/rappi-search/main.py >> ${current_dir}/Rappi_Scraper/log.txt 2>&1"
