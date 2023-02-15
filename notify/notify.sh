#!/bin/bash

export TELEGRAM_TOKEN=REDACTED


cat <<EOF | ./build/telegram-send 123456
🚨🚨 [$PAM_SERVICE] [$PAM_TYPE] PAM Event on $(hostname) at $(date -Ins)
<code>
USER:  $PAM_RUSER
TTY:   $PAM_TTY
RHOST: $PAM_RHOST

$(printenv | grep -Ev 'LC_PAPER|LS_COLORS')
</code>
EOF