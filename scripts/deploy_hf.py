"""One-click deploy script for Hugging Face Spaces.
Usage: python scripts/deploy_hf.py <HF_TOKEN>
"""
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, whoami

def main():
    if len(sys.argv) < 2:
        print("Error: Missing token. Usage: python scripts/deploy_hf.py hf_...")
        sys.exit(1)

    token = sys.argv[1].strip()
    api = HfApi(token=token)

    try:
        user_info = whoami(token=token)
        username = user_info["name"]
        print(f"Logged in as Hugging Face user: {username}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    repo_id = f"{username}/WellSense"
    print(f"Creating Space: {repo_id}...")
    try:
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            private=False,
            token=token,
            exist_ok=True,
        )
        print("Space initialized successfully.")
    except Exception as e:
        print(f"Space initialization note: {type(e).__name__}")

    ROOT = Path(__file__).resolve().parents[1]
    print(f"Uploading files from {ROOT} to Space {repo_id}...")
    
    # Files to exclude from upload (sensitive data, temp folders, venv)
    ignore_patterns = [
        ".venv/**",
        "data/raw/**",
        "data/processed/*.db",
        "*.db",
        ".env",
        ".cache/**",
        "__pycache__/**",
        ".git/**",
        "tools/**",
    ]

    api.upload_folder(
        folder_path=str(ROOT),
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=ignore_patterns,
        commit_message="Deploy WellSense Streamlit app",
        token=token,
    )

    url = f"https://huggingface.co/spaces/{repo_id}"
    print(f"\n=======================================================")
    print(f"  SUCCESS! Your app is building and live at:")
    print(f"  >>> {url} <<<")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
