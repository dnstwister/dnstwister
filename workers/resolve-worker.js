/* globals fetch, addEventListener, Headers, Response */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const jsonHeaders = new Headers([['Content-Type', 'application/json']])

async function handleRequest (request) {
  return fetch('https://dns.google.com/resolve?name=dnstwister.report')
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
