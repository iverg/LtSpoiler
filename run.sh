#!/bin/sh
. ./.venv/bin/activate
if ! [ -r .settings ]; then
    echo "Settings for Lt. Spoiler are not defined."
    echo "Copy settings.template to .settings and update it with actual values."
    exit -1
fi

. ./.settings
python3 ./LtSpoiler.py "$@"
