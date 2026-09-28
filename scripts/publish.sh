#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z "$1" ]]; then
  echo "Usage: $0 \"commit message\"" >&2
  exit 2
fi
: "${SITE_BASE_URL:?Set SITE_BASE_URL to the canonical URL of this site}"

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

branch="$(git branch --show-current)"
if [[ "$branch" != "main" ]]; then
  echo "Refusing to publish from branch '$branch'; switch to main first." >&2
  exit 1
fi
if [[ -n "$(git diff --cached --name-only)" ]]; then
  echo "The Git index has staged changes. Commit or unstage them before publishing." >&2
  exit 1
fi
hugo version >/dev/null
git submodule update --init --recursive
git fetch origin main
if ! git merge-base --is-ancestor origin/main HEAD; then
  echo "Local main is behind or diverged from origin/main. Pull/reconcile before publishing." >&2
  exit 1
fi

build_dir="$(mktemp -d)"
deploy_dir="$build_dir/gh-pages"
deploy_branch="site-deploy-$$"
cleanup() {
  if git worktree list --porcelain | grep -Fq "worktree $deploy_dir"; then
    git worktree remove --force "$deploy_dir" >/dev/null 2>&1 || true
  fi
  git branch -D "$deploy_branch" >/dev/null 2>&1 || true
  rm -rf "$build_dir"
}
trap cleanup EXIT

hugo --baseURL "$SITE_BASE_URL" --minify --destination "$build_dir/site"
test -s "$build_dir/site/index.html"
test -s "$build_dir/site/blog/index.html"
test -s "$build_dir/site/about/index.html"
if grep -qiE 'localhost|127\.0\.0\.1' "$build_dir/site/sitemap.xml"; then
  echo "Sitemap contains a local development address; refusing to publish." >&2
  exit 1
fi
touch "$build_dir/site/.nojekyll"

# Keep generated output out of main. Stage only Hugo source and project files.
git add -A -- content archetypes assets static layouts hugo.yaml .gitignore .gitmodules themes scripts README.md
if [[ -n "$(git ls-files docs)" ]]; then
  git rm -r --cached -- docs
fi
if ! git diff --cached --quiet; then
  git commit -m "$1"
fi
if ! git merge-base --is-ancestor origin/main HEAD; then
  echo "Local main is behind or diverged from origin/main. Resolve before publishing." >&2
  exit 1
fi
git push origin main

# Publish the generated site from the dedicated branch's root directory.
remote_deploy_ref="$(git ls-remote --heads origin gh-pages)"
if [[ -n "$remote_deploy_ref" ]]; then
  git fetch origin gh-pages
  git worktree add --detach "$deploy_dir" origin/gh-pages
else
  git worktree add --orphan -b "$deploy_branch" "$deploy_dir"
fi
rsync -a --delete --exclude=.git "$build_dir/site/" "$deploy_dir/"
git -C "$deploy_dir" add -A
if ! git -C "$deploy_dir" diff --cached --quiet; then
  git -C "$deploy_dir" commit -m "Deploy site from $(git rev-parse --short HEAD)"
  git -C "$deploy_dir" push origin HEAD:gh-pages
fi

echo "Source published to origin/main; generated site published to origin/gh-pages."
