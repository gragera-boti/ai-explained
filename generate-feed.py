#!/usr/bin/env python3
"""Generate RSS feed for AI Explained podcast from episodes directory."""

import os
import json
import datetime
from pathlib import Path
from email.utils import formatdate
import time

REPO_URL = "https://gragera-boti.github.io/ai-explained"
PODCAST_TITLE = "AI Explained"
PODCAST_DESC = "Daily bite-sized episodes explaining AI concepts — from quantization to transformers. Narrated by Boti."
PODCAST_AUTHOR = "Boti"
PODCAST_LANGUAGE = "en"
PODCAST_CATEGORY = "Technology"

EPISODES_DIR = Path(__file__).parent / "episodes"
FEED_PATH = Path(__file__).parent / "feed.xml"


def get_episode_info(ep_dir):
    meta_path = ep_dir / "meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path) as f:
        meta = json.load(f)
    mp3_file = ep_dir / f"{ep_dir.name}.mp3"
    if not mp3_file.exists():
        return None
    meta["mp3_size"] = mp3_file.stat().st_size
    meta["mp3_url"] = f"{REPO_URL}/episodes/{ep_dir.name}/{ep_dir.name}.mp3"
    meta["dir_name"] = ep_dir.name
    return meta


def build_feed(episodes):
    now_rfc2822 = formatdate(time.time(), usegmt=True)

    items = ""
    for ep in sorted(episodes, key=lambda e: e["date"], reverse=True):
        pub_date = formatdate(
            time.mktime(
                datetime.datetime.strptime(ep["date"], "%Y-%m-%d").timetuple()
            ),
            usegmt=True,
        )
        items += f"""    <item>
      <title>{escape_xml(ep["title"])}</title>
      <description>{escape_xml(ep["description"])}</description>
      <pubDate>{pub_date}</pubDate>
      <enclosure url="{ep["mp3_url"]}" length="{ep["mp3_size"]}" type="audio/mpeg"/>
      <guid isPermaLink="false">{ep["dir_name"]}</guid>
      <itunes:author>{PODCAST_AUTHOR}</itunes:author>
      <itunes:duration>{ep.get("duration", "10:00")}</itunes:duration>
      <itunes:episode>{ep.get("episode_number", 1)}</itunes:episode>
      <itunes:explicit>false</itunes:explicit>
    </item>
"""

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{PODCAST_TITLE}</title>
    <link>{REPO_URL}</link>
    <description>{PODCAST_DESC}</description>
    <language>{PODCAST_LANGUAGE}</language>
    <lastBuildDate>{now_rfc2822}</lastBuildDate>
    <itunes:author>{PODCAST_AUTHOR}</itunes:author>
    <itunes:category text="{PODCAST_CATEGORY}"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="{REPO_URL}/icon.png"/>
    <itunes:type>episodic</itunes:type>
    <image>
      <url>{REPO_URL}/icon.png</url>
      <title>{PODCAST_TITLE}</title>
      <link>{REPO_URL}</link>
    </image>
{items}  </channel>
</rss>"""

    with open(FEED_PATH, "w") as f:
        f.write(feed)
    print(f"Feed written with {len(episodes)} episodes")


def escape_xml(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


if __name__ == "__main__":
    episodes = []
    if EPISODES_DIR.exists():
        for ep_dir in sorted(EPISODES_DIR.iterdir()):
            if ep_dir.is_dir():
                info = get_episode_info(ep_dir)
                if info:
                    episodes.append(info)
    build_feed(episodes)
