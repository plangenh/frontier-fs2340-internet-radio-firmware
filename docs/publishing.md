# Connecting GitHub later

The local repository is separate from the private analysis workspace. It has no remote or credentials configured.

## Create the repository in a browser

1. Sign in to GitHub and create a repository named `majority-touro-research`.
2. Choose **Public**. Do not generate an additional README, license, or `.gitignore`; they already exist locally.
3. Open a terminal in this project directory. If needed, configure your Git identity for this repository only.
4. Add the HTTPS or SSH address shown by GitHub as the remote and push:

```sh
git remote add origin https://github.com/YOUR-NAME/majority-touro-research.git
git push -u origin main
```

Authenticate using your own Git credentials or GitHub CLI. No credentials need to be placed in project files.

## Enable GitHub Pages

After pushing, select **Settings → Pages → Build and deployment → Source: GitHub Actions**. Then run **Actions → Deploy research pages → Run workflow**. The workflow uploads only `site/`. Subsequent pushes to `main` that change `site/` trigger another deployment.

GitHub displays the final Pages URL in the deployment. No public URL exists before the repository is connected and deployed.

## ZIP alternative

The ZIP includes only curated project files, without Git history. You can extract it and upload through GitHub's web interface. Include hidden files such as `.github/` and `.gitignore`.

## Before publishing

```sh
python3 -m unittest discover -s tests -v
python3 tools/publication_check.py
git status --short
git diff --cached
```

Checks do not replace reviewing the contents of newly added attachments.

The Pages configuration follows the [official GitHub documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
