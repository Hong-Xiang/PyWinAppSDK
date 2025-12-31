import pathlib
import argparse

def collect_requirements():
    parser = argparse.ArgumentParser(description="Collect requirements from obj/gen folders.")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to search in")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    requirements = set()

    # Recursively find all-requirements.txt files
    for file_path in root.rglob("all-requirements.txt"):
        # Optional: Filter to ensure it's inside an obj/gen folder if needed to avoid false positives
        if "obj" in file_path.parts and "gen" in file_path.parts:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            requirements.add(line)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    print("\n".join(sorted(requirements)))

if __name__ == "__main__":
    collect_requirements()
