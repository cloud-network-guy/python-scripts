from pathlib import Path
from os import stat, utime
from pillow_heif import register_heif_opener
from PIL import Image

JPEG_QUALITY = 90
JPEG_OPTIMIZE = True

def main():

    heic_dir = Path(__file__).parent
    register_heif_opener()

    for source_file in heic_dir.iterdir():
        if not source_file.is_file() or not source_file.suffix.lower() == ".heic":
            continue
        # Read the Heic Image
        with Image.open(source_file) as image:
            # Create a new jpg file and save to that files
            jpg_path = Path(source_file.with_suffix(".jpg"))
            if jpg_path.exists():
                print(jpg_path, "already exists.  skipping...")
                continue  # don't touch existing files
            image.save(jpg_path, "JPEG", quality=JPEG_QUALITY, exif=image.info.get("exif"), optimize=JPEG_OPTIMIZE)

        # Preserve the original access and modification timestamps
        heic_stat = stat(source_file)
        utime(jpg_path, (heic_stat.st_atime, heic_stat.st_mtime))


if __name__ == "__main__":

    main()
