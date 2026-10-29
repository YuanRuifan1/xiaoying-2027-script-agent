"""Optional official portable GitHub CLI; installs only inside ignored .tools/."""
import json
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
dest = ROOT / ".tools"
dest.mkdir(exist_ok=True)
request = urllib.request.Request("https://api.github.com/repos/cli/cli/releases/latest", headers={"User-Agent": "script-agent-setup"})
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
    asset = next(a for a in release["assets"] if a["name"].endswith("windows_amd64.zip"))
    name, url = asset["name"], asset["browser_download_url"]
except urllib.error.HTTPError as error:
    if error.code != 403:
        raise
    with urllib.request.urlopen("https://github.com/cli/cli/releases/latest", timeout=30) as response:
        version = response.geturl().rstrip("/").split("/")[-1]
    if not version.startswith("v") or not all(c.isdigit() or c == "." for c in version[1:]):
        raise RuntimeError("could not resolve official release version")
    name = f"gh_{version[1:]}_windows_amd64.zip"
    url = f"https://github.com/cli/cli/releases/download/{version}/{name}"
archive = dest / name
urllib.request.urlretrieve(url, archive)
with zipfile.ZipFile(archive) as package:
    for member in package.infolist():
        target = (dest / member.filename).resolve()
        if not target.is_relative_to(dest.resolve()):
            raise RuntimeError("unsafe archive path")
    package.extractall(dest)
print("Portable CLI:", next(dest.rglob("gh.exe")))
