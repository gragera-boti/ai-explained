#!/bin/bash
# Generate a podcast episode. Called by the cron job agent after it writes the script.
# Usage: ./generate-episode.sh <episode_number> <slug> <script_file>

set -e

EPISODE_NUM=$1
SLUG=$2
SCRIPT_FILE=$3
VOICE="en-US-AndrewNeural"
RATE="-5%"

EP_DIR="$(dirname "$0")/episodes/$(printf '%03d' $EPISODE_NUM)-${SLUG}"
MP3_FILE="${EP_DIR}/$(printf '%03d' $EPISODE_NUM)-${SLUG}.mp3"

mkdir -p "$EP_DIR"
cp "$SCRIPT_FILE" "$EP_DIR/script.txt"

echo "Generating audio with voice ${VOICE}..."
~/.local/share/edge-tts-venv/bin/edge-tts --voice "$VOICE" --rate="$RATE" --file "$EP_DIR/script.txt" --write-media "$MP3_FILE"

echo "Regenerating feed..."
cd "$(dirname "$0")"
python3 generate-feed.py

echo "Pushing to GitHub..."
git add -A
git commit -m "Episode $(printf '%03d' $EPISODE_NUM): ${SLUG}"
git push origin main

echo "Done: $MP3_FILE"
