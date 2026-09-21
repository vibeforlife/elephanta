from pathlib import Path
import re, html, json, shutil

ROOT=Path('/mnt/data/elephanta-pwa')
SRC=Path('/mnt/data/Elephanta_Caves_COMPLETE_90_120_MINUTE_FINAL.txt')
text=SRC.read_text(encoding='utf-8')
lines=text.splitlines()
heading_re=re.compile(r'^\s*[A-Z][A-Z0-9’\- —:,.\'()]+\s*$')
# Identify headings conservatively: uppercase and at most 100 chars.
heads=[]
for i,l in enumerate(lines):
    s=l.strip()
    if s and len(s)<=100 and s==s.upper() and re.search('[A-Z]',s):
        heads.append((i,s))
# remove metadata headings before first PART and END markers; retain all PART and deep-dive headings
start_idx=next(i for i,(ln,h) in enumerate(heads) if h.startswith('PART ONE'))
# Map heading -> block text, preserving every line in the selected script.
blocks=[]
for n,(ln,h) in enumerate(heads):
    if n<start_idx: continue
    end=heads[n+1][0] if n+1<len(heads) else len(lines)
    content='\n'.join(lines[ln+1:end]).strip()
    blocks.append((h,content))
# Drop the tiny END/END-like markers but keep content around them.
blocks=[b for b in blocks if b[0] not in {'END'}]
by={h:c for h,c in blocks}
order=[h for h,c in blocks]

# Main tour groups. Each group is a contiguous range of original headings.
groups=[
('01','Ferry Landing & Gharapuri', ['PART ONE — BEFORE YOU REACH THE ISLAND','PART TWO — WHY IS IT CALLED ELEPHANTA?','PART THREE — THE QUESTION OF WHO BUILT IT','PART FOUR — THE SEA JOURNEY','PART FIVE — ARRIVING AT GHARAPURI','PART SIX — THE GEOLOGY OF THE TEMPLE']),
('02','Approaching Cave One', ['PART SEVEN — FIRST VIEW OF CAVE ONE','PART EIGHT — ENTERING THE DARKNESS','PART NINE — UNDERSTANDING THE SHAIVA WORLD']),
('03','Yogishvara — Shiva the Yogi', ['PART TEN — YOGISHVARA: SHIVA THE YOGI','PART ELEVEN — NATARAJA: SHIVA THE DANCER','PART TWELVE — THE CENTRAL AXIS']),
('04','The Trimurti — Sadashiva', ['PART THIRTEEN — SADASHIVA: THE GREAT THREE-FACED IMAGE','PART FOURTEEN — THE POSSIBLE HIDDEN FACES','PART FIFTEEN — THE DVARAPALAS']),
('05','Ardhanarishvara', ['PART SIXTEEN — ARDHANARISHVARA', "PART SEVENTEEN — PARVATI'S PRESENCE"]),
('06','Gangadhara — Shiva & the Ganges', ['PART EIGHTEEN — GANGADHARA: SHIVA AND THE GANGES']),
('07','Kalyanasundara — The Divine Wedding', ['PART NINETEEN — KALYANASUNDARA: THE DIVINE WEDDING']),
('08','Ravana Under Kailash', ['PART TWENTY — RAVANA UNDER KAILASH']),
('09','Andhakasuravadha', ['PART TWENTY-ONE — ANDHAKASURAVADHA']),
('10','The Linga Shrine & Temple Architecture', ['PART TWENTY-TWO — THE LINGA SHRINE','PART TWENTY-THREE — LOOKING AT THE CEILING','PART TWENTY-FOUR — THE CAVE AS THEOLOGY IN MOTION']),
('11','Damage, Artists & What Has Been Lost', ['PART TWENTY-FIVE — HOW MUCH OF THE ORIGINAL LOOK IS LOST?','PART TWENTY-SIX — WHY SADASHIVA STILL WORKS',"PART TWENTY-SEVEN — THE ARTISTS' PROBLEM"]),
('12','The Other Caves & Earlier Island', ['PART TWENTY-EIGHT — THE OTHER CAVES','PART TWENTY-NINE — THE EASTERN SIDE AND EARLIER HISTORY']),
('13','The Portuguese Period & Cannon', ['PART THIRTY — THE PORTUGUESE PERIOD','PART THIRTY-ONE — THE CANNON AND THE VIEW']),
('14','Elephanta & Ellora', ['PART THIRTY-TWO — ELEPHANTA AND ELLORA']),
('15','What to Photograph & Visual Game', ['PART THIRTY-THREE — WHAT YOU SHOULD PHOTOGRAPH','PART THIRTY-FOUR — A VISUAL GAME']),
('16','The Linga, Darkness & Mythic Characters', ['PART THIRTY-FIVE — WHY THE LINGA MATTERS','PART THIRTY-SIX — THE EXPERIENCE OF DARKNESS','PART THIRTY-SEVEN — THE MYTHOLOGICAL CHARACTERS','PART THIRTY-EIGHT — AVOIDING THE EASY STORIES']),
('17','Conservation & UNESCO', ['PART THIRTY-NINE — THE CONSERVATION STORY','PART FORTY — THE UNESCO STORY']),
('18','Final Circuit & Leaving the Island', ['PART FORTY-ONE — YOUR LAST CIRCUIT OF CAVE ONE','PART FORTY-TWO — THE MASTERPIECE TEST','PART FORTY-THREE — LEAVING THE CAVE','PART FORTY-FOUR — THE WALK DOWN','PART FORTY-FIVE — BEFORE THE FERRY','PART FORTY-SIX — THE RETURN JOURNEY','PART FORTY-SEVEN — WHAT YOU SHOULD REMEMBER','PART FORTY-EIGHT — THE FINAL LOOK','PART FORTY-NINE — FINAL THOUGHT']),
]
# Deep-dive optional pages.
deep_groups=[
('19','Deep Dive — History & Religious World',['THE DATE AND THE PATRON','THE ANONYMOUS SCULPTORS','LAKULISHA AND THE PASHUPATA WORLD']),
('20','Deep Dive — Shiva as a System of Contrasts',['SHIVA AS A SYSTEM OF CONTRASTS','GANGADHARA — THE LOGIC OF CONTROL','RAVANA — POWER WITHOUT HUMILITY','ARDHANARISHVARA — A PHILOSOPHICAL IDEA MADE PHYSICAL','KALYANASUNDARA — SHIVA THE HUSBAND','ANDHAKASURAVADHA — DESTRUCTION']),
('21','Deep Dive — Architecture, Light & Scale',['THE LINGA — THE SACRED CENTRE','THE PILLARS','THE CAVE AS A JOURNEY','THE IMPORTANCE OF LIGHT','THE IMPORTANCE OF SCALE',"WHY PHOTOGRAPHS DON'T FULLY WORK"]),
('22','Deep Dive — Conservation, Caves & Legacy',['CONSERVATION','THE OTHER CAVES','THE EARLIER ISLAND','THE PORTUGUESE PERIOD','ELEPHANTA AND ELLORA','THE ANONYMOUS MASTERPIECE','A FINAL VISUAL GAME','THE FINAL CIRCUIT','THE WALK BACK','THE FERRY HOME','FINAL TEN THINGS','FINAL WORD'])
]
groups += deep_groups

# Validate every selected heading exists and no PART content is accidentally omitted.
used=[]
for _,_,hs in groups:
    for h in hs:
        if h not in by:
            raise SystemExit(f'Missing heading: {h}')
        used.append(h)

# Build a source attribution page. Main pages keep image credits out of the narration DOM.
images={
 'trimurti':{
   'url':'https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Trimurti_Sadashiva_in_Cave_1_of_Elephanta_Cave.jpg/960px-Trimurti_Sadashiva_in_Cave_1_of_Elephanta_Cave.jpg',
   'credit':'Saankav — Wikimedia Commons — CC BY-SA 4.0',
   'source':'https://commons.wikimedia.org/wiki/File:Trimurti_Sadashiva_in_Cave_1_of_Elephanta_Cave.jpg'},
 'yogishvara':{
   'url':'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cd/Shiva_as_Yogishvara%2C_God_of_Yoga_%2849548559731%29.jpg/960px-Shiva_as_Yogishvara%2C_God_of_Yoga_%2849548559731%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Shiva_as_Yogishvara,_God_of_Yoga_(49548559731).jpg'},
 'nataraja':{
   'url':'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c4/Shiva_as_Nataraja%2C_God_of_dance_%2849548063363%29.jpg/960px-Shiva_as_Nataraja%2C_God_of_dance_%2849548063363%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Shiva_as_Nataraja,_God_of_dance_(49548063363).jpg'},
 'ardhanarishvara':{
   'url':'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Ardhanarishvara_%2849548598836%29.jpg/960px-Ardhanarishvara_%2849548598836%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Ardhanarishvara_(49548598836).jpg'},
 'gangadhara':{
   'url':'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/04/Shiva_bringing_River_Ganges_to_Earth_%2849548098753%29.jpg/960px-Shiva_bringing_River_Ganges_to_Earth_%2849548098753%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Shiva_bringing_River_Ganges_to_Earth_(49548098753).jpg'},
 'kalyanasundara':{
   'url':'https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Kalyanasundara%2C_the_wedding_of_Shiva_and_Parvati_%2849548100613%29.jpg/960px-Kalyanasundara%2C_the_wedding_of_Shiva_and_Parvati_%2849548100613%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Kalyanasundara,_the_wedding_of_Shiva_and_Parvati_(49548100613).jpg'},
 'ravana':{
   'url':'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/87/Ravana_shaking_Mount_Kailasha_%2849548821277%29.jpg/960px-Ravana_shaking_Mount_Kailasha_%2849548821277%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Ravana_shaking_Mount_Kailasha_(49548821277).jpg'},
 'andhaka':{
   'url':'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a3/Shiva_slaying_Andhaka_%2849548103593%29.jpg/960px-Shiva_slaying_Andhaka_%2849548103593%29.jpg',
   'credit':'Dinesh Valke — Wikimedia Commons — CC BY-SA 2.0',
   'source':'https://commons.wikimedia.org/wiki/File:Shiva_slaying_Andhaka_(49548103593).jpg'},
}
# images per page; use only when visually useful.
page_image={
'03':'yogishvara','04':'trimurti','05':'ardhanarishvara','06':'gangadhara','07':'kalyanasundara','08':'ravana','09':'andhaka'
}

# Convert script paragraphs into narration paragraphs; preserve wording.
def paras(s):
    return [p.strip() for p in re.split(r'\n\s*\n',s) if p.strip()]

out=ROOT
(out/'pages').mkdir(exist_ok=True)
for idx,(num,title,hs) in enumerate(groups):
    combined=[]
    for h in hs:
        combined.append(f"{h}\n{by[h]}")
    # Use hidden source headings in narration? We don't want Read Aloud to repeat PART labels.
    # Instead, strip the heading line and retain only prose.
    content=[]
    for h in hs:
        content.extend(paras(by[h]))
    title_slug=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
    fn=f'{num}-{title_slug}.html'
    prev=f'../{int(num)-1:02d}-'+re.sub(r'[^a-z0-9]+','-',groups[idx-1][1].lower()).strip('-')+'.html' if idx>0 else 'index.html'
    nxt=f'../{int(num)+1:02d}-'+re.sub(r'[^a-z0-9]+','-',groups[idx+1][1].lower()).strip('-')+'.html' if idx<len(groups)-1 else 'index.html'
    img=page_image.get(num)
    img_html=''
    if img:
        im=images[img]
        img_html=f'<div class="visual" aria-hidden="true"><img src="{im["url"]}" alt=""></div>'
    nav=f'''<nav class="nav" aria-label="Tour navigation">
      <a class="navbtn" href="{prev}">← Previous</a><a class="navbtn home" href="index.html">All Stops</a><a class="navbtn" href="{nxt}">Next →</a>
    </nav>'''
    phtml='\n'.join(f'<p>{html.escape(p)}</p>' for p in content)
    page=f'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#33291f"><link rel="manifest" href="../manifest.webmanifest"><link rel="icon" href="../assets/icons/favicon.png"><link rel="apple-touch-icon" href="../assets/icons/apple-touch-icon.png">
<title>{html.escape(title)} — Elephanta Guide</title><link rel="stylesheet" href="../styles.css">
</head><body><header><a class="brand" href="index.html"><img src="../assets/icons/icon-192.png" alt="" aria-hidden="true"><span>ELEPHANTA GUIDE</span></a></header>
<main class="page"><div class="kicker">STOP {num} {'· OPTIONAL DEEP DIVE' if int(num)>=19 else ''}</div><h1>{html.escape(title)}</h1>{img_html}<article class="narration" data-read-aloud>{phtml}</article>{nav}</main><script src="../app.js"></script></body></html>'''
    (out/'pages'/fn).write_text(page,encoding='utf-8')

# Home/index and visual index.
stops=[]
for num,title,hs in groups:
    fn=f'{num}-{re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-")}.html'
    stops.append((num,title,fn,int(num)>=19))
stop_cards=[]
for num,title,fn,deep in stops:
    badge='Deep Dive' if deep else f'Stop {num}'
    stop_cards.append(f'<a class="card" href="pages/{fn}"><span class="badge">{badge}</span><strong>{html.escape(title)}</strong><span class="chev">→</span></a>')

visuals=[]
for key,im in images.items():
    names={'trimurti':'The Trimurti — Sadashiva','yogishvara':'Yogishvara — Shiva the Yogi','nataraja':'Nataraja — Shiva the Dancer','ardhanarishvara':'Ardhanarishvara','gangadhara':'Gangadhara — Shiva and the Ganges','kalyanasundara':'Kalyanasundara — Shiva and Parvati','ravana':'Ravana and Mount Kailash','andhaka':'Andhakasuravadha'}
    # Link to relevant page.
    target={'trimurti':'04-the-trimurti-sadashiva.html','yogishvara':'03-yogishvara-shiva-the-yogi.html','nataraja':'03-yogishvara-shiva-the-yogi.html','ardhanarishvara':'05-ardhanarishvara.html','gangadhara':'06-gangadhara-shiva-the-ganges.html','kalyanasundara':'07-kalyanasundara-the-divine-wedding.html','ravana':'08-ravana-under-kailash.html','andhaka':'09-andhakasuravadha.html'}[key]
    visuals.append(f'<a class="visual-card" href="pages/{target}"><img src="{im["url"]}" alt="" aria-hidden="true"><span>{names[key]}</span></a>')

home=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#33291f"><meta name="description" content="A mobile audio walking guide to the Elephanta Caves at Gharapuri."><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="assets/icons/favicon.png"><link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png"><link rel="stylesheet" href="styles.css"><title>Elephanta Guide</title></head>
<body><header><a class="brand" href="index.html"><img src="assets/icons/icon-192.png" alt="" aria-hidden="true"><span>ELEPHANTA GUIDE</span></a></header><main class="home">
<section class="hero"><div class="hero-icon"><img src="assets/icons/icon-512.png" alt="" aria-hidden="true"></div><div><div class="kicker">GHARAPURI · MUMBAI</div><h1>Elephanta Caves</h1><p class="lead">A visual audio walking tour built for your phone.</p></div></section>
<section class="notice"><strong>How to use</strong><p>Open a stop in Microsoft Edge and use <strong>Read Aloud</strong>. Each stop is a separate page, so you can jump directly to the sculpture or place you are standing in front of.</p></section>
<div class="actions"><a class="primary" href="pages/01-ferry-landing-gharapuri.html">▶ Start the Walking Tour</a><a class="secondary" href="#stops">Choose a Stop</a></div>
<section id="stops"><div class="section-head"><h2>All Stops</h2><span>{len(stops)} pages</span></div><div class="cards">{''.join(stop_cards)}</div></section>
<section class="visual-index"><div class="section-head"><h2>Find a Sculpture</h2><span>Visual index</span></div><p class="muted">Tap a photograph to jump straight to its narration. The photographs contain no labels or text.</p><div class="visual-grid">{''.join(visuals)}</div></section>
<section class="notice small"><strong>Offline use</strong><p>After you first open the guide while connected, the PWA can cache the app shell and tour pages. The sculpture photographs are served from Wikimedia Commons and may need to be loaded once while online.</p></section>
<footer><a href="credits.html">Image &amp; source credits</a> · Elephanta Guide</footer>
</main><script src="app.js"></script></body></html>'''
(out/'index.html').write_text(home,encoding='utf-8')

# Credits page
credits=['<h1>Image &amp; Source Credits</h1><p>Visual photographs used in this guide are from Wikimedia Commons under the licenses listed below.</p>']
for key,im in images.items():
    credits.append(f'<p><strong>{html.escape(key.title())}</strong><br>{html.escape(im["credit"])}<br><a href="{im["source"]}">Wikimedia Commons source page</a></p>')
credits.append('<p><strong>Tour content:</strong> original guide script prepared for this project, using established archaeological and historical references including UNESCO and IGNCA materials. This app does not reproduce those sources verbatim.</p>')
(out/'credits.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="styles.css"><link rel="manifest" href="manifest.webmanifest"><title>Credits — Elephanta Guide</title></head><body><header><a class="brand" href="index.html"><img src="assets/icons/icon-192.png" alt="" aria-hidden="true"><span>ELEPHANTA GUIDE</span></a></header><main class="page credits">{''.join(credits)}<p><a class="navbtn" href="index.html">← Back to guide</a></p></main><script src="app.js"></script></body></html>''',encoding='utf-8')

# CSS
(out/'styles.css').write_text('''
:root{--bg:#f5f0e8;--paper:#fffdf9;--ink:#211d19;--muted:#766d62;--stone:#33291f;--accent:#9a5a2b;--line:#ded4c7;--soft:#eee4d7}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;font-size:18px;line-height:1.7}header{position:sticky;top:0;z-index:10;background:rgba(255,253,249,.96);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:10px 16px}.brand{display:inline-flex;align-items:center;gap:10px;color:var(--stone);text-decoration:none;font-weight:800;letter-spacing:.08em;font-size:14px}.brand img{width:38px;height:38px;border-radius:10px}.home,.page{max-width:820px;margin:auto;padding:22px 18px 60px}.hero{display:flex;gap:18px;align-items:center;padding:22px 0 14px}.hero-icon{width:112px;height:112px;flex:0 0 112px;border-radius:28px;overflow:hidden;box-shadow:0 12px 28px #33291f25}.hero-icon img{width:100%;height:100%;object-fit:cover}.kicker{font-size:12px;font-weight:800;letter-spacing:.12em;color:var(--accent);text-transform:uppercase}.hero h1{font-size:40px;line-height:1.05;margin:5px 0}.lead{margin:0;color:var(--muted);font-size:17px}.notice{background:var(--soft);border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:20px 0}.notice p{margin:5px 0 0}.notice.small{font-size:14px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0 28px}.primary,.secondary,.navbtn{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;border-radius:12px;padding:11px 15px;font-weight:750}.primary{background:var(--stone);color:#fff}.secondary,.navbtn{background:var(--paper);border:1px solid var(--line);color:var(--ink)}.section-head{display:flex;align-items:baseline;justify-content:space-between;margin:26px 0 10px}.section-head h2{margin:0;font-size:24px}.section-head span,.muted{color:var(--muted);font-size:14px}.cards{display:grid;gap:9px}.card{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:14px 15px;text-decoration:none;color:var(--ink)}.card strong{font-size:16px}.badge{font-size:11px;color:var(--accent);font-weight:800;letter-spacing:.06em;text-transform:uppercase}.chev{font-size:22px;color:var(--muted)}.visual-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.visual-card{background:var(--paper);border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--ink)}.visual-card img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}.visual-card span{display:block;padding:10px 12px;font-weight:700;font-size:14px}.page h1{font-size:36px;line-height:1.1;margin:6px 0 20px}.visual{margin:0 0 24px;border-radius:18px;overflow:hidden;background:#2e2924}.visual img{width:100%;max-height:480px;object-fit:cover;display:block}.narration{font-size:19px;line-height:1.75}.narration p{margin:0 0 17px}.nav{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:30px}.navbtn{font-size:14px;text-align:center;padding:12px 7px}.home{min-width:0}.credits a{color:var(--accent)}footer{margin-top:35px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}footer a{color:var(--accent)}@media(max-width:520px){body{font-size:17px}.hero h1{font-size:33px}.hero-icon{width:92px;height:92px;flex-basis:92px}.page h1{font-size:31px}.narration{font-size:18px}.visual-grid{grid-template-columns:1fr}.navbtn{font-size:13px}.card{grid-template-columns:auto 1fr auto}}
''',encoding='utf-8')

# JS: service worker registration and a tiny "keep reading" scroll helper.
(out/'app.js').write_text('''if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));}''',encoding='utf-8')
# service worker needs root-relative assets/pages because it lives at root.
(out/'sw.js').write_text('''const CACHE='elephanta-guide-v1';
const CORE=['./','./index.html','./credits.html','./styles.css','./app.js','./manifest.webmanifest','./assets/icons/icon-192.png','./assets/icons/icon-512.png','./assets/icons/apple-touch-icon.png','./assets/icons/favicon.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{const copy=r.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)); return r;}).catch(()=>caches.match('./index.html'))));
});
''',encoding='utf-8')

manifest={"name":"Elephanta Guide","short_name":"Elephanta","description":"A visual audio walking guide to the Elephanta Caves at Gharapuri.","start_url":"./","display":"standalone","background_color":"#f5f0e8","theme_color":"#33291f","orientation":"portrait-primary","icons":[{"src":"assets/icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},{"src":"assets/icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}],"categories":["travel","education"]}
(out/'manifest.webmanifest').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

# README with GitHub Pages deployment and local testing instructions.
(out/'README.md').write_text('''# Elephanta Guide\n\nA mobile-first PWA audio walking guide for the Elephanta Caves at Gharapuri.\n\n## Local test\n\nFrom this folder, run a local static server (for example `python3 -m http.server 8080`) and open `http://localhost:8080/`. Service workers require localhost or HTTPS.\n\n## GitHub Pages\n\nUpload the contents of this folder to the repository root, enable GitHub Pages for the branch/folder containing the site, and open the generated HTTPS Pages URL on Android. Use Edge Read Aloud on each stop page.\n\n## Design\n\n- Separate substantial tour pages with Previous / All Stops / Next navigation.\n- Visual sculpture index.\n- Photographs are decorative/visual only and carry no narration text.\n- PWA manifest + service worker.\n- Generated Trimurti-inspired app icon.\n- Wikimedia Commons images are credited in `credits.html`.\n''',encoding='utf-8')

# zip package
shutil.make_archive('/mnt/data/Elephanta_Guide_PWA','zip',ROOT)
print('Built',len(groups),'pages')
print('Zip:',Path('/mnt/data/Elephanta_Guide_PWA.zip').stat().st_size)
