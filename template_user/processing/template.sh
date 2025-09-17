#!/bin/bash
USERPATH=realpath $(dirname "${BASH_SOURCE[0]}") | sed -E 's#/metadata(/|$)|/processing(/|$)|/analysis(/.*|$)##g'
cd $USERPATH
# use always relative paths to your user (absolute paths won't work for other users because they have another user_dir)
