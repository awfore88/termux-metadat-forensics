# termux-metadata-forensics
> A Python-based CLI tool for automated metadata extraction and forensic analysis of image and PDF files in mobile sandboxed environments (Termux).

## Termux Forensic Metadata Analyzer (`meta.py`)

### 🕵️ Why I Built This
I’m currently a Cybersecurity student at **ASUMH**, and I wanted to build something that actually solves a problem for an operator in the field. When you’re out on a job, you don't always have a full Linux rig with you. This tool was built to run entirely inside **Termux on Android**, allowing me to do a forensic triage of images, PDFs, and audio files right from my phone (shoutout to my Pixel 8 Pro and my battle-scarred S20+).

This wasn't just a copy-paste job. I used AI to help me understand the "under the hood" logic of how files store data, and then I wrote the code and commented it out to make sure I actually knew what was happening with every byte.

### 🛠 What it Does
This script is a menu-driven CLI tool that handles the "messy" data you find in the real world:
*   **Images (JPG & HEIC):** Extracts EXIF data including device make/model and timestamps.
*   **GPS Mapping:** Follows nested "hex pointers" (like `0x8825`) to find hidden GPS data, converts it from raw degrees/minutes/seconds to decimal degrees, and generates a clickable Google Maps link.
*   **Documents (PDF):** Uses `PyPDF2` to pull Author, Creator, and Producer metadata.
*   **Audio (In Progress):** Foundational logic for `mutagen`-based extraction of bitrate and duration is written; full menu integration and format testing are currently in the dev pipeline.
*   **Automatic Reporting:** Every analysis automatically generates a formatted `.txt` report in the downloads folder for a clean "chain of custody".

### 🧠 What I Learned (The Hard Stuff)
Building this taught me a lot about the reality of digital forensics:
*   **Rational Numbers:** I figured out that Samsung devices store GPS coordinates as fractions (numerator/denominator tuples), so I had to write a converter to make them readable.
*   **Defensive Coding:** I learned to use "if key in dictionary" checks. Real-world files are often missing data, and I didn't want my tool crashing just because a photo didn't have a GPS tag.
*   **Linux/Termux Logic:** Dealing with case-sensitive file extensions (.jpg vs .JPG) and the specific way Termux handles file paths compared to a standard desktop.

### 🗺️ Future Roadmap
*   **Automated Routing:** Implementing automatic file-type detection so the tool chooses the right forensic module without user input.
*   **Wigle WiFi Integration:** Building a parser for wardriving data to visualize wireless network density.
*   **MakerNote Parsing:** Digging deeper into proprietary manufacturer-specific metadata for advanced device fingerprinting.

### 🚀 Getting Started in Termux
To run this on your own mobile lab, you'll need these in Termux:

```bash
pkg update && pkg upgrade
pkg install python python-pillow libheif
pip install pillow-heif PyPDF2 mutagen
termux-setup-storage
python meta.py
```

