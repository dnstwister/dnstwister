/* global Velocity */
var ui = (function () {
  var reportShown = false
  var rowMap = {}

  var anchorElem = function (innerHtml, href, className) {
    var elem = document.createElement('a')
    elem.href = href
    elem.className = className || ''
    elem.insertAdjacentHTML('afterbegin', innerHtml)
    return elem
  }

  var updatedProgress = function (checkedCount, resolvedCount) {
    var checkedCountElem = document.getElementById('checked_count')
    var resolvedCountElem = document.getElementById('resolved_count')
    var reportTableElem = document.getElementById('main_report')

    if (checkedCount > 0) {
      checkedCountElem.innerHTML = checkedCount
    }

    if (resolvedCount > 0) {
      resolvedCountElem.innerHTML = resolvedCount
      if (reportShown === false) {
        reportShown = true
        reportTableElem.style.display = 'table'
      }
    }
  }

  var startProgressDots = function () {
    var searchDotsElem = document.getElementById('search_dots')

    return setInterval(function () {
      var dotsCount = (searchDotsElem.firstChild || []).length
      var nextDotsCount = (dotsCount + 1) % 4

      var newDots = ''
      for (var i = 0; i < nextDotsCount; i++) {
        newDots += '.'
      }
      searchDotsElem.innerHTML = newDots
    }, 350)
  }

  var markProgressAsDone = function (errorCount) {
    var progressElem = document.getElementsByClassName('search_progress')[0]
    progressElem.innerHTML = 'Done!'

    Velocity(document.getElementsByClassName('wip_text'), 'fadeOut', { duration: 500, delay: 250 })
    Velocity(progressElem, 'slideUp', { duration: 500, delay: 1500 })
    Velocity(document.getElementsByClassName('search_result'), { 'font-size': '130%' }, { duration: 500, delay: 1500 })

    if (errorCount > 0) {
      document.getElementById('errored_count').innerText = errorCount
      Velocity(document.getElementById('error_summary'), 'fadeIn', { duration: 500, delay: 1500 })
    }
  }

  var reportRowElem = function (domain, punyCodedDomain, encodedDomain) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var mxCellElem = document.createElement('td')
    var ipCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    var domainText = domain
    if (domain !== punyCodedDomain) {
      domainText += ' (' + punyCodedDomain + ')'
    }
    domainCellElem.appendChild(document.createTextNode(domainText))
    toolsCellElem.className = 'tools'

    toolsCellElem.appendChild(
      anchorElem('analyse', '/analyse/' + encodedDomain)
    )

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(ipCellElem)
    rowElem.appendChild(mxCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row resolved'

    return rowElem
  }

  var addResolvedRow = function (reportElem, domain, punyCodedDomain, encodedDomain) {
    if (rowMap[domain] !== undefined) {
      return
    }

    var rowElem = reportRowElem(domain, punyCodedDomain, encodedDomain)
    rowMap[domain] = rowElem
    reportElem.appendChild(rowElem)
  }

  var addARecordInfo = function (domain, ipText) {
    var row = rowMap[domain]
    var td = row.childNodes[1]
    td.appendChild(document.createTextNode(ipText))
  }

  return {
    updatedProgress: updatedProgress,
    startProgressDots: startProgressDots,
    markProgressAsDone: markProgressAsDone,
    addResolvedRow: addResolvedRow,
    addARecordInfo: addARecordInfo
  }
})()
