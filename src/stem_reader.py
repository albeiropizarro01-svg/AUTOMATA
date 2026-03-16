import os

stems_folder = "stems"

print("\nSTEMS DETECTADOS:\n")

for file in os.listdir(stems_folder):

    if file.lower().endswith((".wav", ".aif", ".aiff")):
        print("-", file)