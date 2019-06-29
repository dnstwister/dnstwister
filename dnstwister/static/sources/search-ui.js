/* global Velocity */
var ui = (function () {
  var resolvedRowMap = {}

  var anchorElem = function (innerHtml, href, className) {
    var elem = document.createElement('a')
    elem.href = href
    elem.className = className || ''
    elem.insertAdjacentHTML('afterbegin', innerHtml)
    return elem
  }

  var updateProgress = function (identifiedCount, checkedCount, resolvedCount, usePercent) {
    var identifiedCountElem = document.getElementById('identified_count')
    var checkedCountElem = document.getElementById('checked_count')
    var resolvedCountElem = document.getElementById('resolved_count')

    if (identifiedCount > 0) {
      identifiedCountElem.innerHTML = identifiedCount
    }

    if (checkedCount > 0) {
      if (usePercent === true) {
        checkedCountElem.innerHTML = Math.round((checkedCount / identifiedCount) * 100) + '%'
      } else {
        checkedCountElem.innerHTML = checkedCount
      }
    }

    if (resolvedCount > 0) {
      resolvedCountElem.innerHTML = resolvedCount
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
    } else {
      if (document.getElementById('errored_report').clientHeight > 0) { // Visible.
        setTimeout(function () {
          document.getElementById('tab-1').click()
          ui.placeFooter()
        }, 1500)
      }
      Velocity(document.getElementById('errors_tab'), 'fadeOut', { duration: 500, delay: 1500 })
    }
  }

  var resolvedReportRowElem = function (domain, idnaEncodedDomain, encodedDomain) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var ipCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    var domainText = domain
    if (domain !== idnaEncodedDomain) {
      domainText += ' (' + idnaEncodedDomain + ')'
    }
    domainCellElem.appendChild(document.createTextNode(domainText))
    toolsCellElem.className = 'tools'

    toolsCellElem.appendChild(
      anchorElem('analyse', '/analyse/' + encodedDomain)
    )

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(ipCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row resolved'

    return rowElem
  }

  var erroredReportRowElem = function (domain, idnaEncodedDomain, encodedDomain) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    var domainText = domain
    if (domain !== idnaEncodedDomain) {
      domainText += ' (' + idnaEncodedDomain + ')'
    }
    domainCellElem.appendChild(document.createTextNode(domainText))
    toolsCellElem.className = 'tools'

    toolsCellElem.appendChild(
      anchorElem('retry', '/analyse/' + encodedDomain)
    )

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row errored'

    return rowElem
  }

  var unresolvedReportRowElem = function (domain, idnaEncodedDomain, encodedDomain) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    var domainText = domain
    if (domain !== idnaEncodedDomain) {
      domainText += ' (' + idnaEncodedDomain + ')'
    }
    domainCellElem.appendChild(document.createTextNode(domainText))
    toolsCellElem.className = 'tools'

    toolsCellElem.appendChild(
      anchorElem('buy', '/analyse/' + encodedDomain)
    )

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row unresolved'

    return rowElem
  }

  var addResolvedRow = function (reportElem, domain, idnaEncodedDomain, encodedDomain) {
    if (resolvedRowMap[domain] !== undefined) {
      return
    }

    var rowElem = resolvedReportRowElem(domain, idnaEncodedDomain, encodedDomain)
    resolvedRowMap[domain] = rowElem
    reportElem.appendChild(rowElem)
    ui.placeFooter()
  }

  var addErroredRow = function (reportElem, domain, idnaEncodedDomain, encodedDomain) {
    var rowElem = erroredReportRowElem(domain, idnaEncodedDomain, encodedDomain)
    reportElem.appendChild(rowElem)
    ui.placeFooter()
  }

  var addUnresolvedRow = function (reportElem, domain, idnaEncodedDomain, encodedDomain) {
    console.log('unresolved', domain, reportElem)
    var rowElem = unresolvedReportRowElem(domain, idnaEncodedDomain, encodedDomain)
    reportElem.appendChild(rowElem)
    ui.placeFooter()
  }

  var addARecordInfo = function (domain, ipText) {
    var row = resolvedRowMap[domain]
    var td = row.childNodes[1]
    td.appendChild(document.createTextNode(ipText))
    ui.placeFooter()
  }

  var placeFooter = function () {
    var contents = document.getElementsByClassName('tab-content')

    var visibleHeight = 0
    for (var i = 0; i < contents.length; i++) {
      var tabContents = contents[i]
      if (tabContents.clientHeight > 0) { // AKA it's visible.
        visibleHeight = tabContents.offsetHeight + tabContents.parentNode.offsetHeight + 20
        break
      }
    }

    var footer = document.getElementsByTagName('footer')[0]
    footer.style.marginTop = visibleHeight + 'px'
  }

  return {
    updateProgress: updateProgress,
    startProgressDots: startProgressDots,
    markProgressAsDone: markProgressAsDone,
    addResolvedRow: addResolvedRow,
    addUnresolvedRow: addUnresolvedRow,
    addErroredRow: addErroredRow,
    addARecordInfo: addARecordInfo,
    placeFooter: function () {
      setTimeout(function () {
        placeFooter()
      }, 1) // DOM positioning.
    }
  }
})()
