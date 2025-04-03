#!/bin/bash
cd $(dirname $0)
./signal-to-json.sh | ./json-to-logseq.py --read-from-stdin
