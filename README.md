# xchern's website

Hugo + PaperMod. Source is on `main`; GitHub Actions builds and deploys to GitHub Pages using [Hugo's official workflow](https://gohugo.io/host-and-deploy/host-on-github-pages/), adapted to this site.

## Local preview

Install Hugo (CI uses 0.169.0), then run:

```sh
git submodule update --init --recursive
hugo server -D
```

## Write a post

```sh
hugo new content blog/my-post/index.md
```

Keep images beside `index.md`. Set the date and `draft: false` when ready.

## Publish

Commit your changes and push `main`. See **Actions → Build and deploy** for status. Pages must use **GitHub Actions** as its source.

Workflow: `.github/workflows/hugo.yaml`. No publish script or generated-site branch is needed.
