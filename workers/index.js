/* globals addEventListener, Headers, Response */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const dns = require('dns');
let jsonHeaders = new Headers([['Content-Type', 'application/json']])

async function handleRequest (request) {
  console.log('request!')

  let response = {
    'hi': 'hello!'
  }

  return new Response(JSON.stringify(response), {
    headers: jsonHeaders,
    status: 200
  })
}
