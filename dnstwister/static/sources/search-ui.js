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

  var updateProgress = function (identifiedCount, checkedCount, resolvedCount, usePercent) {
    var identifiedCountElem = document.getElementById('identified_count')
    var checkedCountElem = document.getElementById('checked_count')
    var resolvedCountElem = document.getElementById('resolved_count')
    var reportTableElem = document.getElementById('main_report')

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

  var reportRowElem = function (domain, idnaEncodedDomain, encodedDomain) {
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

  var addResolvedRow = function (reportElem, domain, idnaEncodedDomain, encodedDomain) {
    if (rowMap[domain] !== undefined) {
      return
    }

    var rowElem = reportRowElem(domain, idnaEncodedDomain, encodedDomain)
    rowMap[domain] = rowElem
    reportElem.appendChild(rowElem)
    ui.placeFooter()
  }

  var addARecordInfo = function (domain, ipText) {
    var row = rowMap[domain]
    var td = row.childNodes[1]
    td.appendChild(document.createTextNode(ipText))
    ui.placeFooter()
  }

  var addUnresolvedARecord = function (domain) {
    var row = rowMap[domain]
    var td = row.childNodes[1]
    td.insertAdjacentHTML('afterbegin', '&#10006;')
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
    addARecordInfo: addARecordInfo,
    addUnresolvedARecord: addUnresolvedARecord,
    placeFooter: function () {
      setTimeout(function () {
        placeFooter()
      }, 1) // DOM positioning.
    }
  }
})()
