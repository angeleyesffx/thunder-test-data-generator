import sys
import os

# Patch sys.argv before any module-level code in environment.py runs.
# environment.py calls parse_args() and reads config at import time,
# so pytest's own argv would cause argparse to exit with code 2.
sys.argv = [
    "main.py",
    "-CONFIG_YAML", "config_test",
    "-ENV", "sit",
]

# Ensure the project root is on the path so imports resolve correctly
# when pytest is run from any working directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
