# Jira configuration setup (one-time)

`fetch_ticket.py` needs three values — your Jira Cloud site URL, your email, and
an API token. Nothing org-specific or secret is stored in the skill. All three
are resolved in this order:

1. **Environment variables** `JIRA_BASE_URL` / `JIRA_EMAIL` / `JIRA_API_TOKEN`
2. **Home-level file** `~/.config/jira/.env` (recommended — set once, works from
   every repo)
3. **Local `.env`** found by walking up from the current directory (so a repo
   that already has these in its `.env` keeps working unchanged)

All three are **required**; a missing one exits with code `2` and lists what's
missing.

## Recommended: home-level config

Generate an API token at
<https://id.atlassian.com/manage-profile/security/api-tokens>, then:

```bash
mkdir -p ~/.config/jira
cat > ~/.config/jira/.env <<'EOF'
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=paste-your-token-here
EOF
chmod 600 ~/.config/jira/.env
```

`chmod 600` keeps the token readable only by you. Tokens may contain `=`
characters — the parser keeps everything after the first `=`, so paste the whole
token verbatim. A trailing slash on `JIRA_BASE_URL` is fine (it's stripped).

## Alternative: environment variables

Export them from your shell profile (`~/.bashrc`, `~/.zshrc`):

```bash
export JIRA_BASE_URL="https://your-org.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="your-token"
```

## Jira Cloud vs on-prem

`JIRA_BASE_URL` must be a **Jira Cloud** site (`*.atlassian.net`). This skill
uses Cloud-only APIs (REST v3, ADF, `nextPageToken` search, email+token auth)
and will not work against on-prem Data Center/Server.

## Verifying

```bash
python3 scripts/fetch_ticket.py PROJ-1234
```

Missing/invalid config exits with code `2` (message points back here). A
missing/inaccessible ticket exits with code `1`.
