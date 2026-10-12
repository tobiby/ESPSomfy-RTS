import os
import subprocess
Import("env")

# Define the folder and filename
DATA_FOLDER = "data-src"
FILENAME = "appversion"

# Construct the full path: /your/project/path/data-src/appversion
project_dir = env.get("PROJECT_DIR")
version_file_path = os.path.join(project_dir, DATA_FOLDER, FILENAME)

# Default fallback if something goes wrong
version = "0.0.0"

if os.path.exists(version_file_path):
    try:
        with open(version_file_path, "r") as f:
            version = f.read().strip()
            # Clean output for the PlatformIO console
            print(f"--- SUCCESS: Found version {version} in {version_file_path} ---")
    except Exception as e:
        print(f"--- ERROR: could not read version file: {e} ---")
else:
    print(f"--- ERROR: File NOT FOUND at {version_file_path} ---")

# Apply to the build environment
# We use escaped quotes so C++ treats it as a string literal "vX.X.X"
full_version_str = f'\\"v{version}\\"'

env.Append(CPPDEFINES=[
    ("FW_VERSION", full_version_str)
])

# ---------------------------------------------------------------------------
# Git revision: lets the UI show exactly which commit is running, e.g.
# "v3.0.14 (32b0313)" or "v3.0.14 (32b0313-dirty)" for uncommitted changes.
# The define is part of the compiler command line, so a new commit forces
# SCons to rebuild every object - no stale objects from an older checkout.
# ---------------------------------------------------------------------------
def _git(*args):
    return subprocess.check_output(["git", *args], cwd=project_dir,
                                   stderr=subprocess.DEVNULL).decode().strip()

git_rev = "nogit"
try:
    git_rev = _git("rev-parse", "--short=7", "HEAD")
    if _git("status", "--porcelain", "--untracked-files=no"):
        git_rev += "-dirty"
except Exception as e:
    print(f"--- WARNING: could not determine git revision: {e} ---")

print(f"--- Git revision: {git_rev} ---")
env.Append(CPPDEFINES=[("FW_GIT_REV", f'\\"{git_rev}\\"')])

# Same revision for the web app (LittleFS image), served as /apprev.
try:
    with open(os.path.join(project_dir, DATA_FOLDER, "apprev"), "w") as f:
        f.write(git_rev)
except Exception as e:
    print(f"--- WARNING: could not write apprev: {e} ---")
