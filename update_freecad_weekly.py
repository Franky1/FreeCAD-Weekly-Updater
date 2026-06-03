# pylint: disable=C0301
"""
This script updates the FreeCAD weekly 7z archive with the latest TAG version of FreeCAD from Github Releases:

https://github.com/FreeCAD/FreeCAD/releases

It performs the following steps:

1. Get the absolute path of the script and its directory.
2. Change the current working directory to the script's directory.
3. Fetch the latest release TAG information from GitHub.
4. Read local file "update_freecad_weekly.txt" to get the local version.
5. Compare the latest release TAG with the local version.
6. If a newer TAG is available, download the latest FreeCAD archive named "FreeCAD_weekly-YYYY.MM.DD-Windows-x86_64.7z" to the local directory.
7. Delete all files in the local directory except *.7z files and except all update_freecad_weekly.* files.
8. Delete the old archive 7z file in the local directory if it exists.
9. Unpack the downloaded 7z archive in the local directory.
10. If successful, update "update_freecad_weekly.txt" with the new TAG version.

"""

import json
import os
import shutil
import stat
import subprocess
import urllib.request
from pathlib import Path

GITHUB_API_URL = "https://api.github.com/repos/FreeCAD/FreeCAD/releases"
VERSION_FILE = "update_freecad_weekly.txt"
ASSET_PREFIX = "FreeCAD_weekly-"
ASSET_SUFFIX = "-Windows-x86_64.7z"


def fetch_latest_release() -> dict:
    """Return the most recent release that has the matching Windows .7z asset, including pre-releases."""
    req = urllib.request.Request(
        url=GITHUB_API_URL,
        headers={"User-Agent": "python-urllib/3.11"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        releases: list[dict] = json.loads(response.read().decode())
    for release in releases:
        if any(
            asset["name"].startswith(ASSET_PREFIX)
            and asset["name"].endswith(ASSET_SUFFIX)
            for asset in release.get("assets", [])
        ):
            return release
    raise FileNotFoundError("No release with a matching Windows .7z asset found")


def find_asset(release: dict) -> tuple[str, str, int]:
    """Return (tag_name, download_url, size_in_bytes) for the Windows x86_64 .7z asset in the release."""
    tag = release["tag_name"]
    for asset in release.get("assets", []):
        name: str = asset["name"]
        if name.startswith(ASSET_PREFIX) and name.endswith(ASSET_SUFFIX):
            return tag, asset["browser_download_url"], asset["size"]
    raise FileNotFoundError(f"No Windows .7z asset found for release {tag}")


def get_local_version(version_file: Path) -> str:
    """Read the locally installed TAG from the version file, or return an empty string if absent."""
    return (
        version_file.read_text(encoding="utf-8").strip()
        if version_file.exists()
        else ""
    )


def download_file(url: str, dest: Path) -> None:
    """Download url to dest in 1 MB chunks, printing progress to stdout."""
    print(f"Downloading {dest.name} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "python-urllib/3.11"})
    with urllib.request.urlopen(req) as response, dest.open("wb") as out:
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
            downloaded += len(chunk)
            if total:
                print(
                    f"\r  {downloaded / total * 100:.1f}%  ({downloaded >> 20} / {total >> 20} MB)",
                    end="",
                    flush=True,
                )
    print()


def find_7zip() -> str:
    """Return the path to the 7-Zip executable, checking PATH then common install locations."""
    candidates = (
        "7z",
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    )
    for candidate in candidates:
        try:
            if subprocess.run(
                args=[candidate, "--help"],
                capture_output=True,
                timeout=5,
                check=False,
            ).returncode in (0, 1):
                return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    raise FileNotFoundError("7-Zip not found. Install it from https://www.7-zip.org/")


def _force_remove(func, path, _) -> None:
    """onerror handler for shutil.rmtree: clear read-only bit and retry."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clean_directory(script_dir: Path, new_archive: Path) -> None:
    """Remove old files and directories from script_dir, keeping new_archive and update_freecad_weekly.* files."""
    print("Removing old installation files ...")
    removed = 0
    for item in script_dir.iterdir():
        if item.name.startswith("update_freecad_weekly."):
            continue
        if item.suffix == ".7z":
            if item != new_archive:
                print(f"  Deleting old archive: {item.name}")
                item.unlink()
            continue
        print(f"  Deleting: {item.name}")
        if item.is_dir():
            shutil.rmtree(item, onerror=_force_remove)
        else:
            item.unlink()
        removed += 1
    print(f"Removed {removed} item(s).")


def unpack_archive(archive: Path) -> None:
    """Extract archive into its parent directory, flattening a single embedded top-level folder."""
    seven_zip: str = find_7zip()
    extract_dir: Path = archive.parent / ".freecad_extract_tmp"
    if extract_dir.exists():
        print("Removing leftover temporary extraction folder ...")
        shutil.rmtree(extract_dir, onerror=_force_remove)

    size_mb: int = archive.stat().st_size >> 20
    print(f"Extracting {archive.name} ({size_mb} MB) with 7-Zip ...")
    print("This can take several minutes; 7-Zip progress is shown below:")
    # -bsp1 streams progress percentage to stdout; stderr is captured for errors.
    result: subprocess.CompletedProcess[str] = subprocess.run(
        args=[seven_zip, "x", str(archive), f"-o{extract_dir}", "-y", "-bsp1"],
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        shutil.rmtree(extract_dir, onerror=_force_remove)
        raise RuntimeError(f"7-Zip extraction failed:\n{result.stderr}")
    print("Extraction complete.")

    # If the archive wraps everything in a single top-level folder, strip it
    # so the contents land directly in archive.parent.
    extracted: list[Path] = list(extract_dir.iterdir())
    source_dir: Path = (
        extracted[0] if len(extracted) == 1 and extracted[0].is_dir() else extract_dir
    )
    if source_dir is not extract_dir:
        print(
            f"Flattening embedded folder '{source_dir.name}' into the local directory ..."
        )
    items: list[Path] = list(source_dir.iterdir())
    for index, item in enumerate(items, start=1):
        print(f"  Moving {index}/{len(items)}: {item.name}")
        shutil.move(str(item), str(archive.parent / item.name))

    print("Cleaning up temporary extraction folder ...")
    shutil.rmtree(extract_dir, onerror=_force_remove)


def main() -> None:
    """Check for a new FreeCAD weekly release and update the local installation if one is available."""
    script_dir: Path = Path(__file__).resolve().parent
    os.chdir(script_dir)

    print("Fetching latest FreeCAD release from GitHub ...")
    release: dict = fetch_latest_release()
    latest_tag, download_url, asset_size = find_asset(release)
    print(f"Latest: {latest_tag}")

    version_file: Path = script_dir / VERSION_FILE
    local_version: str = get_local_version(version_file)
    print(f"Local:  {local_version or '(none)'}")

    if latest_tag == local_version:
        print("Already up to date.")
        return

    print(f"New version available: {local_version or '(none)'} -> {latest_tag}")

    new_archive: Path = script_dir / Path(download_url).name
    if new_archive.exists() and new_archive.stat().st_size == asset_size:
        print(f"{new_archive.name} already downloaded; skipping download.")
    else:
        download_file(download_url, new_archive)
    clean_directory(script_dir, new_archive)
    unpack_archive(new_archive)

    version_file.write_text(latest_tag, encoding="utf-8")
    print(f"Done. Updated to {latest_tag}.")


if __name__ == "__main__":
    main()
