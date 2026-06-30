# staten-extensions

Personal [Claude Code](https://claude.com/claude-code) extensions, packaged as a
plugin marketplace so they install on any machine.

## Layout

```
.claude-plugin/marketplace.json     # marketplace: lists every plugin below
plugins/
  jira-cloud-tools/                 # a plugin
    .claude-plugin/plugin.json
    skills/analyze-jira-ticket/     # SKILL.md + scripts/ + reference/
```

One repo = one marketplace = many plugins. Each plugin can bundle skills,
agents, commands, and hooks. Add new plugins under `plugins/`.

## Install (on any machine)

```
/plugin marketplace add staten/claude-extensions   # replace with your remote (owner/repo or URL)
/plugin install jira-cloud-tools@staten-extensions
```

To update after pushing changes:

```
/plugin marketplace update staten-extensions
```

## Plugins

### jira-cloud-tools

Tools for **Jira Cloud** (REST API v3 / ADF — not on-prem Data Center/Server).

- **analyze-jira-ticket** — fetch a single ticket plus its context and produce a
  type-aware analysis (Epic/Feature, Story, Bug). Read-only.

**Requires Python 3** on PATH (the fetch script is stdlib-only and runs on
Windows/macOS/Linux). On Windows, invoke with `python` or `py -3` if `python3`
isn't available.

**Configuration** is never stored in this repo — no site URL, email, or token.
The fetch script reads `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` in order
from: env vars, then `~/.config/jira/.env`, then a walked-up `.env`. All three
are required. See
`plugins/jira-cloud-tools/skills/analyze-jira-ticket/reference/credentials-setup.md`.

`JIRA_BASE_URL` is your Jira Cloud site (`https://your-org.atlassian.net`).

## License

[MIT](LICENSE) © 2026 Jon Staten
