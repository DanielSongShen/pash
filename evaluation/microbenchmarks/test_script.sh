#!/bin/bash
cat $IN | grep '[a-zA-Z0-9]\+@[a-zA-Z0-9]\+\.[a-z]\{2,\}'
