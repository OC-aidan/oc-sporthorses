#!/usr/bin/env python3
"""Builds the Oak Creek Sport Horses site from content/*.json into public/.
Run: python3 build.py   (Vercel runs this automatically on every deploy)"""
import json, os, shutil, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')
S = json.load(open(os.path.join(ROOT, 'content/site.json')))
ALL = json.load(open(os.path.join(ROOT, 'content/horses.json')))
H = [h for h in ALL if h.get('status') in ('available', 'under-offer', 'sold')]  # drafts and archived stay hidden
e = html.escape
STATUS = {'available': 'Available', 'under-offer': 'Under offer', 'sold': 'Sold'}

def exists(p):
    if not p:
        return False
    if p.startswith('http://') or p.startswith('https://'):
        return True
    return os.path.exists(os.path.join(ROOT, p))

def scene(seed=0, dark=False):
    o = (seed % 5) * 37
    posts = ''.join(f'<rect x="{x}" y="{420 - (x-60)*0.05:.0f}" width="7" height="70" fill="#2F4A37" opacity=".85"/>' for x in range(60, 1200, 120))
    trees = ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2F4A37"/><rect x="{cx-3}" y="{cy}" width="6" height="{r+10}" fill="#2F4A37"/>'
                    for cx, cy, r in [(820+o, 250, 34), (870+o, 262, 24), (160+o//2, 270, 22)])
    shade = '<rect width="1200" height="600" fill="#0d1a12" opacity=".3"/>' if dark else ''
    return f'''<svg viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs><linearGradient id="sk{seed}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9D3C0"/><stop offset="1" stop-color="#EDE6D3"/></linearGradient></defs>
<rect width="1200" height="600" fill="url(#sk{seed})"/><circle cx="{930-o}" cy="150" r="60" fill="#fff" opacity=".35"/>
<path d="M0 300 C200 {240+o//3} 380 260 600 280 S1000 230 1200 270 V600 H0Z" fill="#7E9478"/>{trees}
<path d="M0 380 C260 330 520 350 760 372 S1060 340 1200 360 V600 H0Z" fill="#4E6B52"/>
<path d="M0 445 C300 410 700 430 1200 405" stroke="#2F4A37" stroke-width="5" fill="none"/><path d="M0 475 C300 440 700 460 1200 435" stroke="#2F4A37" stroke-width="5" fill="none"/>{posts}
<path d="M0 500 C300 480 800 500 1200 470 V600 H0Z" fill="#2F4A37" opacity=".55"/>{shade}</svg>'''

def url(p, pre=''):
    return p if p.startswith('http') else pre + p

def yt_id(v):
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})', v or '')
    return m.group(1) if m else (v if v and re.fullmatch(r'[\w-]{11}', v) else '')

def vm_id(v):
    m = re.search(r'vimeo\.com/(?:.*?/)?(?:video/)?(\d{6,})(?:/([0-9a-f]{6,}))?(?:\?h=([0-9a-f]+))?', v or '', re.I)
    return (m.group(1), m.group(2) or m.group(3) or '') if m else ('', '')

def media(img='', label='', ar='16/10', play=False, seed=0, video='', small=False, pre=''):
    """Real photo/video when the file exists, otherwise a pasture drawing."""
    if video and exists(video):
        inner = f'<video src="{url(video, pre)}" muted playsinline preload="metadata"></video>'
    elif img and exists(img):
        inner = f'<img src="{url(img, pre)}" alt="{e(label)}" loading="lazy">'
    else:
        inner = scene(seed)
    p = f'<span class="play{" sm" if small else ""}"></span>' if play else ''
    l = f'<span class="lab">{e(label)}</span>' if label else ''
    return f'<div class="ph" style="--ar:{ar}">{inner}{p}{l}</div>'

def price(h, short=False):
    if h.get('price_display') == 'request' or not h.get('price'):
        return 'Price on request'
    s = f"${h['price']:,}"
    if h.get('price_display') == 'range' and h.get('price_max'):
        s += f" to ${h['price_max']:,}"
    return s if short else s

def thumb_for(h):
    v = (h.get('videos') or [{}])[0]
    if v.get('vimeo') and v.get('thumb'):
        return v['thumb']
    if yt_id(v.get('youtube')):
        return f"https://img.youtube.com/vi/{yt_id(v['youtube'])}/hqdefault.jpg"
    return ''

def hcard(h, i, pre=''):
    nv = len(h.get('videos', []))
    yt = thumb_for(h)
    if yt and not exists(h.get('photo')):
        m = f'<div class="ph" style="--ar:16/10"><img src="{yt}" alt="{e(h["name"])}" loading="lazy"><span class="play sm"></span><span class="lab">▶ {nv} videos</span></div>'
    else:
        m = media(h.get('photo'), f'▶ {nv} video{"s" if nv != 1 else ""}', '16/10', True, i + 4, small=True, pre=pre)
    meta = f"{h['year']} {h['sex']} · {h['breeding']} · {h['height']}" + (f", maturing {h['mature_height']}" if h.get('mature_height') else '')
    return f'''<a class="card" href="{pre}horses/{h['slug']}/" data-status="{h['status']}" data-sex="{h['sex'].lower()}">{m}
<div class="body"><div class="row-top"><span class="chip st-{h['status']}">{STATUS[h['status']]}</span>{'<span class="sample">Sample listing</span>' if h.get('sample') else ''}</div>
<h3>{e(h['name'])}</h3><div class="meta">{e(meta)}</div><div class="spacer"></div>
<div class="foot"><span class="price">{price(h)}</span><span class="link">Watch &amp; details →</span></div></div></a>'''

NAV = [('horses/', 'Available Horses'), ('#pasture', 'Pasture to Partner'), ('story/', 'Our Story'), ('graduates/', 'Graduates'), ('visit/', 'Visit')]

def page(title, body, pre='', over=False, on='', desc='', og_img='', path=''):
    links = ''.join(f'<a href="{pre}{u}" class="{"on" if on == u else ""}">{t}</a>' for u, t in NAV)
    logo = f'{pre}assets/img/logo-{"gold" if over else "green"}.png'
    banner = f'<div class="preview-bar">{e(S["preview_banner"])}</div>' if S.get('preview_banner') else ''
    desc = desc or S['tagline']
    og = og_img or 'assets/img/logo-full.png'
    base = (os.environ.get('SITE_URL') or S.get('site_url') or '').rstrip('/')
    og = og if og.startswith('http') else f"{base}/{og}"
    canon = f'<meta property="og:url" content="{base}/{path}">' if base else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:site_name" content="{e(S['name'])}"><meta property="og:image" content="{og}">{canon}<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{pre}favicon.png"><link rel="apple-touch-icon" href="{pre}apple-touch-icon.png"><link rel="stylesheet" href="{pre}assets/style.css"></head><body>
{banner}<header class="{'over' if over else 'solid'}" {'style="top:' + ('30px' if banner else '0') + '"' if over else ''}><div class="wrap nav" id="nav"><a class="logo" href="{pre or './'}"><img src="{logo}" alt="Oak Creek Sport Horses"></a>
<button class="menu-btn" aria-label="Menu" onclick="document.getElementById('nav').classList.toggle('open')"><span></span></button>
<div class="links">{links}<a class="btn {'bgold' if over else 'b1'}" href="{pre}visit/">Inquire</a></div></div></header>
{body}
<footer><div class="wrap"><div class="cols"><div><img src="{pre}assets/img/logo-gold.png" alt="" style="height:76px;width:auto"><p style="margin-top:14px;opacity:.75;font-size:14px;max-width:280px">{e(S['tagline'])}</p></div>
<div><b>Horses</b><a href="{pre}horses/">Available</a><a href="{pre}graduates/">Graduates</a><a href="{pre or './'}#pasture">Pasture to Partner</a></div>
<div><b>Visit</b><a href="{pre}visit/">Book a visit</a><a href="{pre}visit/#call">Video call viewing</a><a href="{pre}story/#buying">Buying from us</a></div>
<div><b>Follow</b><a href="{S['facebook_url'] or '#'}">Facebook</a><a href="{S['instagram_url'] or '#'}">Instagram</a><a href="{S['youtube_url'] or '#'}">YouTube</a></div></div>
<div class="small"><span>© 2026 {e(S['name'])} · {e(S['location'])}</span><a class="owner" href="{pre}manage/" rel="nofollow"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>Owner sign-in</a></div></div></footer>
<script src="{pre}assets/main.js"></script></body></html>'''

def signup():
    return '''<section style="padding-bottom:0"><div class="wrap"><div class="signup"><div><h2 style="font-size:34px">See new horses first</h2>
<p class="muted" style="margin-top:6px">Get a text or email the day a new horse is listed, before it's shared anywhere else.</p></div>
<form data-form="firstlook"><input required placeholder="Email or mobile number" aria-label="Email or mobile number"><button class="btn b1">Notify me</button>
<div class="ok" style="width:100%">You're on the list. We'll let you know when the next horse is listed.</div></form></div></div></section>'''

def home():
    hv = S.get('hero_video')
    if exists(hv):
        hm = f'<video autoplay muted loop playsinline poster="{S["hero_poster"] if exists(S["hero_poster"]) else ""}" src="{hv}"></video>'
    elif exists(S.get('hero_poster')):
        hm = f'<img src="{S["hero_poster"]}" alt="">'
    else:
        hm = scene(1, True)
    vals = [('The cross', 'Clydesdale bone, sense and kindness, with Thoroughbred athleticism and stamina.'),
            ('Raised in a herd', 'Foaled and grown up on open pasture, learning manners from the herd.'),
            ('Shown on video', 'Every horse has its own videos: ground work, under saddle, trail and water.')]
    forsale = [h for h in H if h['status'] != 'sold' and h.get('featured')][:3]
    steps = ''.join(f'''<div><button data-video="{s[2] if exists(s[2]) else ''}" style="width:100%;text-align:left">{media('', '▶ ' + s[0], '16/10', True, i + 7, video=s[2], small=True)}</button>
<div class="step-cap"><span class="n">0{i+1}</span><div><b style="font-weight:600">{s[0]}</b><div class="muted" style="font-size:13.5px">{s[1]}</div></div></div></div>''' for i, s in enumerate(S['steps']))
    grads = ''.join(f'<div>{media(g["photo"], "Owner photo" if not exists(g["photo"]) else "", "4/3", seed=i+13)}<div class="muted" style="font-size:13px;margin-top:8px">{e(g["name"])} · {e(g["home"])}</div></div>' for i, g in enumerate(S['graduates']))
    body = f'''<div class="hero"><div class="media">{hm}</div><div class="shade"></div><div class="wrap inner">
<div class="kick">Clydesdale × Thoroughbred Sport Horses</div><h1>{S['headline'].replace('. ', '.<br>')}</h1><p>{e(S['tagline'])}</p>
<div class="ctas"><a class="btn bgold" href="horses/">See available horses</a><a class="btn b2" href="#pasture">▶ Watch the herd</a></div></div></div>
<section><div class="wrap values">{''.join(f'<div><div class="rule"></div><h3>{a}</h3><p class="muted">{b}</p></div>' for a, b in vals)}</div></section>
<section style="padding-top:0"><div class="wrap"><div class="head-row"><div><div class="kick">Available now</div><h2 style="margin-top:8px">Meet the horses</h2></div>
<a class="link" href="horses/">All horses ({len([h for h in H if h['status'] != 'sold'])}) →</a></div><div class="grid3">{''.join(hcard(h, i) for i, h in enumerate(forsale))}</div></div></section>
<section class="dark" id="pasture"><div class="wrap"><div class="head-row" style="margin-bottom:34px"><div><div class="kick">From pasture to partner</div><h2 style="margin-top:8px">Watch them grow up</h2></div>
<p class="muted" style="max-width:400px">Short videos follow a horse from foal to finished partner, so you know exactly what you're getting.</p></div><div class="steps">{steps}</div></div></section>
<section><div class="wrap split">{media('assets/img/story.jpg', 'Aidan with the herd', '4/3.2', seed=11)}
<div><div class="kick">Our story</div><h2 style="margin-top:10px">A small herd, raised the slow way</h2><div class="rule"></div>
<p class="muted lede">{e(S['story_short'])}</p><p style="margin-top:22px"><a class="link" href="story/">Read our story →</a></p></div></div></section>
<section style="padding-top:0"><div class="wrap"><div class="center"><div class="kick">Graduates</div><h2 style="margin-top:8px">Where they are now</h2>
<p class="muted" style="margin-top:8px">Horses that have gone on to new homes, with updates and photos from their owners.</p></div><div class="grads">{grads}</div>
<p class="center" style="margin-top:24px"><a class="link" href="graduates/">See all graduates →</a></p></div></section>
{signup()}'''
    return page(f"{S['name']} · Clydesdale × Thoroughbred Sport Horses", body, '', True)

def horses_index():
    live = [h for h in H if h['status'] != 'sold']
    body = f'''<div class="wrap page-head"><div class="kick">Available horses</div><h1 style="margin-top:8px">Meet the horses</h1>
<p class="muted lede">Every horse has its own videos. Watch them move, then ask us anything or book a visit or video call.</p>
<div class="filters" data-filter><button class="on" data-f="all">All</button><button data-f="available">Available</button><button data-f="under-offer">Under offer</button><button data-f="gelding">Geldings</button><button data-f="mare">Mares</button></div>
<div class="grid3">{''.join(hcard(h, i, '../') for i, h in enumerate(live))}</div>
<p class="muted" style="margin-top:30px">Looking for something specific? <a class="link" href="../visit/">Tell us what you need</a> and we'll let you know when the right horse comes along.</p></div>{signup()}'''
    return page(f"Available Horses · {S['name']}", body, '../', on='horses/')

def video_item(v, i, pre):
    yt, (vm, vh) = yt_id(v.get('youtube')), vm_id(v.get('vimeo'))
    if vm:
        return dict(kind='vimeo', id=vm, h=vh, thumb=v.get('thumb', ''))
    if yt:
        return dict(kind='youtube', id=yt, thumb=f'https://img.youtube.com/vi/{yt}/hqdefault.jpg')
    if exists(v.get('src')):
        return dict(kind='file', src=url(v['src'], pre), thumb='')
    return dict(kind='none', thumb='')

def horse_page(h):
    pre = '../../'
    vids = h.get('videos', [])
    items = [video_item(v, i, pre) for i, v in enumerate(vids)]
    for it, v in zip(items, vids):
        it.update(chapter=v['chapter'], title=v['title'], duration=v.get('duration', ''))
    def vthumb(it, i, big=False):
        if it['thumb']:
            inner = f'<img src="{it["thumb"]}" alt="">'
        elif it['kind'] == 'file':
            inner = f'<video src="{it["src"]}" muted playsinline preload="metadata"></video>'
        else:
            inner = scene(19 + i)
        lab = f'▶ {it["chapter"]} · {it["duration"]}' if big else ''
        return f'<div class="ph{" player" if big else ""}" style="--ar:{"16/9" if big else "16/10"}" {"id=player" if big else ""}>{inner}<span class="play{"" if big else " sm"}"></span>{f"<span class=lab>{e(lab)}</span>" if lab else ""}</div>'
    first = items[0] if items else dict(kind='none', thumb='', chapter='', duration='', title='')
    chapters = []
    for it in items:
        if it['chapter'] not in chapters:
            chapters.append(it['chapter'])
    tabs = ''.join(f'<button class="{"on" if i == 0 else ""}" data-chapter="{e(c)}">{e(c)}</button>' for i, c in enumerate(chapters))
    thumbs = ''.join(f'<button class="{"on" if i == 0 else ""}" data-i="{i}">{vthumb(it, i)}<div class="cap">{e(it["chapter"])} · {e(it["duration"])}</div></button>' for i, it in enumerate(items))
    tiles = [('Age', f"{2026 - h['year']} years ({h['year']})"), ('Sex', h['sex']), ('Breeding', h['breeding'].replace('Clydesdale', 'Clyde').replace('Thoroughbred', 'TB')),
             ('Height', h['height'] + (f" · maturing {h['mature_height']}" if h.get('mature_height') else '')), ('Training', h.get('training_time', '')), ('Disciplines', ' & '.join(h.get('disciplines', [])[:2]))]
    checks = ''.join(f'<div class="chk"><i>✓</i>{e(x)}</div>' for x in h.get('training', []))
    buying = ''.join(f'<div class="tile" style="background:var(--surf)"><div class="v" style="font-size:15px">{e(a)}</div><div class="muted" style="font-size:13px;margin-top:3px">{e(b)}</div></div>' for a, b in S['buying'][:4])
    others = [x for x in H if x['slug'] != h['slug'] and x['status'] != 'sold'][:3]
    cur = f'<span class="muted" style="font-size:13px">{h.get("currency", "")}</span>' if h.get('price_display') != 'request' and h.get('price') else ''
    data = json.dumps(items)
    fb_cap = f"Meet {h['name']}! Our {h['year']} {h['breeding'].replace('½ ', '').replace(' · ', ' × ')} {h['sex'].lower()}. Watch the videos and get the details:"
    body = f'''<div class="wrap"><div class="crumb"><a href="../">Available horses</a> / <span style="color:var(--ink)">{e(h['name'])}</span> {'<span class="sample" style="margin-left:10px">Sample listing</span>' if h.get('sample') else ''}</div>
<div class="listing"><div>{vthumb(first, 0, True)}<div class="tabs">{tabs}</div><div class="thumbs">{thumbs}</div>
<div class="mob-sum"><div class="row-top"><span class="chip st-{h['status']}">● {STATUS[h['status']]}</span></div><h1 style="font-size:38px;margin-top:10px">{e(h['name'])}</h1><div class="muted">{h['year']} {h['sex']} · {e(h['height'])}</div>
<div class="big-price" style="margin-top:10px"><span class="serif">{price(h)}</span>{cur}</div><a class="btn b1 full" style="margin-top:14px" href="#ask">Inquire about {e(h['name'])} →</a></div>
<h2 class="sec-h" style="font-size:34px">About {e(h['name'])}</h2><div class="rule"></div><p class="lede">{e(h['summary'])}</p><p class="muted" style="margin-top:12px">{e(h.get('notes', ''))}</p>
<h3 class="sec-h">Training &amp; experience</h3><div class="checks">{checks}</div>
<h3 class="sec-h">Pedigree</h3><div class="two"><div class="tile" style="background:var(--surf)"><div class="k">Sire</div><div class="v">{e(h.get('sire', ''))}</div></div><div class="tile" style="background:var(--surf)"><div class="k">Dam</div><div class="v">{e(h.get('dam', ''))}</div></div></div>
<h3 class="sec-h">Buying from Oak Creek</h3><div class="two">{buying}</div></div>
<aside class="panel"><div class="card"><div class="row-top"><span class="chip st-{h['status']}">● {STATUS[h['status']]}</span><span class="muted" style="font-size:12.5px">Listed {h.get('listed', '')}</span></div>
<h1>{e(h['name'])}</h1><div class="muted">{h['year']} {h['sex']} · Clydesdale × Thoroughbred</div>
<div class="big-price"><span class="serif">{price(h)}</span>{cur}</div>
<div class="tiles">{''.join(f'<div class="tile"><div class="k">{a}</div><div class="v">{e(b)}</div></div>' for a, b in tiles)}</div>
<a class="btn b1 full" style="margin-top:22px;padding:16px" href="#ask">Inquire about {e(h['name'])} →</a>
<a class="btn b2 full" style="margin-top:10px;color:var(--green)" href="{pre}visit/?horse={h['slug']}">Book a visit or video call</a>
<div class="share"><button data-share="fb">Share on Facebook</button><button data-share="copy">Copy link</button></div></div>
<div class="card" id="ask" style="padding:22px;margin-top:16px"><b style="font-weight:600">Ask about {e(h['name'])}</b>
<form data-form="inquiry"><input type="hidden" name="horse" value="{e(h['name'])}"><input required placeholder="Name" style="margin-top:12px"><input required placeholder="Email or phone" style="margin-top:8px">
<textarea rows="3" style="margin-top:8px">Hi Aidan, I'm interested in {e(h['name'])}. </textarea><button class="btn b2" style="margin-top:10px;color:var(--green)">Send</button>
<div class="ok">Thanks! Aidan will get back to you about {e(h['name'])} soon.</div></form></div></aside></div>
<section style="padding-bottom:0"><h2>You might also like</h2><div class="grid3" style="margin-top:24px">{''.join(hcard(x, i + 30, pre) for i, x in enumerate(others))}</div></section></div>
<script>window.VIDEOS={data};window.FB_CAPTION={json.dumps(fb_cap)};</script>'''
    return page(f"{h['name']} · {h['year']} Clydesdale × Thoroughbred {h['sex']} · {S['name']}", body, pre, on='horses/', desc=h['summary'],
                og_img=h['photo'] if exists(h.get('photo')) else '', path=f"horses/{h['slug']}/")

def story():
    pre = '../'
    paras = ''.join(f'<p class="lede" style="margin-top:16px">{e(p)}</p>' for p in S['story_long'])
    buying = ''.join(f'<div class="tile" style="background:var(--surf);padding:20px"><div class="v">{e(a)}</div><div class="muted" style="font-size:14px;margin-top:4px">{e(b)}</div></div>' for a, b in S['buying'])
    body = f'''<div class="wrap page-head"><div class="kick">Our story</div><h1 style="margin-top:8px">A small herd, raised the slow way</h1></div>
<section style="padding-top:30px"><div class="wrap split">{media('assets/img/story.jpg', 'Aidan with the herd', '4/5', seed=11, pre=pre)}<div>{paras}</div></div></section>
<section class="dark"><div class="wrap split"><div><div class="kick">The cross</div><h2 style="margin-top:10px">Why Clydesdale × Thoroughbred</h2><div class="rule"></div>
<p class="muted lede">The Clydesdale brings bone, substance and a famously kind, sensible mind. The Thoroughbred brings athleticism, stamina and a lighter, more forward way of going. Together they make a sport horse with presence and a steady temperament, suited to riders who want a horse that can do a bit of everything.</p></div>
{media('assets/img/cross.jpg', 'Photo · the cross', '4/3', seed=3, pre=pre)}</div></section>
<section id="buying"><div class="wrap"><div class="kick">Buying from Oak Creek</div><h2 style="margin-top:8px">How buying a horse works</h2>
<div class="grid3" style="margin-top:26px">{buying}</div><p style="margin-top:30px"><a class="btn b1" href="../horses/">See available horses</a></p></div></section>'''
    return page(f"Our Story · {S['name']}", body, pre, on='story/')

def graduates():
    pre = '../'
    sold = [h for h in H if h['status'] == 'sold']
    gl = ''.join(f'<div class="card">{media(g["photo"], "Owner photo", "4/3", seed=i+13, pre=pre)}<div class="body"><h3 style="font-size:22px;margin-top:0">{e(g["name"])}</h3><div class="meta">{e(g["home"])} · {e(g["discipline"])}</div><p class="muted" style="margin-top:10px;font-size:14.5px">“{e(g["note"])}”</p></div></div>' for i, g in enumerate(S['graduates']))
    gl += ''.join(hcard(h, i + 40, pre) for i, h in enumerate(sold))
    body = f'''<div class="wrap page-head"><div class="kick">Graduates</div><h1 style="margin-top:8px">Where they are now</h1>
<p class="muted lede">Horses we've raised that have gone on to new homes. When a horse is marked sold, it moves here. Owners, send us your updates!</p>
<div class="grid3" style="margin-top:30px">{gl}</div></div>'''
    return page(f"Graduates · {S['name']}", body, pre, on='graduates/')

def visit():
    pre = '../'
    opts = ''.join(f'<option value="{e(h["name"])}">{e(h["name"])}</option>' for h in H if h['status'] != 'sold')
    contact = []
    if S['email']: contact.append(f'<a class="link" href="mailto:{S["email"]}">{e(S["email"])}</a>')
    if S['phone']: contact.append(f'<a class="link" href="tel:{S["phone"]}">{e(S["phone"])}</a>')
    body = f'''<div class="wrap page-head"><div class="kick">Visit &amp; inquire</div><h1 style="margin-top:8px">Come meet the herd</h1></div>
<section style="padding-top:30px"><div class="wrap contact"><div><p class="lede">Visits are by appointment. If you're too far away, we'll do a live video call: we'll show you the horse in the field, tacked up and under saddle, and answer every question.</p>
<div class="two" style="margin-top:26px"><div class="tile" style="background:var(--surf);padding:18px" id="call"><div class="v">Video call viewing</div><div class="muted" style="font-size:14px">Watch the horse live from anywhere.</div></div>
<div class="tile" style="background:var(--surf);padding:18px"><div class="v">Visit the ranch</div><div class="muted" style="font-size:14px">{e(S['location'])}. Directions sent when you book.</div></div></div>
<p style="margin-top:24px">{' · '.join(contact) if contact else '<span class="muted">Email and phone go here.</span>'}</p>
<div style="margin-top:26px">{media('assets/img/visit.jpg', 'Photo · the ranch', '16/10', seed=2, pre=pre)}</div></div>
<div class="formcard"><h3>Send an inquiry</h3><form data-form="visit"><div class="grid2"><div><label class="f">Name</label><input required></div><div><label class="f">Email or phone</label><input required></div></div>
<label class="f">Which horse?</label><select name="horse" id="horse-select"><option value="">General inquiry</option>{opts}</select>
<label class="f">I'd like to…</label><select><option>Ask a question</option><option>Book a visit</option><option>Book a video call</option></select>
<label class="f">Message</label><textarea rows="5" placeholder="Tell us about yourself, your riding and what you're looking for."></textarea>
<button class="btn b1 full" style="margin-top:16px">Send inquiry</button><div class="ok">Thank you! Aidan will be in touch shortly.</div></form></div></div></section>'''
    return page(f"Visit & Inquire · {S['name']}", body, pre, on='visit/')

def write(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(s)

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for d in ['assets/img', 'assets/video']:
        if os.path.exists(os.path.join(ROOT, d)):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(OUT, d), dirs_exist_ok=True)
    for f in ['favicon.png', 'apple-touch-icon.png']:
        shutil.copy(os.path.join(ROOT, f), OUT)
    shutil.copy(os.path.join(ROOT, 'src/style.css'), os.path.join(OUT, 'assets/style.css'))
    shutil.copy(os.path.join(ROOT, 'src/main.js'), os.path.join(OUT, 'assets/main.js'))
    write('index.html', home())
    write('horses/index.html', horses_index())
    for h in H:
        write(f"horses/{h['slug']}/index.html", horse_page(h))
    write('story/index.html', story())
    write('graduates/index.html', graduates())
    write('visit/index.html', visit())
    m = open(os.path.join(ROOT, 'src/manage.html')).read()
    write('manage/index.html', m.replace('{{REPO}}', S.get('repo', '')).replace('{{BRANCH}}', S.get('branch', 'main')))
    shutil.copytree(os.path.join(ROOT, 'content'), os.path.join(OUT, 'content'))
    open(os.path.join(OUT, '_headers'), 'w').write('/manage/*\n  X-Robots-Tag: noindex\n/assets/*\n  Cache-Control: public, max-age=86400\n')
    print('built', len(H), 'horses ->', OUT)

if __name__ == '__main__':
    main()
