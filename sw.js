/* Playbox offline cache.
 *
 * Playbox is delivered as a URL, not an app, so without this there is nothing
 * on the device and closing the browser out of range leaves you with nothing.
 *
 * Tested on the Fire tablet: this works in Silk from the adult profile, where
 * aeroplane mode opens Playbox exactly as normal. It does NOT rescue the
 * Amazon Kids browser, which refuses to open any page with no connection
 * before a service worker is ever consulted. The offline route there is a
 * home-screen shortcut from the adult profile.
 *
 * Two caches, deliberately:
 *
 *   SHELL - index.html, the manifest, the icons, the trace list. Versioned, so
 *           bumping VERSION throws the old app away and pulls a fresh one.
 *   ART   - the trace pictures. NOT versioned, because 2MB of drawings should
 *           not be re-downloaded every time a button moves in the app. The
 *           filenames never change once published, so a cached one is always
 *           correct.
 *
 * Bump VERSION when index.html changes in a way that must not be served stale.
 * Ordinary changes do not need it: the shell is stale-while-revalidate, so the
 * app updates itself one launch later without anyone thinking about it.
 */

var VERSION = 'v2';   /* v2: icons added to the shell */
var SHELL   = 'playbox-shell-' + VERSION;
var ART     = 'playbox-art';

/* Kept small on purpose. The whole point is that the app opens instantly with
   no network, and everything else can arrive later. */
var SHELL_URLS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './traces/traces.json',
  /* The home-screen shortcut is how this gets used offline on the Fire tablet,
     so the things that shortcut is made of belong in the offline copy too. */
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png'
];

self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(SHELL).then(function(c){
      /* addAll is all-or-nothing, and one 404 would leave the child with no
         offline app at all. Take whatever we can get instead. */
      return Promise.all(SHELL_URLS.map(function(u){
        return c.add(new Request(u, { cache: 'reload' }))['catch'](function(){});
      }));
    }).then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(names){
      return Promise.all(names.map(function(n){
        /* drop old shells, never the artwork */
        if(n.indexOf('playbox-shell-') === 0 && n !== SHELL) return caches['delete'](n);
        return null;
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

function isArt(url){
  return url.pathname.indexOf('/traces/') !== -1 && /\.(png|jpg|jpeg|webp|gif)$/i.test(url.pathname);
}

/* Cache first. A trace picture at a given filename is the same picture
   forever, so going to the network for it is pure waste. */
function artFirst(req){
  return caches.open(ART).then(function(c){
    return c.match(req).then(function(hit){
      if(hit) return hit;
      return fetch(req).then(function(res){
        if(res && res.ok) c.put(req, res.clone());
        return res;
      });
    });
  });
}

/* Serve what we have immediately, then quietly refresh it for next time.
   The app is therefore at most one launch behind, and never blocked on a
   slow or missing connection. */
function shellSWR(req){
  return caches.open(SHELL).then(function(c){
    return c.match(req).then(function(hit){
      /* Revalidate against the server rather than the browser's own HTTP
         cache. GitHub Pages sends max-age=600, and without this a push could
         sit unseen for ten minutes on top of the one-launch delay. */
      var fresh;
      try{ fresh = new Request(req.url, { cache: 'no-cache', credentials: 'same-origin' }); }
      catch(e){ fresh = req; }
      var net = fetch(fresh).then(function(res){
        if(res && res.ok) c.put(req, res.clone());
        return res;
      })['catch'](function(){
        return hit || Response.error();
      });
      return hit || net;
    });
  });
}

self.addEventListener('fetch', function(e){
  var req = e.request;
  if(req.method !== 'GET') return;

  var url;
  try{ url = new URL(req.url); }catch(err){ return; }
  if(url.origin !== self.location.origin) return;

  /* Escape hatch. There are no developer tools on a Fire tablet in Kids mode,
     so if a bad cache ever gets stuck there has to be a way out that a parent
     can type: add ?fresh=1 to the address. Everything is thrown away and the
     app is pulled down again. */
  if(url.searchParams && url.searchParams.get('fresh') !== null){
    e.respondWith(
      caches.keys()
        .then(function(ns){ return Promise.all(ns.map(function(n){ return caches['delete'](n); })); })
        .then(function(){ return self.registration.unregister(); })
        .then(function(){ return fetch(new Request('./index.html', { cache: 'reload' })); })
        ['catch'](function(){ return fetch(req); })
    );
    return;
  }

  if(isArt(url)){ e.respondWith(artFirst(req)); return; }

  /* A navigation offline must land on the app, not on the browser's
     dinosaur, even if the child typed a path we never cached. */
  if(req.mode === 'navigate'){
    e.respondWith(
      shellSWR(req)['catch'](function(){
        return caches.match('./index.html', { cacheName: SHELL })
          .then(function(h){ return h || Response.error(); });
      })
    );
    return;
  }

  e.respondWith(shellSWR(req));
});

/* ---------------------------------------------------------------------------
   Downloading every picture, on request.

   Runtime caching alone only saves the pictures a child already opened, which
   is no use for the journey they have not taken yet. The page sends the list
   and we walk it a few at a time, reporting progress so the grown-up can see
   something is happening.
--------------------------------------------------------------------------- */
function precacheArt(urls, port){
  var done = 0, failed = 0, total = urls.length, i = 0;
  var LANES = 6;              /* enough to saturate tablet wifi, not enough to stall it */

  function say(state){
    if(port) try{ port.postMessage({ state: state, done: done, failed: failed, total: total }); }catch(e){}
  }

  return caches.open(ART).then(function(c){
    function lane(){
      if(i >= urls.length) return Promise.resolve();
      var u = urls[i++];
      return c.match(u).then(function(hit){
        if(hit){ done++; say('progress'); return lane(); }
        return fetch(u, { cache: 'no-store' }).then(function(res){
          if(res && res.ok) return c.put(u, res.clone()).then(function(){ done++; });
          failed++;
        })['catch'](function(){ failed++; })
         .then(function(){ say('progress'); return lane(); });
      });
    }
    var lanes = [];
    for(var k = 0; k < LANES; k++) lanes.push(lane());
    return Promise.all(lanes);
  }).then(function(){ say('done'); });
}

self.addEventListener('message', function(e){
  var d = e.data || {};
  var port = e.ports && e.ports[0];

  if(d.cmd === 'precache-art'){
    e.waitUntil(precacheArt(d.urls || [], port));
    return;
  }

  if(d.cmd === 'art-status'){
    caches.open(ART).then(function(c){ return c.keys(); }).then(function(keys){
      if(port) port.postMessage({ state: 'status', cached: keys.length });
    });
    return;
  }

  if(d.cmd === 'drop-art'){
    e.waitUntil(caches['delete'](ART).then(function(){
      if(port) port.postMessage({ state: 'dropped' });
    }));
    return;
  }
});
