#!/bin/bash
# vim: set ft=bash

testfile="$HOME/signalcli-messages.json"
tel=$(cat config.json | jq -r ".tel")

# signal-cli -a "$tel" -o json receive > $testfile
# messages=$(cat "$testfile")
messages=$(signal-cli -a $tel -o json receive)

messages=$(echo "$messages" | jq --arg tel "$tel" '.envelope|select(.source==$tel).syncMessage.[]')
messages=$(echo "$messages" | jq --arg tel "$tel" 'select(.destination==$tel)') # Select Note to Self
# messages=$(echo "$messages" | jq --arg groupId "TODO" 'select(.groupInfo.groupId=="$groupId")' # Select some group by groupid
#
messages=$(echo $messages | jq  '{
  message: .message,
  timestamp: .timestamp,
  attachments: (.attachments // []) | map({id: .id, filename: .filename})
}')

echo $messages | jq -s

