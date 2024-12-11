import os
import subprocess
import sys

def set_python_tag(version):
    os.environ['PYTHON_VERSION'] = version

def build_wheel(python_version):
    set_python_tag(python_version)
    subprocess.run(["poetry", "build", "--format", "wheel"])

if __name__ == "__main__":
    python_version = sys.argv[1] if len(sys.argv) > 1 else "3.8"
    build_wheel(python_version)

