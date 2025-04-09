from datetime import datetime
from pathlib import Path

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content" / "posts"

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("post.md.j2")


def load_repos():
    with open(BASE_DIR / "data" / "repos.yaml") as f:
        return yaml.safe_load(f)


def fetch_repo_data(repo_url):
    owner, name = repo_url.rstrip("/").split("/")[-2:]
    api_url = f"https://api.github.com/repos/{owner}/{name}"
    contrib_url = f"{api_url}/contributors"

    repo_resp = requests.get(api_url)
    contrib_resp = requests.get(contrib_url)

    repo_data = repo_resp.json()
    contributors = len(contrib_resp.json())

    return repo_data, contributors


def render_post(repo_data, contributors):
    now = datetime.utcnow().isoformat()
    return template.render(repo=repo_data, contributors=contributors, now=now)


def write_post(slug, content):
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONTENT_DIR / f"{slug}.md", "w") as f:
        f.write(content)


def main():
    repos = load_repos()
    for entry in repos:
        url = entry["url"]
        repo_data, contributors = fetch_repo_data(url)
        slug = repo_data["name"]
        post_content = render_post(repo_data, contributors)
        write_post(slug, post_content)


if __name__ == "__main__":
    main()
