# LtSpoiler
Somebody sent you or to a group chat a link to a YouTube video, but you are not sure if it is worth watching?
Leutenant Spoiler to the rescue! It will reply to the message with a summary of the video content (yes, there will be spoilers).

## Installation

Create virtual environment .venv
```
python3 -m venv .venv
```

Install depdendencies
```
. .venv/bin/activate; python3 -m pip install -r requirements.txt
```

Configure parameters - copy settings template
```
cp settings.template .settings
```
and set actual values in your `.settings` file.

## Run
Run your bot
```
./run.sh
```
