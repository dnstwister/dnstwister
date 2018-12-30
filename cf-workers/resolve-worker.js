/* globals fetch, addEventListener, Headers, Response */
// Route: https://dnstwister.report/api/ip2*
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const urlStart = 'https://cloudflare-dns.com/dns-query?type=A&ct=application/dns-json&name='

const jsonHeaders = new Headers([
  ['Content-Type', 'application/json'],
  ['Access-Control-Allow-Origin', '*']
])

async function handleRequest (request) {
  const parsedUrl = new URL(request.url)
  if (!parsedUrl.searchParams.has('pd')) {
    return new Response('Missing encoded domain parameter', { status: 403 })
  }

  let domain = parsedUrl.searchParams.get('pd')

  return fetch(urlStart + domain, { cf: { cacheTtl: 86400 } })
    .then(function (response) {
      if (response.ok) {
        return response.json()
      }
    })
    .then(function (data) {
      let response = {
        ip: false,
        error: false
      }
      if (data.Answer !== undefined && data.Answer.length > 0) {
        response.ip = data.Answer.find(function (element) {
          return element.type === 1
        }).data
      }
      return new Response(JSON.stringify(response), {
        headers: jsonHeaders
      })
    })
    .catch(function () {
      let response = {
        ip: null,
        error: true
      }
      return new Response(JSON.stringify(response), {
        headers: jsonHeaders
      })
    })
}
