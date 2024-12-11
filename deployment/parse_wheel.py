import os
import re
import zipfile


def parse_wheel_filename(full_path):
    # Extract just the filename from the full path
    filename = os.path.basename(full_path)

    # Regular expression to match wheel filename components
    pattern = r"^(?P<distribution>.+?)-(?P<version>\d+(\.\d+)*)"
    pattern += r"(-(?P<build>\d+))?-(?P<python_tag>.+?)-(?P<abi_tag>.+?)-(?P<platform_tag>.+?)\.whl$"

    match = re.match(pattern, filename)
    if not match:
        raise ValueError(f"Invalid wheel filename: {filename}")

    components = match.groupdict()
    components["full_path"] = full_path
    return components


def parse_wheel_content(content):
    wheel_info = {}
    for line in content.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "Tag":
                if "Tags" not in wheel_info:
                    wheel_info["Tags"] = []
                wheel_info["Tags"].append(value)
            else:
                wheel_info[key] = value

    # Extract python, abi, and platform tags from the first Tag
    if "Tags" in wheel_info and wheel_info["Tags"]:
        python_tag, abi_tag, platform_tag = wheel_info["Tags"][0].split("-")
        wheel_info["Python-Tag"] = python_tag
        wheel_info["ABI-Tag"] = abi_tag
        wheel_info["Platform-Tag"] = platform_tag

    return wheel_info


def get_wheel_metadata(filename):
    try:
        with zipfile.ZipFile(filename, "r") as zf:
            wheel_file_path = next(
                (f for f in zf.namelist() if f.endswith("/WHEEL")), None
            )
            if not wheel_file_path:
                return "WHEEL file not found in the archive."

            wheel_content = zf.read(wheel_file_path).decode("utf-8")
            return parse_wheel_content(wheel_content)
    except zipfile.BadZipFile:
        return "The file is not a valid zip file."
    except Exception as e:
        return f"Error reading WHEEL metadata: {str(e)}"


def parse_wheel(filename):
    # Parse filename
    try:
        components = parse_wheel_filename(filename)
        print("Filename components:")
        for key, value in components.items():
            if (
                value and key != "full_path"
            ):  # Only print non-None values, exclude full_path
                print(f"  {key}: {value}")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Get internal metadata
    wheel_data = get_wheel_metadata(filename)
    print("\nInternal WHEEL metadata:")
    if isinstance(wheel_data, dict):
        for key, value in wheel_data.items():
            print(f"  {key}: {value}")
    else:
        print(wheel_data)

    # List all files in the wheel
    print("\nFiles in the wheel:")
    try:
        with zipfile.ZipFile(filename, "r") as zf:
            for file in zf.namelist():
                print(f"  {file}")
    except Exception as e:
        print(f"Error listing files: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <wheel_filename>")
    else:
        parse_wheel(sys.argv[1])
