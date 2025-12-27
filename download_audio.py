import os
import requests

# Ensure directory exists
output_dir = os.path.join('static', 'audio')
os.makedirs(output_dir, exist_ok=True)

tracks = {
    'happy_birthday.mp3': 'http://codeskulptor-demos.commondatastorage.googleapis.com/pang/paza-moduless.mp3',
    'wedding_bells.mp3': 'http://commondatastorage.googleapis.com/codeskulptor-assets/Epoq-Lepidoptera.ogg', 
    'party_time.mp3': 'http://codeskulptor-demos.commondatastorage.googleapis.com/GalaxyInvaders/theme_01.mp3',
    'celebration.mp3': 'http://commondatastorage.googleapis.com/codeskulptor-demos/riceracer_assets/music/win.ogg',
    'elegant_classic.mp3': 'http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3',
    'upbeat_pop.mp3': 'http://commondatastorage.googleapis.com/codeskulptor-demos/pyman_assets/intromusic.ogg'
}

print(f"Downloading files to {output_dir}...")

for filename, url in tracks.items():
    path = os.path.join(output_dir, filename)
    try:
        print(f"Downloading {filename} from {url}...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"Success: {filename}")
        else:
            print(f"Failed to download {filename}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("Done.")
