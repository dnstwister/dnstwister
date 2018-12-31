/* globals fetch, addEventListener, Headers, Response */
// Routes:
//  * https://dnstwister.report/api/a*
//  * https://dnstwister.report/api/mx*
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const urlStart = 'https://cloudflare-dns.com/dns-query?ct=application/dns-json&name='

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

  const mode = parsedUrl.pathname.split('/').slice(-1)[0]
  if (mode === 'a') {
    return aRecord(domain)
  } else if (mode === 'mx') {
    return mxRecord(domain)
  }

  return new Response('', { status: 404 })
}

function aRecord (domain) {
  return fetch(urlStart + domain + '&type=A', { cf: { cacheTtl: 86400 } })
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

function mxRecord (domain) {
  return fetch(urlStart + domain + '&type=MX', { cf: { cacheTtl: 86400 } })
    .then(function (response) {
      if (response.ok) {
        return response.json()
      }
    })
    .then(function (data) {
      let response = { mx: false }
      if (data.Answer !== undefined && data.Answer.length > 0) {
        response.mx = data.Answer.find(function (element) {
          return element.type === 15
        }).data !== undefined
      }
      return new Response(JSON.stringify(response), {
        headers: jsonHeaders
      })
    })
    .catch(function () {
      let response = { mx: null }
      return new Response(JSON.stringify(response), {
        headers: jsonHeaders
      })
    })
}
