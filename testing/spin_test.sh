#!/usr/bin/env bash
#
# Script Name: spin_test.sh
# Description: Spins the bot as some kind of testing.

while :; do
curl 'http://192.168.51.94:5000/cmd' \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Tef; x64; rv:149.0) Gecko/20100101 Firefox/149.0' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Referer: http://192.168.51.94:5000/' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://192.168.51.94:5000' \
  -H 'Connection: keep-alive' \
  -H 'Priority: u=0' \
  --data-raw '{"command":"SPIN_LEFT"}'
  sleep 0.5
done