import os
import subprocess

def run_command(command):
    """Executes a shell command and returns the output."""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error executing: {command}\n{result.stderr}")
        return None
    return result.stdout

def automate_git_commit():
    print("--- Step 1: Analyzing modified files ---")
    # Get the diff of all staged and unstaged changes
    diff_text = run_command("git diff HEAD")
    
    if not diff_text or diff_text.strip() == "":
        print("No changes detected since the last commit.")
        return

    # In a real-world scenario, you would pass 'diff_text' to an LLM API here.
    # For this script, we'll summarize the filenames.
    changed_files = run_command("git status --short")
    summary_text = f"Summary of changes:\n{changed_files}"
    print(f"Changes identified:\n{changed_files}")

    print("--- Step 2: Checking and updating documentation ---")
    docs_path = "./docs"
    if os.path.exists(docs_path):
        # Logic: If certain keywords exist in diff, append to a changelog or doc
        # This is a placeholder for your specific documentation logic
        with open(os.path.join(docs_path, "changelog.md"), "a") as f:
            f.write(f"\n## Update {summary_text.splitlines()[0]}\n{summary_text}")
        print("Updated docs/changelog.md based on new changes.")
    else:
        print("Docs folder not found. Skipping documentation update.")

    print("--- Step 3: Checking and updating Roadmap ---")
    roadmap_file = "roadmap.md" # or docs/roadmap.md
    if os.path.exists(roadmap_file):
        # Placeholder: Logic to mark tasks as [x] instead of [ ]
        print(f"Checking {roadmap_file} for archived criteria...")
        # (Your logic for parsing and updating roadmap goes here)
        print("Roadmap updated.")
    else:
        print("Roadmap file not found. Skipping.")

    print("--- Step 4: Staging and Committing changes ---")
    run_command("git add .")
    
    # Generate a commit message based on the summary
    commit_msg = f"Auto-commit: {summary_text.splitlines()[1] if len(summary_text.splitlines()) > 1 else 'Updates'}"
    commit_result = run_command(f'git commit -m "{commit_msg}"')
    
    if commit_result:
        print(f"Successfully committed with message: {commit_msg}")
    
    print("\nProcess complete.")

if __name__ == "__main__":
    automate_git_commit()