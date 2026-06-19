# Showmax Global — Production Deploy Runbook (SHO-2)

Status: the site is **deploy-ready and verified**; production deploy is **blocked on one
human/board-provided input** (a hosting credential + the domain DNS decision). Once provided,
deploy is a single command and HTTPS is automatic.

## What is ready (done)
- `site/` — verbatim static export: `index.html`, `trade-facilitation.html`, `privacy.html`,
  `sitemap.xml`, `robots.txt`, `og-image.jpg`.
- All 6 assets serve HTTP 200 locally; homepage renders premium; pages are responsive
  (`<meta name="viewport">` + media queries present in index/trade).
- `netlify.toml` (publish=`site`) and `site/_headers` (security headers) committed so
  Cloudflare Pages / Netlify can ship the files verbatim.

## The two unblock inputs needed (human/board — agents cannot create accounts or enter passwords)
1. **Domain.** `showmaxglobal.com` is already REGISTERED, and the site hardcodes
   `https://www.showmaxglobal.com`.
   - If Showmax Global already owns it → provide DNS access (or add the host's CNAME records).
   - If NOT owned → approve an available alternative (`showmaxglobal.co`, `.io`, or `.global`)
     and register it via the company GoDaddy account.
2. **Hosting credential.** Need exactly ONE of:
   - **Cloudflare** (recommended): a human creates the free account once, then provides a scoped
     **API token** (permission: Account → Cloudflare Pages → Edit) + the **Account ID**.
   - **Netlify**: a Personal Access Token.
   - **GitHub**: an empty repo + token; I push `site/` and enable GitHub Pages.

## Deploy command once a Cloudflare token is provided (recommended)
```bash
# env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID
npx --yes wrangler@latest pages project create showmax-global --production-branch main
npx --yes wrangler@latest pages deploy site --project-name=showmax-global
# then bind custom domain in Pages; Cloudflare issues HTTPS automatically
```

Recommended host: **Cloudflare Pages** — free tier, automatic HTTPS, easy custom domain,
token-based (no interactive browser login required from the agent).
