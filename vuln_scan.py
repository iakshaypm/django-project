#!/usr/bin/env python3
import subprocess
import sys
import time
import os

def run_tool(tool_name, cmd):
    """
    Runs a given tool command and measures the elapsed time.
    Prints the output and any errors, then returns the elapsed time.
    """
    print(f"Running {tool_name} ...")
    start = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {tool_name}:")
        print(e.stderr)
        return 0.0
    end = time.perf_counter()
    elapsed = end - start
    print(f"{tool_name} completed in {elapsed:.2f} seconds.\n")
    print(result.stdout)
    if result.stderr:
        print("Errors/Warnings:")
        print(result.stderr)
    print("=" * 60 + "\n")
    return elapsed

def main():
    if len(sys.argv) != 2:
        print("Usage: python vuln_scan.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    total_time = 0.0

    # Run Bandit on the target file/directory
    bandit_cmd = ["bandit", "-r", target]
    total_time += run_tool("Bandit", bandit_cmd)

    # Run Semgrep on the target file/directory
    semgrep_cmd = ["semgrep", "--config", "auto", target]
    total_time += run_tool("Semgrep", semgrep_cmd)

    # For Bearer, run using Docker
    # Here, we mount a local folder (./utils/bearer_files) to the container's /tmp/scan directory.
    # Adjust the folder path as needed to point to your scan files.
    current_directory = os.getcwd()
    bearer_cmd = [
        'docker', 'run', '--rm',
        '-v', f'{current_directory}/utils/bearer_files:/tmp/scan',  # Mount the local folder to /tmp/scan in the container
        'bearer/bearer:latest-amd64', 'scan', '/tmp/scan', '--format', 'json'
    ]
    total_time += run_tool("Bearer", bearer_cmd)

    print(f"Total scanning time: {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()

