self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("farmacia-cache").then((cache) => {
      return cache.addAll([
        "/",
        "/static/style.css",
        "/static/script.js",
        "/static/manifest.json"
      ]);
    })
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request);
    })
  );
});
