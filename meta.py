# === IMPORTS ===
import glob        # finds files matching patterns like *.heic
import os          # talks to operating system for file paths/timestamps
from PIL import Image                    # opens and reads image files
from PIL.ExifTags import TAGS, GPSTAGS  # translation dictionaries for
                                         # numeric IDs to human names
from pillow_heif import register_heif_opener  # plugin for HEIC support
register_heif_opener()  # activates the HEIC plugin immediately

# === MENU FUNCTION === 
def main_menu():
    while True:  # keep showing menu until user exits
        print("\n=== METADATA FORENSIC ANALYZER ===")
        print("1. Analyze newest picture")
        print("2. Analyze specific file")
        print("3. Analyze entire folder")
        print("4. Analyze PDF")
        print("5. Analyze Audio")
        print("6. Exit")
        
        choice = input("\nChoose an option: ")
        
        if choice == "1":
            analyze_newest_pic()
        elif choice == "2":
            analyze_specific_file()
        elif choice == "3":
            folder = input("Enter folder path: ")
            analyze_folder(folder)
        elif choice == "4":
            pdf_menu()
        elif choice == "5":
            audio_menu ()
        elif choice == "6":
            print("Closing analyzer.")
            break  # exits the while loop
        else:
            print("Invalid option, try again.")



# === FUNCTION 1: CONVERT RAW GPS TO DECIMAL DEGREES ===
def convert_gps(coord, ref):
    # each coord value may be a fraction tuple (numerator, denominator)
    # or already a float — handle both cases
    def to_decimal(value):
        if isinstance(value, tuple):
            return value[0] / value[1]  # divide numerator by denominator
        return float(value)  # already a number, just convert to float
    
    degrees = to_decimal(coord[0])
    minutes = to_decimal(coord[1]) / 60
    seconds = to_decimal(coord[2]) / 3600
    
    decimal = degrees + minutes + seconds
    
    if ref in ["S", "W"]:
        decimal *= -1
    
    return round(decimal, 6)  # round to 6 decimal places


# === FUNCTION 2: EXTRACT GPS DATA FROM IMAGE ===
def extract_gps(image):
    # follow the pointer to the GPS nested block
    # 0x8825 is the universal EXIF address for GPS data
    exif_data = image.getexif().get_ifd(0x8825)
    
    gps_info = {}  # empty dictionary to store results in
    
    for tag_id, value in exif_data.items():
        # tag_id is a raw number like 1, 2, 3
        # GPSTAGS.get() translates it to "GPSLatitude" etc
        # second argument means: if no translation exists,
        # just keep the raw number instead of crashing
        tag = GPSTAGS.get(tag_id, tag_id)
        gps_info[tag] = value  # store as human name → value pair
    
    return gps_info  # hand the completed dictionary back


# === FUNCTION 3: WRITE REPORT TO TEXT FILE ===
def write_report(filepath, metadata, gps):
    # create report filename based on the image filename
    # os.path.basename strips the folder path, leaving just the filename
    report_name = os.path.expanduser("~/storage/downloads/") + os.path.basename(filepath) + "_report.txt"
    
    # open file for writing — "w" means write mode
    # "with" automatically closes the file when done
    with open(report_name, "w") as f:
        f.write("=== METADATA FORENSIC REPORT ===\n")  # \n = new line
        f.write(f"File: {filepath}\n\n")  # \n\n = blank line after
        
        f.write("--- EXIF DATA ---\n")
        for tag, value in metadata.items():
            f.write(f"{tag}: {value}\n")  # write every EXIF field
        
        if gps:  # only write GPS section if GPS data exists
            f.write("\n--- GPS DATA ---\n")
            for key, value in gps.items():
                f.write(f"{key}: {value}\n")  # write raw GPS fields
            
            # convert raw DMS coordinates to decimal degrees
            # pass the coordinate tuple AND the direction reference
            if "GPSLatitude" in gps and "GPSLongitude" in gps:
                lat = convert_gps(gps["GPSLatitude"], gps["GPSLatitudeRef"])
                lon = convert_gps(gps["GPSLongitude"], gps["GPSLongitudeRef"])
                f.write(f"\nDecimal Coordinates: {lat}, {lon}\n")
                f.write(f"Google Maps: https://maps.google.com/?q={lat},{lon}\n")
            
            # write the converted decimal coordinates
            # build a clickable Google Maps link using those coordinates
    
    # confirm to the terminal that the report was saved
    print(f"Report saved as {report_name}")


# === FUNCTION 4: MAIN METADATA EXTRACTION ===
def extract_image_metadata(filepath):
    image = Image.open(filepath)   # open the image file
    exif_data = image.getexif()    # pull all EXIF data out of it
    
    if not exif_data:              # if nothing came back, bail out
        print("No EXIF data found.")
        return
    
    # build a dictionary of all metadata for passing to report writer
    metadata = {}
    for tag_id, value in exif_data.items():
        # translate numeric ID to human readable name
        tag = TAGS.get(tag_id, tag_id)
        metadata[tag] = value      # store it
        print(f"{tag}: {value}")   # also print to screen
    
    # extract GPS data by calling Function 2
    gps = extract_gps(image)
    
    if gps:  # only print GPS section if data exists
        print("\n--- GPS DATA ---")
        for key, value in gps.items():
            print(f"{key}: {value}")
    
    # call the report writer, passing filepath, all metadata, and gps
    write_report(filepath, metadata, gps)


# === FUNCTION 5: NEWEST HEIC OR JPG FILE FROM CAMERA ===
def analyze_newest_pic():
    extensions = ["*.heic", "*.HEIC", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]
    all_files = []
    for ext in extensions:
        all_files += glob.glob(os.path.expanduser("~/storage/dcim/Camera/" + ext))
    if not all_files:
        print("No files found.")
        return
    latest = max(all_files, key=os.path.getmtime)
    print(f"\nAnalyzing: {latest}")
    extract_image_metadata(latest)


# === FUNCTION 6: ALL HEIC OR JPG FILES IN FILEPATH FOLDER ===
def analyze_folder(folder):
    extensions = ["*.heic", "*.HEIC", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]
    all_files = []
    for ext in extensions:
        all_files += glob.glob(os.path.expanduser(folder + "/" + ext))
    if not all_files:
        print ("No files found")
        return
    for filepath in all_files:
        print(f"\nAnalyzing: {filepath}")
        extract_image_metadata(filepath)


# === FUNCTION 7: ANALYZE FILEPATH ===
def analyze_specific_file():
    folder = input("Enter folder to search:")
    extensions = ["*.heic", "*.HEIC", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]
    all_files = []
    for ext in extensions:
        all_files += glob.glob(os.path.expanduser(folder + "/" + ext))
    recent = sorted(all_files, key=os.path.getmtime, reverse=True)[:5]
    print("\nRecent files:")
    for i, f in enumerate(recent):
        print(f"{i+1}. {os.path.basename(f)}")
    print("6. Enter filepath manually")
    
    choice = input("\nChoose a number: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(recent):
        extract_image_metadata(recent[int(choice)-1])
    elif choice == "6":
        filepath = input("Enter filepath: ")
        extract_image_metadata(filepath)
    else:
        print("Invalid choice.")


# === FUNCTION 8: WRITE PDF REPORT ===
def write_pdf_report(filepath, metadata):
    report_name = os.path.expanduser("~/storage/downloads/") + os.path.basename(filepath) + "_report.txt"

    with open(report_name, "w") as f:
        f.write("=== PDF FORENSIC REPORT ===\n")
        f.write(f"File: {filepath}\n\n")
        f.write("--- PDF METADATA ---\n")
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")

    print(f"Report saved as {report_name}")


# === FUNCTION 9: EXTRACT PDF METADATA ===
def extract_pdf_metadata(filepath):
    from PyPDF2 import PdfReader  # import here, only needed for PDFs

    reader = PdfReader(filepath)
    metadata = reader.metadata  # PyPDF2's built in metadata object

    if not metadata:
        print("No metadata found.")
        return

    pdf_metadata = {}
    for key, value in metadata.items():
        # PyPDF2 keys look like "/Author", "/Title" with a leading slash
        clean_key = key.lstrip("/")  # remove the leading slash for readability
        pdf_metadata[clean_key] = value
        print(f"{clean_key}: {value}")

    write_pdf_report(filepath, pdf_metadata)


# === FUNCTION 10: PDF SUBMENU ===
def pdf_menu():
    while True:
        print("\n=== PDF ANALYZER ===")
        print("1. Analyze specific PDF")
        print("2. Analyze newest PDF in folder")
        print("3. Analyze all PDFs in folder")
        print("4. Return to Main Menu")
        
        choice = input("\nChoose an option: ")
        if choice == "1":
            folder = input("Enter folder to search: ")
            pdfs = glob.glob(os.path.expanduser(folder + "/*.pdf")) + \
            glob.glob(os.path.expanduser(folder + "/*.PDF"))
    
            if not pdfs:
                print("No PDFs found in that folder.")
            else:
                recent = sorted(pdfs, key=os.path.getmtime, reverse=True)[:5]
        
                print("\nRecent PDFs:")
                for i, f in enumerate(recent):
                    print(f"{i+1}. {os.path.basename(f)}")
                    print(f"{len(recent)+1}. Enter filepath manually")
        
                    pick = input("\nChoose a number: ")
        
                    if pick.isdigit() and 1 <= int(pick) <= len(recent):
                        extract_pdf_metadata(recent[int(pick)-1])
                    elif pick == str(len(recent)+1):
                        filepath = input("Enter filepath: ")
                        extract_pdf_metadata(filepath)
                    else:
                        print("Invalid choice.")
        elif choice == "2":
            folder = input("Enter folder path: ")
            pdfs = glob.glob(os.path.expanduser(folder + "/*.pdf")) + glob.glob(os.path.expanduser(folder + "/*.PDF"))
            if not pdfs:
                print("No PDFs found.")
            else:
                latest = max(pdfs, key=os.path.getmtime)
                print(f"\nAnalyzing: {latest}")
                extract_pdf_metadata(latest)
        elif choice == "3":
            folder = input("Enter folder path: ")
            pdfs = glob.glob(os.path.expanduser(folder + "/*.pdf")) + glob.glob(os.path.expanduser(folder + "/*.PDF"))
            if not pdfs:
                print("No PDFs found.")
            else:
                for filepath in pdfs:
                    print(f"\nAnalyzing: {filepath}")
                    extract_pdf_metadata(filepath)
        elif choice == "4":
            break
        else:
            print("Invalid option, try again")

# === FUNCTION 11: EXTRACT AUDIO METADATA ===
def extract_audio_metadata(filepath):
    from mutagen import File
    
    audio = File(filepath)  # mutagen auto-detects the format
    
    if audio is None:
        print("Could not read file or no metadata found.")
        return
    
    print(f"\nFormat: {type(audio).__name__}")  # prints MP3, OGG etc
    
    audio_metadata = {}
    for key, value in audio.items():
        # mutagen returns values as lists, so join them into a string
        clean_value = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
        audio_metadata[key] = clean_value
        print(f"{key}: {clean_value}")
    
    # also grab technical info like duration and bitrate
    if hasattr(audio, 'info'):
        info = audio.info
        if hasattr(info, 'length'):
            duration = round(info.length, 2)
            audio_metadata['Duration'] = f"{duration} seconds"
            print(f"Duration: {duration} seconds")
        if hasattr(info, 'bitrate'):
            audio_metadata['Bitrate'] = f"{info.bitrate} bps"
            print(f"Bitrate: {info.bitrate} bps")
    
    write_audio_report(filepath, audio_metadata)


# === FUNCTION 12: WRITE AUDIO REPORT ===
def write_audio_report(filepath, metadata):
    report_name = os.path.expanduser("~/storage/downloads/") + os.path.basename(filepath) + "_report.txt"
    
    with open(report_name, "w") as f:
        f.write("=== AUDIO FORENSIC REPORT ===\n")
        f.write(f"File: {filepath}\n\n")
        f.write("--- AUDIO METADATA ---\n")
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f"Report saved as {report_name}")


# === FUNCTION 13: AUDIO SUBMENU ===
def audio_menu():
    while True:
        print("\n=== AUDIO ANALYZER ===")
        print("1. Analyze specific audio file")
        print("2. Analyze newest audio file in folder")
        print("3. Analyze all audio files in folder")
        print("4. Return to Main Menu")

        extensions = ["*.mp3", "*.ogg", "*.wav", "*.amr",
                      "*.m4a", "*.flac", "*.opus", "*.wma",
                      "*.aiff", "*.mp4"]

        choice = input("\nChoose an option: ")
        if choice == "1":
            folder = input("Enter folder to search: ")
            all_files = []
            for ext in extensions:
                all_files += glob.glob(os.path.expanduser(folder + "/" + ext))

            if not all_files:
                print("No audio files found in that folder.")
            else:
                recent = sorted(all_files, key=os.path.getmtime, reverse=True)[:5]

                print("\nRecent audio files:")
                for i, f in enumerate(recent):
                    print(f"{i+1}. {os.path.basename(f)}")
                print(f"{len(recent)+1}. Enter filepath manually")

                pick = input("\nChoose a number: ")

                if pick.isdigit() and 1 <= int(pick) <= len(recent):
                    extract_audio_metadata(recent[int(pick)-1])
                elif pick == str(len(recent)+1):
                    filepath = input("Enter filepath: ")
                    extract_audio_metadata(filepath)
                else:
                    print("Invalid choice.")
        elif choice == "2":
            folder = input("Enter folder path: ")
            all_files = []
            for ext in extensions:
                all_files += glob.glob(os.path.expanduser(folder + "/" + ext))
            if not all_files:
                print("No audio files found.")
            else:
                latest = max(all_files, key=os.path.getmtime)
                print(f"\nAnalyzing: {latest}")
                extract_audio_metadata(latest)
        elif choice == "3":
            folder = input("Enter folder path: ")
            all_files = []
            for ext in extensions:
                all_files += glob.glob(os.path.expanduser(folder + "/" + ext))
            if not all_files:
                print("No audio files found.")
            else:
                for filepath in all_files:
                    print(f"\nAnalyzing: {filepath}")
                    extract_audio_metadata(filepath)
        elif choice == "4":
            break
        else:
            print("Invalid option, try again")

# === MAIN EXECUTION ===

main_menu()
