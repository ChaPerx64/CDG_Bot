#!/bin/bash
docker stop cdg_bot_container || true && docker rm cdg_bot_container || true
docker build \
--ssh default=./.ssh/id_rsa \
-t chapardev/cdg_bot \
git@github.com:ChaPerx64/CDG_Bot.git
docker run \
--name cdg_bot_container \
--env-file './bots/cdg_bot/.env.prod' \
--mount source=cdg_bot_volume,target=/custom_messages \
--rm -d \
chapardev/cdg_bot
