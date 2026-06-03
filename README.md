A Github Pages template for academic websites. This was forked (then detached) by [Stuart Geiger](https://github.com/staeiou) from the [Minimal Mistakes Jekyll Theme](https://mmistakes.github.io/minimal-mistakes/), which is © 2016 Michael Rose and released under the MIT License. See LICENSE.md.

I think I've got things running smoothly and fixed some major bugs, but feel free to file issues or make pull requests if you want to improve the generic template / theme.

### Note: if you are using this repo and now get a notification about a security vulnerability, delete the Gemfile.lock file. 

# Instructions

1. Register a GitHub account if you don't have one and confirm your e-mail (required!)
1. Fork [this repository](https://github.com/academicpages/academicpages.github.io) by clicking the "fork" button in the top right. 
1. Go to the repository's settings (rightmost item in the tabs that start with "Code", should be below "Unwatch"). Rename the repository "[your GitHub username].github.io", which will also be your website's URL.
1. Set site-wide configuration and create content & metadata (see below -- also see [this set of diffs](http://archive.is/3TPas) showing what files were changed to set up [an example site](https://getorg-testacct.github.io) for a user with the username "getorg-testacct")
1. Upload any files (like PDFs, .zip files, etc.) to the files/ directory. They will appear at https://[your GitHub username].github.io/files/example.pdf.  
1. Check status by going to the repository settings, in the "GitHub pages" section
1. (Optional) Use the Jupyter notebooks or python scripts in the `markdown_generator` folder to generate markdown files for publications and talks from a TSV file.

See more info at https://academicpages.github.io/

## To run locally (not on GitHub Pages, to serve on your own computer)

1. Clone the repository and made updates as detailed above
1. Make sure you have ruby-dev, bundler, and nodejs installed: `sudo apt install ruby-dev ruby-bundler nodejs`
1. Run `bundle clean` to clean up the directory (no need to run `--force`)
1. Run `bundle install` to install ruby dependencies. If you get errors, delete Gemfile.lock and try again.
1. Run `bundle exec jekyll liveserve` to generate the HTML and serve it from `localhost:4000` the local server will automatically rebuild and refresh the pages on change.

# Changelog -- bugfixes and enhancements

There is one logistical issue with a ready-to-fork template theme like academic pages that makes it a little tricky to get bug fixes and updates to the core theme. If you fork this repository, customize it, then pull again, you'll probably get merge conflicts. If you want to save your various .yml configuration files and markdown files, you can delete the repository and fork it again. Or you can manually patch. 

To support this, all changes to the underlying code appear as a closed issue with the tag 'code change' -- get the list [here](https://github.com/academicpages/academicpages.github.io/issues?q=is%3Aclosed%20is%3Aissue%20label%3A%22code%20change%22%20). Each issue thread includes a comment linking to the single commit or a diff across multiple commits, so those with forked repositories can easily identify what they need to patch.

---

# 🗒️ Quick Update Guide

## Publications
Fetched automatically from Google Scholar every Sunday via GitHub Actions.  
To manually refresh (wait 24 h between runs to avoid rate limiting):
```bash
python3 markdown_generator/fetch_from_scholar.py          # all papers
python3 markdown_generator/fetch_from_scholar.py --since 2024  # only recent
```
To fill missing venue fields using Semantic Scholar:
```bash
python3 markdown_generator/enrich_venues.py
```

## Talks
1. Open `markdown_generator/talks.xlsx` and add a new row.  
   Key columns: `title`, `url_slug` (unique slug), `date` (YYYY-MM-DD or DD/MM/YYYY), `type`, `venue`, `location`, `talk_url`, `description`, `image` (optional path/URL).
2. Regenerate markdown files:
   ```bash
   python3 markdown_generator/talks.py
   ```

## Students (Teaching / Supervision)
1. Open `markdown_generator/students.xlsx` and add a new row.  
   Key columns: `Name`, `Type` (PhD / Master / Bachelor / High School), `Institution`, `Thesis / Research Topic`, `Start Date`, `End Date`, `Location`, `Notes`.
2. Regenerate markdown files:
   ```bash
   python3 markdown_generator/students.py
   ```

## News / Updates (About page)
Edit `_data/updates.yml` — add new items at the **top**:
```yaml
- date: "Jun. 2026"
  text: "Your news item here."
  url: "https://optional-link.com"   # omit if no link
```

## LinkedIn Embed (About page)
Go to your LinkedIn post → **···** → **Embed this post** → copy the `src="..."` value.  
Paste it into `_data/linkedin_embed.yml`:
```yaml
url: "https://www.linkedin.com/embed/feed/update/urn:li:share:XXXXXXXXX"
```

## Portfolio
1. Open `markdown_generator/portfolio.xlsx` and add a new row.  
   Key columns: `title`, `image` (local path or URL), `youtube` (video ID), `description`, `tags` (comma-separated), `body` (full page text).
2. Regenerate markdown files:
   ```bash
   python3 markdown_generator/portfolio.py
   ```

## Navigation Bar
Edit `_data/navigation.yml` to add, remove, or reorder top-bar links.

## Site Info (name, bio, social links)
Edit `_config.yml` — key fields: `title`, `name`, `description`, `url`, `author` (bio, avatar, social links).

## Talk Page Layout
Each talk's individual page is controlled by `_layouts/talk.html`.  
Front matter fields rendered: `date`, `type`, `venue`, `location`, `image`.
