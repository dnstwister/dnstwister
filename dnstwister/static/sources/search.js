/* globals jsonpipe, ui, XMLHttpRequest */
var search = (function () {
  var resolve = function (punyCodedDomain, callback) {
    var request = new XMLHttpRequest()
    var url = 'https://dnstwister.report/api/a?pd=' + punyCodedDomain
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
    var unresolved = []
    var errored = []

    var reportElem = document.getElementById('report_target')

    var progressTimer = ui.startProgressDots()

    var resolveNext = function (queue) {
      var data = queue.pop()
      if (data === undefined) {
        if (allFound === true) {
          if (cleaningUp === false) {
            cleaningUp = true
            clearInterval(progressTimer)
            ui.markProgressAsDone(errored.length)
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
          errored.push([data.d, data.pd])
          resolveNext(queue)
          return
        } else if (ip === false) {
          unresolved.push([data.d, data.pd])
          resolveNext(queue)
          return
        }

        resolvedCount += 1
        ui.updatedProgress(checkedCount, resolvedCount)
        ui.addResolvedRow(reportElem, data.d, data.pd, data.ed)
        ui.addARecordInfo(data.d, ip)
        resolveNext(queue)
      })
    }

    jsonpipe.flow('/api/fuzz_chunked/' + encodedDomain, {
      'success': function (data) {
        resolveQueue.push(data)

        if (startedResolving !== true) {
          startedResolving = true
          for (var i = 0; i < 10; i++) {
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
