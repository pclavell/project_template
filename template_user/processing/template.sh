#!/bin/bash
# README
#      1) User either config references to files or paths relative to your user
cd $(realpath $(dirname "${BASH_SOURCE[0]}") | sed -E 's#/metadata(/|$)|/processing(/|$)|/analysis(/.*|$)##g')
CONFIGFILE_MN5="./resources/config_mn5.yml"


# example to use yaml parser
MYFILE=$(yq eval '.data.sam' $CONFIGFILE_MN5)
echo $MYFILE

