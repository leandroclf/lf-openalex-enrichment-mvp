import os
import sys
import importlib.util

def run_smoke_check():
    # Determine the project root dynamically, assuming 'tools' is directly under it
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, ".."))
    
    # Add project root to sys.path to enable local imports
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print(f"Running transversal smoke check in {project_root}")
    failures = []
    
    # Files/directories to exclude from direct import attempts (already handled by other checks or not meant for direct import)
    # Add common test file patterns to avoid test execution as part of smoke check
    # Also exclude the smoke_check.py itself
    excluded_paths = ["tests", "migrations"] # Example exclusions, can be expanded
    excluded_files = ["smoke_check.py", "__main__.py"]

    for root, dirs, files in os.walk(project_root):
        # Exclude specified directories from walking
        dirs[:] = [d for d in dirs if d not in excluded_paths]

        for file in files:
            if file.endswith(".py") and file not in excluded_files:
                filepath = os.path.join(root, file)
                
                # Construct a module name for potential import (primarily for error messages)
                relative_path = os.path.relpath(filepath, project_root)
                module_name = relative_path.replace(os.sep, ".")[:-3]

                # Skip files that are part of excluded directories or patterns
                if any(excluded_dir in relative_path for excluded_dir in excluded_paths):
                    continue

                try:
                    # 1. Basic syntax check by compiling
                    with open(filepath, "r", encoding="utf-8") as f:
                        compile(f.read(), filepath, 'exec')

                    # 2. Attempt to import (without executing __main__ or actual test runners)
                    # This helps catch ImportError due to unresolved dependencies or incorrect paths.
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                except SyntaxError as e:
                    failures.append(f"Syntax error in {filepath}: {e}")
                except ImportError as e:
                    failures.append(f"Import error in {filepath}: {e}")
                except Exception as e:
                    # Catch other potential errors during module loading/execution (e.g., NameError from undeclared vars)
                    failures.append(f"Runtime error during module load {filepath}: {e}")

    if failures:
        print("\nTransversal smoke check FAILED:")
        for f in failures:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("\nTransversal smoke check PASSED: All Python files are syntactically valid and imports resolve.")

if __name__ == "__main__":
    run_smoke_check()
