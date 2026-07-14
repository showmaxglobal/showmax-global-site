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

---

## UPDATE (2026-07-07) — confirmed live host is **Netlify**

Live probe of `https://showmaxglobal.com/` returns `server: Netlify` (HTTP 200). The site is
already published on Netlify, so **new content deploys through the existing Netlify site** — do
NOT create a new host. `/blog/` and the 4 article URLs currently return **404** (not yet shipped).

### SHO-106 status: approved, blocked only on a Netlify credential
- **Board approval gate #3 (live-site modification): GRANTED** (approval_approved, 2026-07-06).
  The policy blocker is cleared.
- **Remaining blocker (technical):** no agent holds a Netlify auth token, there is no git remote
  wired to this repo, and no `netlify` CLI is installed locally. Agents cannot log in or hold the
  credential.

### Single unblock action for the owner (pick ONE)
1. **Provide a token** (preferred, lets an agent finish): supply a **Netlify Personal Access
   Token** (`NETLIFY_AUTH_TOKEN`) + the **Site ID** for showmaxglobal.com. Then deploy is:
   ```bash
   # env: NETLIFY_AUTH_TOKEN, NETLIFY_SITE_ID
   npx --yes netlify-cli@latest deploy --prod --dir=site --site "$NETLIFY_SITE_ID"
   ```
2. **Owner self-deploys** the built `site/` directory from branch `sho-106-blog` (commit `0b40d47`):
   run the command above after `netlify login`, OR drag the `site/` folder onto the Netlify site's
   Deploys page.
3. **Wire git deploy:** connect the Netlify site to this repo and merge `sho-106-blog` → `main`
   (Netlify auto-builds `publish = site`).

### Post-deploy verification (any path)
`/blog/`, the 4 `/blog/<slug>/` URLs, and `/sitemap.xml` (must now contain the 4 blog `<loc>`s)
should all return 200; then submit `sitemap.xml` to Google Search Console + Bing (DoD 5) and post
the 4 live URLs to SHO-106 (DoD 6).
