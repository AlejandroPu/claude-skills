# The traps

Short on purpose. Every item here failed **silently**, or would have. Nothing that a competent
developer works out unaided belongs on this list.

## 1. `.well-known` must be exempt from every redirect

Any `RewriteRule` at the document root that redirects broadly — host canonicalisation, forcing HTTPS,
sending `/` somewhere — **must carry an exemption for `/.well-known/`**:

```apache
RewriteCond %{REQUEST_URI} !^/\.well-known/
```

🔴 **Redirect it and nothing breaks today. It breaks in weeks, and the symptom is the entire domain
behind a TLS warning.** That path is how the certificate authority proves domain ownership when the
**SSL certificate renews**. cPanel's own generated rules carry this exemption; a hand-written rule
placed above them loses it.

**Verify, don't assume:** `/.well-known/anything` must answer **404, not 301**, on every host the
domain answers on.

## 2. Canonicalise the host by matching the bare host, not by negating `www`

```apache
RewriteCond %{HTTP_HOST} ^example\.com$ [NC]
RewriteRule ^ https://www.example.com%{REQUEST_URI} [R=301,L,NE]
```

- **Match the bare host explicitly** rather than `!^www\.`. A request already on `www` can then never
  match, so **a redirect loop is impossible by construction** — and a loop takes the whole domain down.
- **`[NE]` is required.** `%{REQUEST_URI}` arrives already percent-encoded; without `NE`, mod_rewrite
  re-escapes it and `%20` becomes `%2520`. The query string rides along on its own — do not add `?`.
- ⚠️ **Host canonicalisation is not cosmetic when the app stores anything locally.** `localStorage`
  and cookies are **isolated per origin**, so `example.com` and `www.example.com` are two different
  stores: a visitor who arrives on the other host silently loses their saved state.

## 3. Count the redirect hops, and watch for an http downgrade

A bare-domain request can easily take three hops: your canonicalisation → a cPanel rule that emits
**`http://`** → the server's Force-HTTPS sending it back to `https://`. It works, so nobody notices.

**Fix by ordering and by protocol:** make every rule you control emit `https://`, and place your
block **above** the panel-generated ones. Then measure with `curl -sIL` and count.

## 4. In a shared document root, the `.htaccess` at the root is not yours

If your app lives in a subfolder (shape 2), the root `.htaccess` is **shared with other projects and
is in no repo**. It is edited by hand, no deploy touches it, and a mistake there affects everyone on
the domain.

- Keep your own `.htaccess` **inside your folder**, and minimal.
- Changes to the root file are the **owner's** to apply, by hand, with the rollback written down
  first (usually: delete these N lines — no deploy, no CI, immediate).

## 5. What is in the document root that you did not put there

Before the first `--delete`, **list the document root and write down every sibling**. On shared
hosting there is routinely something that is:

- **hand-uploaded and in no repo** — media, a landing page, a legacy folder. Git cannot restore it;
  only the panel's backup can.
- **another project's production asset**, possibly referenced by a different site's CSP or links.

That inventory is what makes `--delete` a decision instead of a gamble, and it belongs in the
project's own infrastructure doc, not in someone's memory.

## 6. A deploy probe must never become part of the product

The habit of dropping a test file on the server to check hosting behaviour is fine. **Deleting it
afterwards is the part that gets forgotten**, and a stray probe is both an indexable URL and a
misleading artefact for the next person. If a project keeps one, gitignore it and delete it from the
server the moment the question is answered.

## 7. The build toolchain is production supply chain

For a statically built site, nothing from `node_modules` is deployed — only the built output. That
makes a production-only dependency audit the right **gate**, and it also makes that gate **blind by
construction**: a compromised build tool writes straight into the output that does get deployed.

⇒ **Keep automated security alerts on, and fix by bumping rather than dismissing.** A dismissal
closes one advisory; a version bump closes the package. Never `npm audit fix --force`.
