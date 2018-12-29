/* globals fetch, addEventListener, Headers, Response */
// Route: https://dnstwister.report/api/ip2*
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const jsonHeaders = new Headers([['Content-Type', 'application/json']])

async function handleRequest (request) {
  const parsedUrl = new URL(request.url)
  if (!parsedUrl.searchParams.has('ed')) {
    return new Response('Missing encoded domain parameter', { status: 403 })
  }

  let domain = parsedUrl.searchParams.get('ed')

  return fetch('https://dns.google.com/resolve?name=' + domain)
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
        response.ip = data.Answer[0].data
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
