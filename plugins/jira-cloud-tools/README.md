# jira-cloud-tools

Tools for working with **Jira Cloud** (REST API v3 / ADF). Part of the
[staten-extensions](../../README.md) marketplace.

> **Jira Cloud only.** This plugin uses Cloud-specific APIs (REST v3, ADF,
> `nextPageToken` search, email + API-token auth). It does **not** work against
> on-prem Jira Data Center/Server (which uses REST v2, wiki markup, and PATs).

## Skills

- **analyze-jira-ticket** — fetch a single ticket plus its context (linked
  issues, subtasks, comments, attachment list, and a child-issue rollup for
  Epic/Feature/Initiative cards) and produce a type-aware analysis:
  - **Epic/Feature/Initiative** → initiative summary + child rollup, scope.
  - **Story** → MVP-alignment / scope-creep check, proposed Gherkin AC, INVEST.
  - **Bug** → repro clarity, expected-vs-actual, impact, root-cause when the
    code is available.

  Read-only — it never writes to Jira.

## Install

```
/plugin marketplace add Erchamion/claude-extensions   # once per machine
/plugin install jira-cloud-tools@staten-extensions
```

Then in a session: "analyze PROJ-1234", "what's ABC-987 about?", or drop a bare
issue key.

## Prerequisites

**Python 3** on PATH — the fetch script is stdlib-only and runs on
Windows/macOS/Linux. On Windows, invoke with `python` or `py -3` if `python3`
isn't available.

## Configuration

No site URL, email, or token is stored in this repo. The fetch script reads
three values — in order — from environment variables, then `~/.config/jira/.env`,
then a `.env` found by walking up from the current directory:

| Variable | Example |
|----------|---------|
| `JIRA_BASE_URL` | `https://your-org.atlassian.net` |
| `JIRA_EMAIL` | `you@example.com` |
| `JIRA_API_TOKEN` | (Atlassian API token) |

All three are required; a missing one exits with code `2` and names what's
missing. Recommended one-time setup (works from every repo):

```bash
mkdir -p ~/.config/jira
cat > ~/.config/jira/.env <<'EOF'
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=paste-your-token-here
EOF
chmod 600 ~/.config/jira/.env
```

Generate a token at
<https://id.atlassian.com/manage-profile/security/api-tokens>. Full details:
[`skills/analyze-jira-ticket/reference/credentials-setup.md`](skills/analyze-jira-ticket/reference/credentials-setup.md).

## License

[MIT](../../LICENSE) © 2026 Jon Staten
