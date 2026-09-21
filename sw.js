const CACHE_NAME = "elephanta-guide-v2";

const CORE_ASSETS = [
  "./",
  "./index.html",
  "./credits.html",
  "./styles.css",
  "./app.js",
  "./manifest.webmanifest",

  "./assets/icons/favicon.png",
  "./assets/icons/apple-touch-icon.png",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",

  "./assets/images/trimurti.jpg",
  "./assets/images/yogishvara.jpg",
  "./assets/images/nataraja.jpg",
  "./assets/images/ardhanarishvara.jpg",
  "./assets/images/gangadhara.jpg",
  "./assets/images/kalyanasundara.jpg",
  "./assets/images/ravana.jpg",
  "./assets/images/andhaka.jpg",

  "./pages/01-ferry-landing-gharapuri.html",
  "./pages/02-approaching-cave-one.html",
  "./pages/03-yogishvara-shiva-the-yogi.html",
  "./pages/04-nataraja-shiva-the-dancer.html",
  "./pages/05-the-trimurti-sadashiva.html",
  "./pages/06-ardhanarishvara.html",
  "./pages/07-gangadhara-shiva-the-ganges.html",
  "./pages/08-kalyanasundara-the-divine-wedding.html",
  "./pages/09-ravana-under-kailash.html",
  "./pages/10-andhakasuravadha.html",
  "./pages/11-the-linga-shrine-temple-architecture.html",
  "./pages/12-damage-artists-what-has-been-lost.html",
  "./pages/13-the-other-caves-earlier-island.html",
  "./pages/14-the-portuguese-period-cannon.html",
  "./pages/15-elephanta-ellora.html",
  "./pages/16-what-to-photograph-visual-game.html",
  "./pages/17-the-linga-darkness-mythic-characters.html",
  "./pages/18-conservation-unesco.html",
  "./pages/19-final-circuit-leaving-the-island.html",
  "./pages/20-deep-dive-history-religious-world.html",
  "./pages/21-deep-dive-shiva-as-a-system-of-contrasts.html",
  "./pages/22-deep-dive-architecture-light-scale.html",
  "./pages/23-deep-dive-conservation-caves-legacy.html"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys =>
        Promise.all(
          keys
            .filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
      .then(() =>
        self.clients.matchAll().then(clients => {
          clients.forEach(client => {
            client.postMessage({ type: "OFFLINE_READY" });
          });
        })
      )
  );
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) return cached;

        return fetch(event.request)
          .then(response => {
            if (response && response.ok) {
              const copy = response.clone();

              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, copy);
              });
            }

            return response;
          })
          .catch(() => {
            if (event.request.mode === "navigate") {
              return caches.match("./index.html");
            }

            return new Response(
              "",
              {
                status: 503,
                statusText: "Offline"
              }
            );
          });
      })
  );
});

self.addEventListener("message", event => {
  if (event.data && event.data.type === "GET_OFFLINE_STATUS") {
    event.source.postMessage({
      type: "OFFLINE_READY"
    });
  }
});
