#!/bin/bash
docker stop cdg_bot_container || true && docker rm cdg_bot_container || true
docker build -t chapardev/cdg_bot .
docker run \
--name cdg_bot_container \
--env-file '.env.dev' \
--mount source=cdg_bot_volume,target=/custom_messages \
--rm \
chapardev/cdg_bot
docker image prune
