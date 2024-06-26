#!/bin/bash

which curl || (apt update && apt install curl -y)

TIME="10"
URL="https://api.telegram.org/bot$TG_BOT_TOKEN/sendMessage"
TEXT="Deploy status: $1%0A%0AProject:+$CI_PROJECT_NAME%0AURL:+$CI_PROJECT_URL/pipelines/$CI_PIPELINE_ID/%0ABranch:+$CI_COMMIT_REF_SLUG"

curl -s --fail --max-time $TIME -d "chat_id=$TG_NOTIFICATION_CHAT_ID&disable_web_page_preview=1&text=$TEXT" $URL
