import os

stems_folder = "stems"

template_tracks = {
    "DRUMS": ["KICK", "SNARE"],
    "VOCALS": ["LEAD VOCAL"],
    "SYNTHS": ["PAD"],
}

session_map = {}

for file in os.listdir(stems_folder):

    if not file.lower().endswith(".wav"):
        continue

    name = file.lower().replace(".wav","")

    for folder, tracks in template_tracks.items():

        for track in tracks:

            key = track.lower().replace(" ","")

            if key in name:

                if folder not in session_map:
                    session_map[folder] = {}

                session_map[folder][track] = file

print("\nSESSION MAP\n")

for folder, tracks in session_map.items():

    print(folder)

    for track, stem in tracks.items():
        print("   ", track, "→", stem)