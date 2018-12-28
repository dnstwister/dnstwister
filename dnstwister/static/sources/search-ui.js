/* global Velocity */
var ui = (function () {
  var reportShown = false

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

  var markProgressAsDone = function () {
    var progressElem = document.getElementsByClassName('search_progress')[0]
    progressElem.innerHTML = 'Done!'

    Velocity(document.getElementsByClassName('wip_text'), 'fadeOut', { duration: 500, delay: 250 })
    Velocity(progressElem, 'slideUp', { duration: 500, delay: 1500 })
    Velocity(document.getElementsByClassName('search_result'), { 'font-size': '150%' }, { duration: 500, delay: 1500 })
  }

  var reportRowElem = function (domain, encodedDomain, ipText, showTools) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var ipCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    domainCellElem.appendChild(document.createTextNode(domain))
    ipCellElem.appendChild(document.createTextNode(ipText))
    toolsCellElem.className = 'tools'

    if (showTools === true) {
      toolsCellElem.appendChild(
        anchorElem('analyse', '/analyse/' + encodedDomain)
      )
      toolsCellElem.appendChild(
        anchorElem('&#128270;', '/search?ed=' + encodedDomain, 'deep-search')
      )
    } else {
      toolsCellElem.insertAdjacentHTML('afterbegin', '&nbsp;')
    }

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(ipCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row resolved'

    return rowElem
  }

  var addErrorRow = function (reportElem, domain, encodedDomain) {
    reportElem.appendChild(
      reportRowElem(domain, encodedDomain, 'Error!', false)
    )
  }

  var addResolvedRow = function (reportElem, domain, encodedDomain, ip) {
    reportElem.appendChild(
      reportRowElem(domain, encodedDomain, ip, true)
    )
  }

  return {
    updatedProgress: updatedProgress,
    startProgressDots: startProgressDots,
    markProgressAsDone: markProgressAsDone,
    addErrorRow: addErrorRow,
    addResolvedRow: addResolvedRow
  }
})()
