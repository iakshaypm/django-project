import os
import subprocess

# Map file extensions to linter commands
linters = {
    '.py': 'flake8',
    '.php': 'phpcs',
    '.js': 'eslint',
    '.css': 'stylelint',
    '.rb': 'rubocop'
}


def run_linter(file):
    ext = os.path.splitext(file)[1]
    linter_command = linters.get(ext)

    if linter_command:
        try:
            subprocess.run([linter_command, file], check=True)
            print(f"Linting {file} successful!")
        except subprocess.CalledProcessError as e:
            print(f"Linting {file} failed: {e}")
    else:
        print(f"No linter configured for {ext}")


# Walk through files in the current directory and lint them
for root, dirs, files in os.walk('.'):
    for file in files:
        run_linter(os.path.join(root, file))