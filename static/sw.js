var staticCacheName = 'v2';


self.addEventListener('install', function(event){
	console.log('[ServiceWorker] Install');
	var filesToCache = [
		'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js',
		'/static/styles/cover.css',
		'/static/styles/hat32.png',
		'/static/index.html',
		'/',
		'/static/offline.html'
	];

	//function needs to be async so that it returns a promise
	//because waitUntil requires a promise as its parameter
	event.waitUntil(async function() {
		console.log('[ServiceWorker] opening cache named:' + staticCacheName);
		caches.open(staticCacheName).then(function(cache){
			return cache.addAll(filesToCache);
		})
	}());
});


self.addEventListener('activate', function(event){
	console.log('[ServiceWorker] Activate');
	event.waitUntil(
		caches.keys().then(function(cacheNames) {
			return Promise.all(
				cacheNames.filter(function(cacheName) {
					return cacheName != staticCacheName;
				}).map(function(cacheName) {
					console.log('[ServiceWorker] Removing old cache', cacheName);
					return caches.delete(cacheName);
					})
			);
		})
	);
});

self.addEventListener('fetch', function(event) {
	event.respondWith(
		fetch(event.request).then(function(response) {
			if (response.status == 404){
				return new Response("Whoops, not found");
			}
			return response;
		}).catch(function() {
			return new Response("Uh oh, that totally failed!");
		}));
	// event.respondWith(
	// 	fetch('/static/dr-evil.gif')
	// );
});



// self.addEventListener( 'fetch', (event)=>{
// 	let headers = new Headers();
// 	headers.append('cache-control', 'no-cache');
// 	headers.append( 'pragma', 'no-cache');
// 	var req = new Request('test-connectivity.html',{
// 		method: 'GET',
// 		mode: 'same-origin',
// 		headers: headers,
// 		redirect: 'manual' // let browser handle redirets
// 	});
// 	event.respondWith( fetch( req, {
// 		cache: 'no-store'
// 	}).then( function( response ) {
// 		return fetch(event.request)
// 	}).catch( function (err) {
// 		return new Response( '<div><h2>Uh oh that did not work</h2></div>', {
// 			headers:{
// 				'Content-type': 'text/html'
// 			}
// 		})
// 	}))
// });



// self.addEventListener('fetch', function(event) {
// 	console.log('[ServiceWorker] Fetch', event.request.url);
// 	event.respondWith(
// 		caches.match(event.request).then(function(response) {
// 			return response || fetch(event.request).then(function(response){
// 				return caches.open(staticCacheName).then(function(cache){
// 					cache.put(event.request, response.clone());
// 					return response;
// 				});
// 			});
// 		})
// 	);
// });