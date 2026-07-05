"""Guard test: platform-versions.md must not lag the newest ESPHome release reference.

aurora/references/platform-versions.md is the canonical "what is current"
file the orchestrator reads for routing hints. esphome/references/ gains a
release-YYYY-M.md file for every tracked ESPHome release. If a release file
lands without a matching section in platform-versions.md, the orchestrator
routes on stale version data (this happened at v1.15.0: release-2026-6.md
shipped while platform-versions.md still called 2026.4.5 current).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLATFORM_VERSIONS = REPO_ROOT / "aurora" / "references" / "platform-versions.md"
ESPHOME_REFERENCES = REPO_ROOT / "esphome" / "references"


def test_platform_versions_covers_newest_esphome_release():
    """The newest ESPHome H2 section must be >= the newest release-*.md file."""
    text = PLATFORM_VERSIONS.read_text(encoding="utf-8")
    doc_versions = [
        (int(y), int(m))
        for y, m in re.findall(r"^## ESPHome (\d{4})\.(\d{1,2})", text, re.M)
    ]
    assert doc_versions, "platform-versions.md has no '## ESPHome YYYY.M' sections"

    file_versions = []
    for path in ESPHOME_REFERENCES.glob("release-*.md"):
        match = re.match(r"release-(\d{4})-(\d{1,2})\.md$", path.name)
        if match:
            file_versions.append((int(match.group(1)), int(match.group(2))))
    assert file_versions, "esphome/references/ has no release-YYYY-M.md files"

    assert max(doc_versions) >= max(file_versions), (
        f"platform-versions.md newest ESPHome section is "
        f"{max(doc_versions)[0]}.{max(doc_versions)[1]} but esphome/references/ "
        f"ships release-{max(file_versions)[0]}-{max(file_versions)[1]}.md; "
        "add a matching section to platform-versions.md"
    )
