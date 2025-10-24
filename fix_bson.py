"""
fix_bson.py

Helper script to remove the conflicting standalone `bson` package (if installed) and ensure `pymongo` is installed/upgraded.

Usage (recommended from project venv):
  d:\Manish\Personall\Projects\fastTV\venv\Scripts\activate
  python fix_bson.py

This script runs `pip uninstall -y bson` and then `pip install --upgrade pymongo` using the current Python interpreter.
It prints the location of the `bson` module after the operations so you can confirm the correct `bson` (from pymongo) is in use.
"""

import sys
import subprocess
import importlib


def run(cmd):
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, check=False)
    return res.returncode


def main():
    print("Fixing bson/pymongo packages using Python:", sys.executable)

    # Try to uninstall standalone 'bson' if present
    print("Uninstalling standalone 'bson' (if present)...")
    rc = run([sys.executable, "-m", "pip", "uninstall", "-y", "bson"])
    if rc == 0:
        print("Uninstall command succeeded (or package not present).\n")
    else:
        print("Uninstall command returned non-zero status (may be fine).\n")

    # Ensure pymongo is installed/upgraded
    print("Installing/upgrading pymongo...")
    rc = run([sys.executable, "-m", "pip", "install", "--upgrade", "pymongo"])
    if rc != 0:
        print("Failed to install/upgrade pymongo. Please run the command manually:")
        print(f"{sys.executable} -m pip install --upgrade pymongo")
        sys.exit(1)

    # Show resulting bson module path (if importable)
    try:
        import bson
        print('\nImported bson from:', getattr(bson, '__file__', repr(bson)))
        # Show the module version if available
        try:
            import pymongo
            print('pymongo version:', getattr(pymongo, '__version__', 'unknown'))
        except Exception:
            pass
    except Exception as e:
        print('\nCould not import bson after fix:', e)
        print('If this persists, check for a system/site-wide bson package or virtualenv issues.')
        sys.exit(1)

    print('\nDone. The `bson` package should now be the one provided by pymongo.')


if __name__ == '__main__':
    main()

