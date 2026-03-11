import os
import sys


EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".tmp",
    ".venv",
    "__pycache__",
    "migrations",
    "tests",
}
EXCLUDED_FILES = {"__main__.py"}


def run_smoke_check():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, ".."))

    print(f"Running transversal smoke check in {project_root}")
    failures = []

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [directory for directory in dirs if directory not in EXCLUDED_DIRS]

        for filename in files:
            if not filename.endswith(".py") or filename in EXCLUDED_FILES:
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as handle:
                    compile(handle.read(), filepath, "exec")
            except SyntaxError as exc:
                failures.append(f"Syntax error in {filepath}: {exc}")

    if failures:
        print("\nTransversal smoke check FAILED:")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)

    print("\nTransversal smoke check PASSED: all Python files compile.")


if __name__ == "__main__":
    run_smoke_check()
