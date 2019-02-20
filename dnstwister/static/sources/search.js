/* globals dnstwistjs, punycode, ui, XMLHttpRequest */
var search = (function () {
  var idnaEncode = function (domain) {
    return punycode.toASCII(domain)
  }

  var hexEncode = function (str) {
    var hex = ''
    for (var i = 0; i < str.length; i++) {
      hex += '' + str.charCodeAt(i).toString(16)
    }
    return hex
  }

  var resolveA = function (idnaEncodedDomain, callback) {
    var request = new XMLHttpRequest()
    var url = 'https://dnstwister.report/api/a?pd=' + idnaEncodedDomain
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
    var checkedCount = 0
    var resolvedCount = 0
    var resolveQueue = []
    var cleaningUp = false
    var erroredA = []

    var reportElem = document.getElementById('report_target')

    var progressTimer = ui.startProgressDots()

    var resolveMomentarily = function () {
      // To give the UI thread a chance.
      setTimeout(function () {
        resolveNext()
      }, 10)
    }

    var resolveNext = function () {
      var nextDomain = resolveQueue.pop()
      if (nextDomain === undefined) {
        if (allIdentified === true) {
          if (cleaningUp === false) {
            cleaningUp = true
            clearInterval(progressTimer)
            ui.markProgressAsDone(erroredA.length)
          }
          return
        } else {
          // Due to queue exhaustion.
          resolveMomentarily()
          return
        }
      }

      var idnaEncodedDomain = idnaEncode(nextDomain)
      var hexEncodedDomain = hexEncode(idnaEncodedDomain)

      checkedCount += 1

      resolveA(idnaEncodedDomain, function (ip) {
        if (ip === null) {
          erroredA.push([nextDomain, idnaEncodedDomain])
        } else if (ip !== false) {
          resolvedCount += 1
          ui.addResolvedRow(reportElem, nextDomain, idnaEncodedDomain, hexEncodedDomain)
          ui.addARecordInfo(nextDomain, ip)
        }

        ui.updateProgress(identifiedCount, checkedCount, resolvedCount, allIdentified)
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
        ui.updateProgress(identifiedCount, checkedCount, resolvedCount, allIdentified)
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
