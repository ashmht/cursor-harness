# Validation

Run:

```bash
python3 scripts/validate.py
```

The validator fails closed across five layers:

1. **Filesystem:** rejects symlinks, private runtime directories, backup files,
   and unexpectedly large artifacts.
2. **Identity and organization:** rejects absolute user-home paths, account
   identifiers, private document URLs, unexpected email addresses, and
   caller-supplied forbidden terms. When the root is its own git checkout, the
   same checks run against the patches of every commit, so a deleted leak still
   fails. Git author headers and commit-message trailers are not part of that
   scan. Public attributions
   `hello@cocoon-ai.com`, `you@example.com`, and `a@b.com` are allowed.
3. **Secrets:** detects common token, credential, and private-key shapes.
4. **Structure and reuse:** verifies skill and rule frontmatter, skill names,
   and references to installed local skills.
5. **Syntax:** parses JSON, parses YAML with PyYAML, compiles Python in memory,
   and runs `bash -n` on executable shell scripts.

## Private organization-term pass

The public repository does not contain its private denylist. Supply one at
validation time:

```bash
export CURSOR_HARNESS_FORBIDDEN_TERMS_JSON='["company-name","internal-domain.example","private-product"]'
python3 scripts/validate.py
```

Use exact names, domains, repository names, product names, ticket prefixes, and
unique internal terminology. Matching is case-insensitive.

## Additional local checks

When available, run:

```bash
bash -n hooks/session-cost.sh
gitleaks detect --source . --no-banner --redact
git diff --check
```

The GitHub workflow runs the repository-native checks on every pull request and
push to `main`. External scanners remain an additional release gate.
