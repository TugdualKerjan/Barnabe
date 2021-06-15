#!/bin/sh
sudo cp ./main.py /usr/lib/main.py

pip3 install python-vlc pafy python-dotenv python-telegram-bot youtube-search-python

sudo cp ./barnabe.service /lib/systemd/system/
sudo systemctl enable barnabe
