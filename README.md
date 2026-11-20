# Oak Creek Sport Horses: website

Hunter & Gold design. Static site, no frameworks, no npm. `build.py` (Python 3, standard library only)
turns `content/*.json` into the finished site in `public/`. The host runs it on every push.
Recommended host: Cloudflare Pages (free for business use). See **SETUP.md** for hosting, the Horse Manager key, and how Aidan uses it.

## Pages
- `/` home: video hero, featured horses, Pasture to Partner, story teaser, graduates, first-look signup
- `/horses/` all available horses with filters
- `/horses/<slug>/` sale page: video player with chapters, price, specs, training, pedigree, inquiry form, Facebook share
- `/story/`, `/graduates/`, `/visit/`
- `/manage/` **Horse Manager**: sign in with the site key; add Vimeo links or upload short clips and photos; edit details, price and status; Publish saves to this repo and the site rebuilds; Facebook post generator

## Change content
- Horses: `content/horses.json` (`status`: `available` | `under-offer` | `sold`; sold horses move to Graduates)
- Site text, contact, social links, graduates: `content/site.json`. Set `preview_banner` to `""` before launch.
- Photos/videos: see `IMAGES.md` for file names. A missing file shows a pasture drawing instead.
- Video on a listing: put a YouTube or Vimeo link in `youtube` / `vimeo`, or a file path in `src`.

## Run locally
```
python3 build.py && python3 -m http.server -d public 8000
```

## Not wired yet
1. **Forms**: inquiry, visit and first-look forms show a thank-you but don't send. Set `FORM_ENDPOINT` in
   `src/main.js` (e.g. Formspree, free tier) to deliver them to AidanGreen@oakcreekthoroughbreds.com.
2. **First-look texts/emails**: connect the signup form to Mailchimp or Flodesk.
3. **Domain**: add it in Cloudflare Pages → Custom domains.
4. **Facebook**: post on her business page (not Marketplace or buy-and-sell groups, which remove animal sales).
