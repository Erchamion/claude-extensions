#!/usr/bin/env python3
"""
Fetch a single Jira ticket (plus its context) and emit structured markdown.

Read-only. Given an issue key it fetches the issue, its linked issues,
subtasks, comments, and — when the issue is an Epic — its child issues, then
prints a structured markdown block to stdout for an agent to analyze.

Usage:
    python3 fetch_ticket.py PROJ-1234

Configuration (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN) is resolved in this
order; nothing org-specific or secret lives in this skill:
    1. Environment variables
    2. Home-level file ~/.config/jira/.env   (recommended; chmod 600)
    3. A .env file found by walking up from the current directory

JIRA_BASE_URL is your Jira Cloud site, e.g. https://your-org.atlassian.net.

See reference/credentials-setup.md for one-time setup. Generate a token at:
    https://id.atlassian.com/manage-profile/security/api-tokens
"""

import json
import os
import sys
from base64 import b64encode
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# Set from configuration at startup (see load_config). No org default is baked
# in so this skill carries zero site identity.
JIRA_BASE_URL = ""

# Issue types that contain child stories — these get a child-issue rollup.
# Covers the standard Epic plus this org's Feature/Initiative hierarchy levels.
PARENT_LEVEL_TYPES = {"epic", "feature", "initiative"}

ISSUE_FIELDS = (
    "summary,description,status,issuetype,priority,assignee,"
    "labels,components,created,updated,comment,attachment,"
    "customfield_10016,customfield_10014,parent,subtasks,issuelinks"
)


# --------------------------------------------------------------------------
# Credentials
# --------------------------------------------------------------------------

def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE pairs from an env file without clobbering existing vars."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


REQUIRED_KEYS = ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")


def load_config() -> tuple[str, str, str]:
    """Resolve JIRA_BASE_URL / JIRA_EMAIL / JIRA_API_TOKEN. Order: env vars,
    then ~/.config/jira/.env, then a walked-up .env. See module docstring."""
    # 1. Environment variables already win (we never overwrite them below).
    # 2. Home-level XDG config file.
    home_env = Path.home() / ".config" / "jira" / ".env"
    if home_env.exists():
        _load_env_file(home_env)

    # 3. Walk up from cwd looking for a local .env (keeps repo workflows working).
    if not all(os.environ.get(k) for k in REQUIRED_KEYS):
        for directory in [Path.cwd(), *Path.cwd().parents]:
            local_env = directory / ".env"
            if local_env.exists():
                _load_env_file(local_env)
                break

    missing = [k for k in REQUIRED_KEYS if not os.environ.get(k)]
    if missing:
        _config_error(missing)
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
    return base_url, os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"]


def _config_error(missing: list[str]) -> None:
    msg = (
        f"Error: missing required config: {', '.join(missing)}.\n\n"
        "Set it once at the home-level config file:\n"
        "  mkdir -p ~/.config/jira\n"
        "  cat > ~/.config/jira/.env <<'EOF'\n"
        "  JIRA_BASE_URL=https://your-org.atlassian.net\n"
        "  JIRA_EMAIL=you@example.com\n"
        "  JIRA_API_TOKEN=your-token\n"
        "  EOF\n"
        "  chmod 600 ~/.config/jira/.env\n\n"
        "Or export them as environment variables, or run from a repo with a .env.\n"
        "Generate a token at: https://id.atlassian.com/manage-profile/security/api-tokens\n"
        "See the skill's reference/credentials-setup.md for details."
    )
    print(msg, file=sys.stderr)
    sys.exit(2)


def get_auth_header(email: str, api_token: str) -> str:
    encoded = b64encode(f"{email}:{api_token}".encode()).decode()
    return f"Basic {encoded}"


# --------------------------------------------------------------------------
# Jira requests
# --------------------------------------------------------------------------

def jira_get(url: str, auth_header: str) -> dict:
    req = Request(url)
    req.add_header("Authorization", auth_header)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if body:
            print(f"  Body: {body[:500]}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def jql_search(jql: str, auth_header: str, fields: list[str] | None = None) -> list:
    """Run a JQL search and return matching issues.

    Uses the /search/jql endpoint, which paginates via nextPageToken (it
    rejects startAt with HTTP 400 "Invalid request payload").
    """
    all_issues: list = []
    next_page_token = None
    while True:
        body: dict = {
            "jql": jql,
            "maxResults": 50,
            "fields": fields if fields is not None else ISSUE_FIELDS.split(","),
        }
        if next_page_token:
            body["nextPageToken"] = next_page_token
        req = Request(
            f"{JIRA_BASE_URL}/rest/api/3/search/jql",
            data=json.dumps(body).encode(),
            method="POST",
        )
        req.add_header("Authorization", auth_header)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        try:
            with urlopen(req) as response:
                data = json.loads(response.read().decode())
        except HTTPError as e:
            err_body = e.read().decode() if e.fp else ""
            print(f"JQL search error {e.code}: {err_body[:300]}", file=sys.stderr)
            break
        all_issues.extend(data.get("issues", []))
        next_page_token = data.get("nextPageToken")
        if data.get("isLast", True) or not next_page_token:
            break
    return all_issues


def fetch_issue_by_key(issue_key: str, auth_header: str) -> dict | None:
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}?fields={ISSUE_FIELDS}"
    req = Request(url)
    req.add_header("Authorization", auth_header)
    req.add_header("Accept", "application/json")
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode())
    except (HTTPError, URLError) as e:
        reason = getattr(e, "reason", e)
        print(f"  Warning: could not fetch {issue_key}: {reason}", file=sys.stderr)
        return None


# --------------------------------------------------------------------------
# ADF -> text
# --------------------------------------------------------------------------

def extract_text_from_adf(node) -> str:
    """Extract plain text/markdown from Atlassian Document Format."""
    if node is None:
        return ""
    if isinstance(node, list):
        return "".join(extract_text_from_adf(n) for n in node)
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""

    node_type = node.get("type", "")
    text = node.get("text", "")

    if node_type == "text":
        return text
    if node_type == "hardBreak":
        return "\n"
    if node_type == "paragraph":
        return extract_text_from_adf(node.get("content", [])) + "\n\n"
    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        return f"{'#' * level} {extract_text_from_adf(node.get('content', []))}\n\n"
    if node_type == "bulletList":
        lines = [
            f"  - {extract_text_from_adf(item.get('content', [])).strip()}"
            for item in node.get("content", [])
        ]
        return "\n".join(lines) + "\n"
    if node_type == "orderedList":
        lines = [
            f"  {i}. {extract_text_from_adf(item.get('content', [])).strip()}"
            for i, item in enumerate(node.get("content", []), 1)
        ]
        return "\n".join(lines) + "\n"
    if node_type == "listItem":
        return extract_text_from_adf(node.get("content", []))
    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        return f"```{lang}\n{extract_text_from_adf(node.get('content', []))}```\n\n"
    if node_type == "blockquote":
        content = extract_text_from_adf(node.get("content", [])).strip()
        return "\n".join(f"> {line}" for line in content.split("\n")) + "\n\n"
    if node_type == "table":
        return _adf_table(node)
    if node_type == "mention":
        return f"@{node.get('attrs', {}).get('text', 'unknown')}"
    if node_type == "inlineCard":
        return node.get("attrs", {}).get("url", "")
    if node_type in ("mediaGroup", "mediaSingle"):
        return "[media attachment]\n"
    if node_type == "emoji":
        return node.get("attrs", {}).get("text", "")
    if node_type == "rule":
        return "\n---\n\n"
    return extract_text_from_adf(node.get("content", []))


def _adf_table(node: dict) -> str:
    table_lines = []
    for row_idx, row in enumerate(node.get("content", [])):
        cells = row.get("content", [])
        cell_texts = [
            extract_text_from_adf(cell.get("content", [])).strip() for cell in cells
        ]
        table_lines.append("| " + " | ".join(cell_texts) + " |")
        if row_idx == 0:
            table_lines.append("| " + " | ".join("---" for _ in cell_texts) + " |")
    return "\n".join(table_lines) + "\n\n"


# --------------------------------------------------------------------------
# Parsing & formatting
# --------------------------------------------------------------------------

def _parse_description(raw) -> str:
    if isinstance(raw, dict):
        return extract_text_from_adf(raw).strip()
    if isinstance(raw, str):
        return raw.strip()
    return "(No description provided)"


def _parse_comments(comment_data: dict) -> list:
    comments = []
    for c in comment_data.get("comments", []):
        body = c.get("body", "")
        if isinstance(body, dict):
            body = extract_text_from_adf(body).strip()
        comments.append({
            "author": c.get("author", {}).get("displayName", "Unknown"),
            "date": c.get("created", "")[:10],
            "body": body,
        })
    return comments


def _parse_links(issuelinks: list) -> list:
    links = []
    for link in issuelinks:
        link_type = link.get("type", {})
        if "outwardIssue" in link:
            linked = link["outwardIssue"]
            direction = link_type.get("outward", "relates to")
        elif "inwardIssue" in link:
            linked = link["inwardIssue"]
            direction = link_type.get("inward", "is related to")
        else:
            continue
        links.append({
            "key": linked.get("key", ""),
            "summary": linked.get("fields", {}).get("summary", ""),
            "direction": direction,
        })
    return links


def parse_issue(issue: dict) -> dict:
    fields = issue.get("fields", {})
    parent = fields.get("parent", {})
    parent_info = None
    if parent:
        parent_info = {
            "key": parent.get("key", ""),
            "summary": parent.get("fields", {}).get("summary", ""),
        }
    assignee = fields.get("assignee")
    return {
        "key": issue.get("key", ""),
        "url": f"{JIRA_BASE_URL}/browse/{issue.get('key', '')}",
        "summary": fields.get("summary", "(No summary)"),
        "description": _parse_description(fields.get("description")),
        "issue_type": fields.get("issuetype", {}).get("name", "Unknown"),
        "priority": (fields.get("priority") or {}).get("name", "None"),
        "status": fields.get("status", {}).get("name", "Unknown"),
        "assignee": assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
        "labels": fields.get("labels", []),
        "components": [c.get("name", "") for c in fields.get("components", [])],
        "story_points": fields.get("customfield_10016"),
        "parent": parent_info,
        "subtasks": [
            {
                "key": s.get("key", ""),
                "summary": s.get("fields", {}).get("summary", ""),
                "status": s.get("fields", {}).get("status", {}).get("name", ""),
            }
            for s in fields.get("subtasks", [])
        ],
        "linked_issues": _parse_links(fields.get("issuelinks", [])),
        "comments": _parse_comments(fields.get("comment", {}) or {}),
        "created": fields.get("created", "")[:10],
        "updated": fields.get("updated", "")[:10],
        "attachments": [
            {
                "filename": a.get("filename", "(unnamed)"),
                "mime": a.get("mimeType", ""),
                "url": a.get("content", ""),
            }
            for a in fields.get("attachment", [])
        ],
    }


def fetch_linked_cards(card: dict, auth_header: str) -> list:
    """Fetch full details for issues this card links to."""
    linked_keys = sorted(
        {link["key"] for link in card.get("linked_issues", []) if link.get("key")}
    )
    cards = []
    for key in linked_keys:
        issue = fetch_issue_by_key(key, auth_header)
        if issue:
            cards.append(parse_issue(issue))
    return cards


def fetch_epic_children(epic_key: str, auth_header: str) -> list:
    """Fetch child issues of an Epic (key + summary + status only)."""
    # `parent` covers next-gen projects; "Epic Link" covers classic projects.
    jql = f'parent = "{epic_key}" OR "Epic Link" = "{epic_key}" ORDER BY rank ASC'
    children = []
    for issue in jql_search(jql, auth_header, fields=["summary", "status", "issuetype"]):
        fields = issue.get("fields", {})
        children.append({
            "key": issue.get("key", ""),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "issue_type": fields.get("issuetype", {}).get("name", ""),
        })
    return children


def render_card(card: dict) -> str:
    lines = [
        f"## [{card['key']}]({card['url']}) — {card['summary']}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **Type** | {card['issue_type']} |",
        f"| **Priority** | {card['priority']} |",
        f"| **Status** | {card['status']} |",
        f"| **Assignee** | {card['assignee']} |",
        f"| **Story Points** | {card['story_points'] or 'Not estimated'} |",
        f"| **Labels** | {', '.join(card['labels']) if card['labels'] else 'None'} |",
        f"| **Components** | {', '.join(card['components']) if card['components'] else 'None'} |",
        f"| **Created** | {card['created']} |",
        f"| **Updated** | {card['updated']} |",
        f"| **Attachments** | {len(card['attachments'])} |",
        "",
    ]
    if card["attachments"]:
        lines += ["### Attachments", ""]
        lines += [
            f"- {a['filename']}"
            + (f" (`{a['mime']}`)" if a["mime"] else "")
            + (f" — {a['url']}" if a["url"] else "")
            for a in card["attachments"]
        ]
        lines += [
            "",
            "> NOTE: Attachment contents (images, pasted tables, spreadsheets) are "
            "NOT rendered here. If the description references data that appears to "
            "live in an attachment, flag it and ask for it inline.",
            "",
        ]
    if card["parent"]:
        lines += [
            f"**Parent/Epic**: [{card['parent']['key']}]"
            f"({JIRA_BASE_URL}/browse/{card['parent']['key']}) — {card['parent']['summary']}",
            "",
        ]
    lines += ["### Description", "", card["description"] or "(No description provided)", ""]

    if card["subtasks"]:
        lines += ["### Subtasks", ""]
        lines += [
            f"- [{s['key']}]({JIRA_BASE_URL}/browse/{s['key']}) — {s['summary']} (`{s['status']}`)"
            for s in card["subtasks"]
        ]
        lines.append("")

    if card["linked_issues"]:
        lines += ["### Linked Issues", ""]
        lines += [
            f"- {link['direction']} [{link['key']}]({JIRA_BASE_URL}/browse/{link['key']}) — {link['summary']}"
            for link in card["linked_issues"]
        ]
        lines.append("")

    if card["comments"]:
        lines += ["### Comments (most recent 5)", ""]
        for comment in card["comments"][-5:]:
            lines += [f"**{comment['author']}** ({comment['date']}):", f"> {comment['body']}", ""]
    return "\n".join(lines)


def render_epic_children(children: list) -> str:
    if not children:
        return ""
    lines = ["### Child Issues (rollup)", ""]
    lines += [
        f"- [{c['key']}]({JIRA_BASE_URL}/browse/{c['key']}) — {c['summary']} "
        f"(`{c['issue_type']}` / `{c['status']}`)"
        for c in children
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python3 fetch_ticket.py <ISSUE-KEY>", file=sys.stderr)
        print("Example: python3 fetch_ticket.py PROJ-1234", file=sys.stderr)
        sys.exit(0 if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help") else 2)

    issue_key = sys.argv[1].strip()
    global JIRA_BASE_URL
    JIRA_BASE_URL, email, token = load_config()
    auth = get_auth_header(email, token)

    issue = fetch_issue_by_key(issue_key, auth)
    if issue is None:
        print(f"Error: ticket {issue_key} could not be fetched (not found or no access).", file=sys.stderr)
        sys.exit(1)

    card = parse_issue(issue)

    out = [f"# Jira Ticket: {card['key']}", ""]
    out.append(render_card(card))
    out.append("")

    if card["issue_type"].lower() in PARENT_LEVEL_TYPES:
        children = fetch_epic_children(card["key"], auth)
        epic_md = render_epic_children(children)
        if epic_md:
            out += [epic_md, ""]

    linked = fetch_linked_cards(card, auth)
    if linked:
        out += ["---", "", "# Linked Issues (context)", ""]
        for lc in linked:
            out += [render_card(lc), "", "---", ""]

    print("\n".join(out))


if __name__ == "__main__":
    main()
