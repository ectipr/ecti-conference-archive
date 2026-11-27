# ECTI Conference Archive

Read-only static snapshots of past ECTI Association conference websites (ECTI-CARD, ECTI-CON,
ICA-SYMP, ISCIT, ITC-CSCC), published with GitHub Pages at
https://ectipr.github.io/ecti-conference-archive/

The ECTI Association's own website (ecti-thailand.org) is archived separately in
[ectipr/ecti-archive](https://github.com/ectipr/ecti-archive) (https://ectipr.github.io/ecti-archive/).

## Summary

31 conference websites are archived (784 MB). Every site is read-only: registration, paper
submission, contact forms and search no longer work.

| Status | Sites |
|---|---|
| Complete, looks like the original (22) | ECTI-CARD 2010–2016, 2019, 2022, 2023 · ECTI-CON 2010, 2012–2015, 2019, 2023 · ICA-SYMP 2023, 2025, 2026 · ISCIT 2024 · ITC-CSCC 2026 |
| Rebuilt from the Wayback Machine, styled (6) | ECTI-CARD 2009, 2020 · ECTI-CON 2009, 2016, 2021, 2022 |
| Rebuilt from the Wayback Machine, text only (3) | ECTI-CARD 2018 · ECTI-CON 2011, 2020 |
| Not available | ECTI-CARD 2017, 2021 · ECTI-CON 2017, 2018 |

Known gaps in otherwise complete sites (the files are missing from the server backup, the live
server and the Wayback Machine alike):

| Site | Missing |
|---|---|
| ECTI-CARD 2013 | 5 menu icons |
| ECTI-CARD 2014 | full-paper links (the folder was already empty in the backup) |
| ECTI-CARD 2019 | gallery photos are resized to 2048 px; originals are in the release (see below) |
| ECTI-CARD 2022 | some pages were unstyled on the original site (`css/main.css` was missing there too) |
| ECTI-CON 2014 | 2 LaTeX template downloads |
| ECTI-CON 2015 | some images and documents under `img/` and `doc/` |
| ICA-SYMP 2026 | the home page header background image |

ECTI-CARD 2018: the theme (dt-the7), plugins and `wp-content/uploads` are missing from the server backup and from the Wayback Machine, so the site has no styling or images. Its WordPress database did survive (`ecti_card2018content`); three hotel posts that Wayback never captured (The Grand Riverside Hotel, The Viewpoint Hotel, The Harmony Ville Apartment) were rebuilt from it with `tools/ecticard2018_hotels_from_db.py`. Every other published page in that database is already in the archive, or has no real content (empty, or only a pop-up script).

Not archived on purpose: the paper-submission systems and anything containing authors' data,
the `ecticon2023tmp` folder (a compromised copy of ECTI-CON 2023) and `icasymp2026.bak` (a
duplicate). See `EXCLUDE.md`.

## Layout

| Path | Contents |
|---|---|
| `docs/` | The published site (GitHub Pages: branch `main`, folder `/docs`). `docs/index.html` lists every archived conference; each conference is in `docs/<name>/`. |
| `tools/` | Scripts used to build the snapshots (crawl, mirror a local Docker copy, restore from the Wayback Machine, fix links, generate the landing page). |
| `EXCLUDE.md` | What was deliberately left out (author submissions, configuration, databases, keys, backups). |

## Large files

- The ECTI-CARD 2019 and 2022 proceedings PDFs (65 MB and 77 MB) are not duplicated here: the
  pages link to the copies in [ectipr/ecti-archive](https://github.com/ectipr/ecti-archive)
  `documents/`.
- The ECTI-CARD 2019 photo galleries were resized to 2048 px. The full-resolution originals
  (634 MB zip) are attached to the GitHub Release
  [`assets-v1`](https://github.com/ectipr/ecti-conference-archive/releases/tag/assets-v1).

## Publishing

Settings → Pages → Deploy from a branch → `main` / `/docs`. The absolute URLs that some WordPress
pages need are already filled in for `https://ectipr.github.io/ecti-conference-archive/`;
`tools/build.py` can rebuild a site for a different URL.

## How the snapshots were made

- Sites still online were crawled politely from their own domains (`tools/crawl.sh`), and files
  missing from the crawl were filled from the server backup.
- Offline WordPress sites were restored from the server backup, run locally in Docker
  (`tools/docker-compose.yml`) and mirrored with wget (`tools/mirror-local.sh`). ECTI-CARD 2014
  (WordPress 3.8) and ECTI-CARD 2016 (Joomla) need an old PHP version and were run in a local
  PHP 5.6 container (`tools/php56/Dockerfile`).
- `tools/postprocess.py`, `tools/localize.py` and `tools/linkcheck.py` make every site
  self-contained and working under a sub-path.
- Sites with no usable backup and no live server were rebuilt from the Internet Archive Wayback
  Machine (`tools/wayback.py`, `tools/wayback_fill.py`): ECTI-CARD 2009, 2018, 2020 and ECTI-CON
  2009, 2011 (www.ecti-con2011.org), 2016 (www.ecticon2016.org), 2020, 2021 and 2022
  (www.ecti-con2022.org, May 2022 captures only; later captures of that domain are spam).
  The Wayback Machine kept the pages and PDFs but often not the theme CSS or images. Where the
  theme, plugins or WordPress core were free releases, the exact versions were taken from
  wordpress.org (`tools/fill_from_dir.py`), which restored the styling of ECTI-CARD 2020 and
  ECTI-CON 2021 and 2022.
- ECTI-CARD 2017, 2021 and ECTI-CON 2017, 2018 were never captured anywhere (backup, server or
  Wayback Machine): only hosting placeholder pages and the excluded submission system exist.
- `tools/landing.py` generates `docs/index.html`.
