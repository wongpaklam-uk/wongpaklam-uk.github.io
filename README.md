# Berlin Apps · Official Showcase Website

A responsive black-and-gold website for **Berlin**, Software Developer & AI Systems Engineer.

## Live site

https://wongpaklam-uk.github.io/

## Pages

- Home: Berlin AI, DownhillSpotter and Metronome by Berlin
- Berlin AI: /apps/berlin-ai.html — original development/test UI captures
- DownhillSpotter: /apps/downhillspotter.html — verified App Store link, genuine screenshots when available, safety warning, demo video
- Metronome by Berlin: /apps/metronome.html — verified App Store link, genuine screenshots when available
- Homepage roadmap: DownhillLab and PhotoRename

The original user-supplied gold logo is preserved. Only **Berlin** is used on the website as the public developer name.

## Real screenshots

- Berlin AI source screenshots are synthetic-test-interface captures taken from the developer's private GitHub project. The three selected captures show no live account credentials.
- The two published apps use Apple's original App Store screenshots. The gallery requests the official Apple image URL when the bundled files are not present.
- A GitHub Actions job in `.github/workflows/sync_appstore.yml` tries to archive Apple's actual images into `assets/screenshots/` on deployment and monthly thereafter. See `scripts/import_appstore.py`.
- If Apple does not expose images, the site links to the official App Store listing rather than using fabricated images.

## Publish and maintain

This repository is already configured as a GitHub Pages repository. Keep the original `app-ads.txt` unchanged.

Add future apps to the `BERLIN_APPS` array in `index.html`, and add a new details page at `apps/<slug>.html`.

**Verified App Store URLs**

- DownhillSpotter: https://apps.apple.com/gb/app/downhillspotter/id6829381502
- Metronome by Berlin: https://apps.apple.com/gb/app/metronome-by-berlin/id6824046685

Contact: berlinwong.uk@gmail.com
