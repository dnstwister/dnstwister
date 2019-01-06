/* globals dnstwistjs, ui, XMLHttpRequest */
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

  var runSearch = function (domain) {
    var identified = []
    var allIdentified = false
    var identifiedCount = 0
    var resolvedCount = 0
    var resolveQueue = []
    var cleaningUp = false
    var unresolved = []
    var errored = []

    var reportElem = document.getElementById('report_target')

    var progressTimer = ui.startProgressDots()

    var resolveMomentarily = function () {
      // To give the UI thread a chance.
      setTimeout(function () {
        resolveNext()
      }, 10)
    }

    var resolveNext = function () {
      var next = resolveQueue.pop()
      if (next === undefined) {
        if (allIdentified === true) {
          if (cleaningUp === false) {
            cleaningUp = true
            clearInterval(progressTimer)
            ui.markProgressAsDone(errored.length)
          }
          return
        } else {
          resolveMomentarily()
          return
        }
      }

      var data = {
        'd': next,
        'pd': next
      }

      resolve(data.pd, function (ip) {
        if (ip === null) {
          errored.push([data.d, data.pd])
          resolveMomentarily()
          return
        } else if (ip === false) {
          unresolved.push([data.d, data.pd])
          resolveMomentarily()
          return
        }

        resolvedCount += 1
        ui.updatedProgress(identifiedCount, resolvedCount)
        ui.addResolvedRow(reportElem, data.d, data.pd, data.ed)
        ui.addARecordInfo(data.d, ip)

        resolveMomentarily()
      })
    }

    var findNext = function (cursor) {
      var result = dnstwistjs.tweak(domain, cursor)
      if (result === null) {
        allIdentified = true
        identified = null
        return
      }

      if (identified.indexOf(result.domain) === -1) {
        identified.push(result.domain)
        resolveQueue.push(result.domain)
        identifiedCount += 1
        ui.updatedProgress(identifiedCount, resolvedCount)
      }

      setTimeout(function () {
        findNext(result.cursor + 1)
      }, 1)
    }

    findNext(0)

    for (var i = 0; i < 10; i++) {
      setTimeout(function () {
        resolveNext()
      }, 100)
    }
  }
  return {
    run: runSearch
  }
})()
