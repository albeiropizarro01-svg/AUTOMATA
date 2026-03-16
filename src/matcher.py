import os

stems_folder = "stems"

template_tracks = {
    "DRUMS": ["KICK", "SNARE"],
    "VOCALS": ["LEAD VOCAL"],
    "SYNTHS": ["PAD"],
}

track_usage = {}

print("\nMATCH STEMS → TRACKS\n")

for file in os.listdir(stems_folder):

    if not file.lower().endswith(".wav"):
        continue

    name = file.lower().replace(".wav","")

    for folder, tracks in template_tracks.items():

        for track in tracks:

            key = track.lower().replace(" ","")

            if key in name:

                count = track_usage.get(track,0) + 1
                track_usage[track] = count

                if count == 1:
                    track_name = track
                else:
                    track_name = f"{track} {count}"

                print(f"{file} → {folder} / {track_name}")