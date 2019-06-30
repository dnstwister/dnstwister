/* globals KV_A_RECORDS, fetch, addEventListener, Headers, Response */
// Routes:
//  * https://dnstwister.report/api/a*
//  * https://dnstwister.report/api/mx*
//
// Map caching namespace as KV_A_RECORDS
//
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event))
})

const cacheTime = 60 * 60 * 24 // 24 hours.
const urlStart = 'https://cloudflare-dns.com/dns-query?ct=application/dns-json&name='

const jsonHeaders = new Headers([
  ['Content-Type', 'application/json'],
  ['Access-Control-Allow-Origin', '*']
])

async function handleRequest (event) {
  const parsedUrl = new URL(event.request.url)
  if (!parsedUrl.searchParams.has('pd')) {
    return new Response('Missing encoded domain parameter', { status: 403 })
  }
  let domain = parsedUrl.searchParams.get('pd')

  const mode = parsedUrl.pathname.split('/').slice(-1)[0]
  if (mode === 'a') {
    return aRecord(event, domain)
  } else if (mode === 'mx') {
    return mxRecord(domain)
  }

  return new Response('', { status: 404 })
}

async function aRecord (event, domain) {
  const cachedRecord = await cachedA(domain)
  if (cachedRecord !== null) {
    const updated = new Date(cachedRecord.updated)
    const age = (new Date() - updated) / 1000
    if (age < cacheTime) {
      const response = {
        ip: cachedRecord.ip,
        error: false,
        when: cachedRecord.updated
      }
      return new Response(JSON.stringify(response), {
        headers: jsonHeaders
      })
    }
  }

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
        const ip = data.Answer.find(function (element) {
          return element.type === 1
        }).data
        response.ip = ip
        response.when = new Date()

        event.waitUntil(cacheA(event, domain, ip))
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

async function cachedA (domain) {
  const key = 'a-' + domain
  return KV_A_RECORDS.get(key, 'json')
}

function cacheA (event, domain, ip) {
  const key = 'a-' + domain
  const value = JSON.stringify({
    ip: ip,
    updated: new Date()
  })
  event.waitUntil(KV_A_RECORDS.put(key, value))
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
