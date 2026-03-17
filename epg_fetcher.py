import requests
import json
import os
from datetime import datetime
import time

BASE_URL = "https://jiotvapi.cdn.jio.com/apis/v1.3/getepg/get"
IMAGE_BASE = "https://jiotv.catchup.cdn.jio.com/dare_images/shows"

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Load channels
with open("channels.json", "r") as f:
    channels = json.load(f)

offsets = list(range(-1, 8))  # yesterday → next 7 days

for ch in channels:
    channel_id = ch["channel_id"]
    channel_name = ch.get("channel_name")
    logo_url = ch.get("logo_url")

    print(f"📡 Fetching: {channel_name} ({channel_id})")

    channel_programs = []

    for offset in offsets:
        url = f"{BASE_URL}?channel_id={channel_id}&offset={offset}"

        try:
            res = requests.get(url, timeout=10)

            if res.status_code != 200:
                print(f"❌ Offset {offset} failed")
                continue

            data = res.json()

            for prog in data.get("epg", []):
                start_epoch = prog.get("startEpoch")
                end_epoch = prog.get("endEpoch")

                if not start_epoch or not end_epoch:
                    continue

                start = datetime.fromtimestamp(start_epoch / 1000)
                end = datetime.fromtimestamp(end_epoch / 1000)

                image_path = prog.get("episodePoster") or prog.get("episodeThumbnail")

                item = {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "logo": logo_url,
                    "name": prog.get("showname"),
                    "date": start.strftime("%Y-%m-%d"),
                    "start_time": start.strftime("%H:%M:%S"),
                    "end_time": end.strftime("%H:%M:%S"),
                    "description": prog.get("episode_desc") or prog.get("description"),
                    "image": f"{IMAGE_BASE}/{image_path}" if image_path else None
                }

                channel_programs.append(item)

            time.sleep(0.3)

        except Exception as e:
            print("Error:", e)

    # ✅ Save per channel
    file_path = f"data/{channel_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(channel_programs, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {file_path}")
