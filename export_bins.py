"""
PlatformIO post-build script: export OTA-ready binaries.

After `pio run` / `pio run -t buildfs` the images are copied to
    build/ota/<env>/SomfyController-<gitrev>.ino.<chip>.bin
    build/ota/<env>/SomfyController-<gitrev>.littlefs.<chip>.bin
The names satisfy the web UI upload check (".ino." / ".littlefs" + ".bin")
and carry the git revision, so it is obvious which build is being flashed.
Older files of the same kind in that folder are removed, so there is only
ever one candidate per image to pick.

Usage in platformio.ini
-----------------------
    extra_scripts = post:export_bins.py   (after pre:app_version.py)
"""

Import("env")

import glob
import os
import shutil

CHIP_NAMES = {
    "esp32dev": "esp32",
    "esp32devdbg": "esp32",
}

env_name = env.subst("$PIOENV")
chip = CHIP_NAMES.get(env_name, env_name)
out_dir = os.path.join(env.subst("$PROJECT_DIR"), "build", "ota", env_name)


def _rev():
    rev_file = os.path.join(env.subst("$PROJECT_DIR"), "data-src", "apprev")
    try:
        with open(rev_file) as f:
            return f.read().strip() or "nogit"
    except OSError:
        return "nogit"


def _export(kind, src):
    if not os.path.isfile(src):
        print(f"[export_bins] {src} not found, skipping.")
        return
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, f"SomfyController-*.{kind}.{chip}.bin")):
        os.remove(old)
    dest = os.path.join(out_dir, f"SomfyController-{_rev()}.{kind}.{chip}.bin")
    shutil.copy2(src, dest)
    print(f"[export_bins] {kind:8s} -> {dest}")


def export_firmware(source, target, env):
    _export("ino", os.path.join(env.subst("$BUILD_DIR"), "firmware.bin"))


def export_littlefs(source, target, env):
    _export("littlefs", os.path.join(env.subst("$BUILD_DIR"), "littlefs.bin"))


env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", export_firmware)
env.AddPostAction("$BUILD_DIR/littlefs.bin", export_littlefs)
