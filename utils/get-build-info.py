#!/usr/bin/python
import subprocess
import re
from datetime import datetime
import json
from pathlib import Path
import sys

# Execute the `cmake --system-information` command and capture its output
cmake_output = subprocess.check_output(
    ["cmake", "--system-information"],
    encoding="utf-8",
    universal_newlines=True
)

# Initialize a dictionary to store (variable, value) pairs
cmake_info = {}

# Filter relevant section ("VARIABLES")
cmake_lines = []
record = False
for line in cmake_output.splitlines():
    # Skip empty lines or separators
    if line.strip() == "" or line.startswith("//") or line.startswith("==========="):
        continue
    if line.startswith("==="):
        record = "VARIABLES" in line
        continue
    if record:
        cmake_lines.append(line)

# Parse
pattern = re.compile(r"CMAKE_([A-Z_]*)\s+\"(.*)\"")
for line in cmake_lines:
    # Check for a new variable=value pair
    # We consider only monoline entries
    match = pattern.match(line)
    if match is None:
        continue
    key = match.group(1)
    value = match.group(2)
    cmake_info[key] = value

# Filter on relevant entries
KEYS = {
    "SYSTEM",
    "SYSTEM_NAME",
    "CXX_COMPILER",
    "CXX_COMPILER_ID",
    "CXX_COMPILER_ARCHITECTURE_ID",
    "CXX_COMPILER_VERSION",
    "C_COMPILER",
    "C_COMPILER_ID",
    "C_COMPILER_ARCHITECTURE_ID",
    "C_COMPILER_VERSION",
}
cmake_info = {key: cmake_info[key] for key in KEYS}

# Add time
cmake_info["TIMESTAMP"] = str(datetime.now())

# Export the dictionary in JSON format
print(json.dumps(cmake_info, sort_keys=True, indent=4))
