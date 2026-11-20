# Oak Creek Sport Horses: setup, start to finish

Everything below ends with Aidan owning her website: the code in **her GitHub**, the site hosted on
**her Cloudflare account** (free), and a **site key** that lets her add and edit horses at `/manage/`.
Bryan keeps access as a collaborator so updates can continue.

Allow about 30 minutes. Steps marked **Aidan** need her logged in; steps marked **Bryan** need you.

---

## Step 1. Aidan: create a GitHub account
1. Go to **github.com → Sign up**. Use her business email (AidanGreen@oakcreekthoroughbreds.com).
2. Pick a username (for example `oakcreeksporthorses`), verify the email, choose the **Free** plan.
3. Send Bryan the username.

## Step 2. Bryan: transfer the code to Aidan
1. Open **github.com/OC-aidan/oc-sporthorses → Settings → General**.
2. Scroll to **Danger Zone → Transfer ownership**.
3. Choose **Specify a user**, enter Aidan's username, type the repository name to confirm, then **Transfer**.

## Step 3. Aidan: accept the transfer and add Bryan back
1. Open the email from GitHub and **accept** the transfer. The code is now at
   `github.com/<her-username>/oc-sporthorses`.
2. In that repository: **Settings → Collaborators → Add people** → Bryan's GitHub username → **Write** access
   (or the default role offered).
3. Bryan accepts the invitation from his email.

## Step 4. Point the Horse Manager at her copy
The Horse Manager needs to know where the code now lives. Either:
- **Send Claude her username** and it will be updated, **or**
- In her repository, open `content/site.json` → pencil icon (Edit) → change
  `"repo": "OC-aidan/oc-sporthorses"` to `"repo": "<her-username>/oc-sporthorses"` → **Commit changes**.

## Step 5. Aidan: create the website on Cloudflare Pages
1. Go to **dash.cloudflare.com → Sign up** with her business email (free plan, no card needed).
2. In the left menu: **Workers & Pages → Create → Pages tab → Connect to Git**.
3. **Connect GitHub**, sign in as Aidan, and allow access to `oc-sporthorses` (choosing only this repository is fine).
4. Select **oc-sporthorses → Begin setup**, then enter:
   - Project name: `oc-sporthorses` (this becomes the free address)
   - Production branch: `main`
   - Framework preset: **None**
   - Build command: `python3 build.py`
   - Build output directory: `public`
5. **Save and Deploy.** After about a minute the site is live at **`oc-sporthorses.pages.dev`**.
   Open it and check the home page, a horse page and the Visit page.

## Step 6. Aidan: make her site key
The key lets the Horse Manager save to her website and nothing else. Create it while logged in as Aidan.
1. GitHub → her profile picture → **Settings → Developer settings** (bottom of the left menu)
   → **Personal access tokens → Fine-grained tokens → Generate new token**.
2. Fill in:
   - Token name: `Oak Creek Horse Manager`
   - Expiration: **1 year** (put a renewal reminder in her calendar)
   - Repository access: **Only select repositories →** `oc-sporthorses`
   - Permissions → Repository permissions → **Contents: Read and write** (leave everything else alone)
3. **Generate token**, then copy it right away (it starts with `github_pat_` and is shown only once).
   Save it in her phone's password manager or Notes. Don't email it.

## Step 7. Aidan: first sign-in and a test listing
1. Open the website and tap **🔒 Owner sign-in** at the very bottom of any page (or go to **`oc-sporthorses.pages.dev/manage/`**) on her phone, paste the key, keep
   "Keep me signed in on this device" ticked, and **Sign in**.
2. Tap **+ List a new horse**, enter a name, then **Save as draft (hidden)**.
3. Wait two minutes and confirm nothing new shows on the website (drafts stay hidden). Then select the
   test horse and **Delete this listing**.
4. Do the same on her computer if she'll use both.

## Step 8. Her own web address (optional, recommended)
1. In Cloudflare: **Workers & Pages → oc-sporthorses → Custom domains → Set up a custom domain**.
2. Enter the domain (e.g. `oakcreeksporthorses.com` or `www.oakcreekthoroughbreds.com`) and follow the
   prompts. Cloudflare explains which DNS records to add at the domain registrar, or offers to manage the
   domain itself. Email at that domain keeps working; only the website records change.
3. After it's connected, the Horse Manager is at `<her-domain>/manage/`.
4. Update `"site_url"` in `content/site.json` to the new address (e.g. `https://oakcreeksporthorses.com`) so Facebook link previews point to it. Also do this right after Step 5 with the `pages.dev` address.

## Step 9. Bryan: tidy up
1. Delete the old Vercel project (**vercel.com → oc-sporthorses → Settings → Delete**).
   Vercel's free plan doesn't allow business sites, and Cloudflare replaces it.
2. When her real horses, photos and story are in, remove the "Preview site" banner: set
   `"preview_banner": ""` in `content/site.json` (or ask Claude).
3. Still to connect: the inquiry forms to her email, and the "see new horses first" list.

---

## How Aidan uses it day to day
1. **Videos:** upload riding videos to **Vimeo** with privacy set to **Unlisted** (or "Hide from Vimeo") and
   embedding allowed. Copy the link and press **Add video**. Short clips under 24 MB can be uploaded
   straight from her phone.
2. **Photo:** upload one side-on, standing photo. It's resized automatically.
3. Fill in the details, training, price and status, then **Publish**. The website updates in 1–2 minutes.
4. **Create Facebook post** writes the caption. Post it on the Oak Creek business page with the link
   (not Marketplace or buy-and-sell groups, which remove animal sales).
5. **Sold:** set Status to **Sold**; the horse moves to the Graduates page automatically.
6. **Not ready yet?** New horses start as drafts and stay off the website until she presses **Publish**.
7. **Archived:** hides a horse from the website entirely (including Graduates) but keeps its record in the Horse Manager. Pick another status and Publish to bring it back.

## If something goes wrong
| Problem | Fix |
|---|---|
| "That key didn't work" | The key expired or was mistyped. Make a new one (Step 6) and sign in again. |
| Lost phone or key shared by mistake | GitHub → Settings → Developer settings → Fine-grained tokens → delete the key, then make a new one. |
| Published but the site didn't change | Wait 2 minutes and refresh. Still nothing: Cloudflare → oc-sporthorses → **Deployments** shows any error. Send Bryan a screenshot. |
| "Clips must be under 24 MB" | Put that video on Vimeo and paste the link instead. |
| Vimeo video won't play on the site | On Vimeo, open the video's **Share/Embed** settings and allow embedding on any site. |

Limits on the free Cloudflare plan: 500 publishes a month, 25 MB per file, unlimited visitors.
