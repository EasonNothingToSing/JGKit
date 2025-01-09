import re
from collections import defaultdict


def parse_string(input_string):
    # Regular expression to match the string pattern
    pattern = r"^(\w+)\s+(\w)\s+([\w.]+)$|^(\w+)\s+(\w)\s+([\w.]+)\s+(.+):(\d+)$"

    # Match the string with the regex pattern
    match = re.match(pattern, input_string)

    if match:
        # Extract groups into corresponding fields
        address = match.group(1)
        if address:
            attribute = match.group(2)
            name = match.group(3)
            path = None
            line = None
        else:
            address = match.group(4)
            attribute = match.group(5)
            name = match.group(6)
            path = match.group(7)
            line = match.group(8)

        return {
            "address": address,
            "attribute": attribute,
            "name": name,
            "path": path,
            "line": line
        }
    else:
        return None


def analyze_symbol_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    directory_sizes = defaultdict(int)

    for i in range(len(lines) - 1):
        current_line = lines[i].strip()
        next_line = lines[i + 1].strip()

        current_parsed = parse_string(current_line)
        next_parsed = parse_string(next_line)

        if current_parsed and next_parsed:
            if current_parsed['attribute'] == 'A':
                continue

            current_address = int(current_parsed['address'], 16)
            next_address = int(next_parsed['address'], 16)

            diff = next_address - current_address

            f_path = current_parsed['path']
            if f_path:
                directory = f_path.rsplit('/', 1)[1]  # Extract directory path
                directory_sizes[directory] += diff

            print(f"Name: {current_parsed['name']}, Address Difference: {diff}, In file: {current_parsed['path']}")
        elif current_parsed:
            print(f"Skipping unmatched line: {current_line}")
        elif next_parsed:
            print(f"Skipping unmatched line: {next_line}")

    print("\nDirectory-wise Size Summary:")
    for directory, size in directory_sizes.items():
        print(f"Directory: {directory}, Total Size: {size}")


# Example usage
# Replace 'xxx.symbol' with the path to your symbol file
symbol_file_path = 'fhost.symbol'
analyze_symbol_file(symbol_file_path)
