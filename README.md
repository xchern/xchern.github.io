# xchern's website

A Hugo site using the PaperMod theme. Hugo builds locally; no GitHub Actions workflow is used. Source lives on `main`; the generated site is published to the root of `gh-pages` and is not stored in the source branch.

## Setup

Requirements: Hugo (extended edition recommended), Git, and rsync.

```sh
git clone --recurse-submodules <repository-url>
cd <repository-directory>
```

If the repository was cloned without submodules:

```sh
git submodule update --init --recursive
```

Set `SITE_BASE_URL` in your shell environment to the site's canonical base URL. Keep that value outside the repository. The build uses it for absolute URLs in metadata and the sitemap.

## Local preview

```sh
SITE_BASE_URL="$SITE_BASE_URL" hugo server -D
```

Open the local URL printed by Hugo. Draft posts are visible in preview; the sitemap continues to use the canonical site URL.

## Write a post

```sh
hugo new content blog/my-post/index.md
```

Posts are page bundles under `content/blog/`. New posts are drafts by default. Set `draft: false` and choose a publication date when ready. Add images beside `index.md` and refer to them with relative paths.

## Publish

Make sure the working tree contains only the site changes you intend to publish, then run from `main`:

```sh
./scripts/publish.sh "Publish my post"
```

The script builds to a temporary directory, commits source changes to `main`, and pushes the generated site to the root of `gh-pages`. It checks remote state and refuses to overwrite source changes it has not fetched. Rerun it after syncing if the remote has advanced.

Configure GitHub Pages once in repository settings: **Deploy from a branch**, branch `gh-pages`, folder `/` (root). GitHub Pages hosts the static branch; repository Actions workflows are not used.

## Structure

- `content/blog/`: articles
- `content/about.md`: biography
- `hugo.yaml`: site and theme configuration
- `assets/css/extended/custom.css`: optional site-specific styles
- `themes/PaperMod/`: PaperMod Git submodule
- `static/`: static resources, including the social icons
- `layouts/`: local Hugo template overrides

The `main` branch contains source only. Do not commit Hugo's generated output; the publish script sends it to `gh-pages`.
