/* globals DOMAINS, addEventListener, Headers, Response */
// Route:
//        https://dnstwister.report/api/buy*
//
// Hit with request like:
//
//   https://dnstwister.report/api/buy?pd=[punycoded domain]
//
// Map KV Storage namespace as DOMAINS variable.
//
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event))
})

const jsonHeaders = new Headers([
  ['Content-Type', 'application/json'],
  ['Access-Control-Allow-Origin', '*']
])

async function handleRequest (event) {
  const parsedUrl = new URL(event.request.url)
  if (!parsedUrl.searchParams.has('pd')) {
    return new Response('Missing encoded domain parameter', { status: 403 })
  }

  const domainKey = parsedUrl.searchParams.get('pd')

  const availableFlag = await DOMAINS.get(domainKey)
  const response = JSON.stringify({
    'available': availableFlag !== null,
    'vendor': availableFlag
  })

  return new Response(response, { headers: jsonHeaders })
}
