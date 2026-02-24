"""
generate_readme.py
------------------
Scans the DSA repository and auto-generates README.md with:
  - Per-topic problem counts
  - A full problem list per topic
  - A total problem count badge

Run locally:   python generate_readme.py
Auto-runs via: .github/workflows/update_readme.yml on every push
"""

import os
import re
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent          # repo root
README_PATH = ROOT_DIR / "README.md"

# File extensions considered as "solutions"
SOLUTION_EXTS = {".cpp", ".c", ".py", ".java", ".js", ".ts", ".go", ".rs", ".kt"}

# Folders / files to skip entirely
SKIP_DIRS = {".git", ".github", "__pycache__", "node_modules", ".venv", "venv"}
SKIP_FILES = {"generate_readme.py", "README.md", ".gitignore", "LICENSE"}

# Difficulty keywords detected from filenames/folder names (case-insensitive)
DIFFICULTY_KEYWORDS = {
    "easy":   ["easy"],
    "medium": ["medium"],
    "hard":   ["hard"],
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def prettify(name: str) -> str:
    """Convert snake_case / CamelCase / hyphen-case to 'Pretty Name'."""
    name = re.sub(r"[_\-]+", " ", name)                  # underscores/hyphens → space
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)     # camelCase → camel Case
    return name.strip().title()


def detect_difficulty(path: str) -> str:
    lower = path.lower()
    for level, keywords in DIFFICULTY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return level.capitalize()
    return "—"


def collect_topics(root: Path) -> dict:
    """
    Returns a dict:
      { topic_name: [ { "name": str, "path": str, "difficulty": str } ] }
    Topics are immediate subdirectories of root.
    Nested sub-folders count toward the parent topic.
    """
    topics = {}

    for entry in sorted(root.iterdir()):
        if entry.name in SKIP_DIRS or entry.name.startswith("."):
            continue
        if not entry.is_dir():
            continue

        topic = prettify(entry.name)
        problems = []

        # Walk everything inside this topic folder
        for dirpath, dirnames, filenames in os.walk(entry):
            # Prune unwanted subdirs in-place
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]

            for fname in sorted(filenames):
                ext = Path(fname).suffix.lower()
                if ext not in SOLUTION_EXTS or fname in SKIP_FILES:
                    continue

                rel_path = Path(dirpath).relative_to(root) / fname
                display  = prettify(Path(fname).stem)
                diff     = detect_difficulty(str(rel_path))

                problems.append({
                    "name":       display,
                    "path":       rel_path.as_posix(),
                    "difficulty": diff,
                })

        if problems:               # only list topics that have at least 1 solution
            topics[topic] = problems

    return topics


def make_progress_bar(count: int, max_val: int = 100, width: int = 20) -> str:
    if max_val == 0:
        return "░" * width
    filled = round(width * min(count, max_val) / max_val)
    return "█" * filled + "░" * (width - filled)


# ── README builder ─────────────────────────────────────────────────────────────

def build_readme(topics: dict) -> str:
    total = sum(len(v) for v in topics.values())
    now   = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        "<!-- AUTO-GENERATED — do not edit by hand. Run generate_readme.py to refresh. -->",
        "",
        '<div align="center">',
        "",
        "# 🧠 DSA Practice Repository",
        "",
        "> A structured collection of Data Structures & Algorithms solutions.",
        "",
        f'![Total Problems](https://img.shields.io/badge/Total%20Problems-{total}-blueviolet?style=for-the-badge)',
        f'![Topics](https://img.shields.io/badge/Topics-{len(topics)}-teal?style=for-the-badge)',
        f'![Language](https://img.shields.io/badge/Primary%20Language-C%2B%2B-00599C?style=for-the-badge&logo=cplusplus)',
        f'![Last Updated](https://img.shields.io/badge/Last%20Updated-{now.replace(" ", "%20").replace(":", "%3A")}-informational?style=for-the-badge)',
        "",
        "</div>",
        "",
        "---",
        "",
    ]

    # ── About ─────────────────────────────────────────────────────────────────
    lines += [
        "## 📖 About",
        "",
        "This repository is my personal log of DSA problem-solving practice.",
        "Every file is a self-contained solution. The README is **automatically regenerated**",
        "whenever a new solution is pushed, so the statistics are always up-to-date.",
        "",
        "---",
        "",
    ]

    # ── Progress overview ─────────────────────────────────────────────────────
    lines += [
        "## 📊 Progress Overview",
        "",
        f"**Total problems solved: `{total}`**",
        "",
        "| # | Topic | Solved | Progress |",
        "|---|-------|:------:|----------|",
    ]
    for i, (topic, problems) in enumerate(topics.items(), 1):
        bar = make_progress_bar(len(problems))
        lines.append(f"| {i} | [{topic}](#{topic.lower().replace(' ', '-')}) | `{len(problems)}` | `{bar}` |")

    lines += ["", "---", ""]

    # ── Per-topic tables ───────────────────────────────────────────────────────
    lines += ["## 📂 Topics", ""]
    for topic, problems in topics.items():
        anchor = topic.lower().replace(" ", "-")
        lines += [
            f"### {topic}",
            "",
            f"**{len(problems)} problem{'s' if len(problems) != 1 else ''} solved**",
            "",
            "| # | Problem | Difficulty | Solution |",
            "|---|---------|:----------:|:--------:|",
        ]
        for j, prob in enumerate(problems, 1):
            diff_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(prob["difficulty"], "⚪")
            link = f"[View]({prob['path']})"
            lines.append(
                f"| {j} | {prob['name']} | {diff_emoji} {prob['difficulty']} | {link} |"
            )
        lines += ["", "---", ""]

    # ── How to contribute / add problems ─────────────────────────────────────
    lines += [
        "## 🚀 How It Works",
        "",
        "1. **Add a solution** – drop a `.cpp` / `.py` / `.java` (etc.) file inside the",
        "   relevant topic folder (e.g. `Arrays/Two_Sum.cpp`).",
        "2. **Create a new topic** – just create a new folder at the repo root",
        "   (e.g. `Graphs/`) and add solutions inside it.",
        "3. **Push to GitHub** – the GitHub Actions workflow (`.github/workflows/update_readme.yml`)",
        "   automatically runs `generate_readme.py` and commits the updated README.",
        "",
        "> **Tip:** difficulty is auto-detected if your filename/path contains `easy`, `medium`, or `hard`.",
        "",
        "---",
        "",
    ]

    # ── Footer ────────────────────────────────────────────────────────────────
    lines += [
        '<div align="center">',
        "",
        f"*Last auto-generated: {now}*",
        "",
        "</div>",
        "",
    ]

    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    topics  = collect_topics(ROOT_DIR)
    content = build_readme(topics)
    README_PATH.write_text(content, encoding="utf-8")
    total   = sum(len(v) for v in topics.items())
    print(f"✅  README.md updated — {len(topics)} topic(s), {sum(len(v) for v in topics.values())} problem(s) total.")
