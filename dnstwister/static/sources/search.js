/* globals jsonpipe, ui, XMLHttpRequest */
var search = (function () {
  var resolve = function (punyCodedDomain, callback) {
    var request = new XMLHttpRequest()
    var url = 'https://dnstwister.report/api/ip2?pd=' + punyCodedDomain
    request.open('GET', url)
    request.send()
    request.onreadystatechange = (e) => {
      if (request.readyState === 4) {
        if (request.status === 200) {
          var responseText = request.responseText
          var response = JSON.parse(responseText)
          if (response.error === false) {
            callback(response.ip)
          } else {
            callback(null)
          }
        } else {
          callback(null)
        }
      }
    }
  }

  var runSearch = function (encodedDomain) {
    var seen = []
    var checkedCount = 0
    var resolvedCount = 0
    var resolveQueue = []
    var startedResolving = false
    var allFound = false
    var cleaningUp = false

    var reportElem = document.getElementById('report_target')

    var progressTimer = ui.startProgressDots()

    var resolveNext = function (queue) {
      var data = queue.pop()
      if (data === undefined) {
        if (allFound === true) {
          if (cleaningUp === false) {
            cleaningUp = true
            clearInterval(progressTimer)
            ui.markProgressAsDone()
          }
          return
        } else {
          // If queue exhausted, wait for more.
          setTimeout(function () {
            resolveNext(queue)
          }, 1000)
          return
        }
      }

      if (seen.indexOf(data.d) !== -1) {
        resolveNext(queue)
        return
      }

      seen.push(data.d)
      resolve(data.pd, function (ip) {
        checkedCount += 1
        ui.updatedProgress(checkedCount, resolvedCount)

        if (ip === null) {
          resolveNext(queue)
          return
        } else if (ip === false) {
          resolveNext(queue)
          return
        }

        resolvedCount += 1
        ui.updatedProgress(checkedCount, resolvedCount)
        ui.addResolvedRow(reportElem, data.d, data.pd, data.ed, ip)
        resolveNext(queue)
      })
    }

    jsonpipe.flow('/api/fuzz_chunked/' + encodedDomain, {
      'success': function (data) {
        resolveQueue.push(data)

        if (startedResolving !== true) {
          startedResolving = true
          for (var i = 0; i < 20; i++) {
            setTimeout(function () {
              resolveNext(resolveQueue)
            }, 500)
          }
        }
      },
      'complete': function () {
        allFound = true
      }
    })
  }

  return {
    run: runSearch
  }
})()
