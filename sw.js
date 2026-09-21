const CACHE='elephanta-guide-v1';
const REMOTE_IMAGES=[
"https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Trimurti_Sadashiva_in_Cave_1_of_Elephanta_Cave.jpg/960px-Trimurti_Sadashiva_in_Cave_1_of_Elephanta_Cave.jpg",
"https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cd/Shiva_as_Yogishvara%2C_God_of_Yoga_%2849548559731%29.jpg/960px-Shiva_as_Yogishvara%2C_God_of_Yoga_%2849548559731%29.jpg",
"https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c4/Shiva_as_Nataraja%2C_God_of_dance_%2849548063363%29.jpg/960px-Shiva_as_Nataraja%2C_God_of_dance_%2849548063363%29.jpg",
"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Ardhanarishvara_%2849548598836%29.jpg/960px-Ardhanarishvara_%2849548598836%29.jpg",
"https://thumb.wikimedia.org/wikipedia/commons/thumb/0/04/Shiva_bringing_River_Ganges_to_Earth_%2849548098753%29.jpg/960px-Shiva_bringing_River_Ganges_to_Earth_%2849548098753%29.jpg",
"https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Kalyanasundara%2C_the_wedding_of_Shiva_and_Parvati_%2849548100613%29.jpg/960px-Kalyanasundara%2C_the_wedding_of_Shiva_and_Parvati_%2849548100613%29.jpg",
"https://thumb.wikimedia.org/wikipedia/commons/thumb/8/87/Ravana_shaking_Mount_Kailasha_%2849548821277%29.jpg/960px-Ravana_shaking_Mount_Kailasha_%2849548821277%29.jpg",
"https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a3/Shiva_slaying_Andhaka_%2849548103593%29.jpg/960px-Shiva_slaying_Andhaka_%2849548103593%29.jpg"
];
const CORE=['./','./index.html','./credits.html','./styles.css','./app.js','./manifest.webmanifest','./assets/icons/icon-192.png','./assets/icons/icon-512.png','./assets/icons/apple-touch-icon.png','./assets/icons/favicon.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(async c=>{await c.addAll(CORE); await Promise.all(REMOTE_IMAGES.map(async u=>{try{const r=await fetch(u,{mode:'no-cors'}); if(r.ok||r.type==='opaque') await c.put(u,r);}catch(_){}})}).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{const copy=r.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)); return r;}).catch(()=>caches.match('./index.html'))));
});
