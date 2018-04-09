if ('serviceWorker' in navigator) {
    window.addEventListener('load', function(){
      navigator.serviceWorker.register('../sw.js').then(function(registration){
      	console.log('[indexController] registration successful with scope: ', registration.scope);
      }).catch(function(error){
      	console.log('[indexController] registration failed' + error)
      });
    });
}

