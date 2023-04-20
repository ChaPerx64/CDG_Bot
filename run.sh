#!/bin/bash
SRVR="root@188.225.86.226"
EXECUTABLE="CDG_Bot.py"
TARDIR="/root/bots/cdg_bot_v0"
ssh $SRVR << EOF
pkill -f "$EXECUTABLE"
cd "$TARDIR"
python3 -m venv venv
source venv/bin/activate
nohup python3 "$EXECUTABLE" >/dev/null 2>&1 &
EOF
