#!/bin/sh

# Script to provide a one line install for the Raspberry Pi.
# 
# Motivating use case:
# - To be able to provide consise and robust instructions for installing a basic
#   Raspberry Pi setup.
#   
# Usage:
# 
# curl -L https://github.com/rjw57/yt/raw/master/tools/install-pi.sh | sh
# wget --no-check-certificate https://github.com/rjw57/yt/raw/master/tools/install-pi.sh -O - | sh

echo "[yt installer] Installing programs to be able to download YouTube videos and to play them."
sudo apt-get install omxplayer youtube-dl

echo "[yt installer] Making sure the YouTube downloader is up to date."
sudo youtube-dl -U

echo "[yt installer] Installing yt."
sudo apt-get install python-setuptools
sudo easy_install --upgrade whitey

echo "[yt_installer] Starting yt!"
pi-yt
