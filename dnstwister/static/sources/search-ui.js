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

    if (errorCount === 0) {
      if (document.getElementById('errored_report').clientHeight > 0) { // Visible.
        setTimeout(function () {
          document.getElementById('tab-1').click()
          ui.placeFooter()
        }, 1500)
      }
      Velocity(document.getElementById('errors_tab'), 'fadeOut', { duration: 500, delay: 1500 })
    }
  }

  var resolvedReportRowElem = function (domain, idnaEncodedDomain, encodedDomain, mxFound, affiliateLink) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var ipCellElem = document.createElement('td')
    var mxCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    domainCellElem.appendChild(document.createTextNode(domain))
    if (domain !== idnaEncodedDomain) {
      var encodedSpan = document.createElement('span')
      encodedSpan.className = 'ed'
      encodedSpan.appendChild(document.createTextNode(' (' + idnaEncodedDomain + ')'))
      domainCellElem.appendChild(encodedSpan)
    }

    mxCellElem.className = 'mx'
    if (mxFound === true) {
      mxCellElem.className += ' found'
      mxCellElem.innerHTML = '&#x2714;'
      mxCellElem.className += ' found'
    } else {
      mxCellElem.innerHTML = '&#x2716;'
    }

    toolsCellElem.className = 'tools'
    toolsCellElem.appendChild(
      anchorElem('analyse', '/analyse/' + encodedDomain)
    )

    if (affiliateLink !== null) {
      var purchaseLink = anchorElem('for sale', affiliateLink)
      purchaseLink.className = 'affiliate button'
      purchaseLink.target = '_blank'
      toolsCellElem.appendChild(purchaseLink)
    }

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(ipCellElem)
    rowElem.appendChild(mxCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row resolved'

    return rowElem
  }

  var erroredReportRowElem = function (domain, idnaEncodedDomain, encodedDomain) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')

    domainCellElem.appendChild(document.createTextNode(domain))
    if (domain !== idnaEncodedDomain) {
      var encodedSpan = document.createElement('span')
      encodedSpan.className = 'ed'
      encodedSpan.appendChild(document.createTextNode(' (' + idnaEncodedDomain + ')'))
      domainCellElem.appendChild(encodedSpan)
    }

    rowElem.appendChild(domainCellElem)
    rowElem.className = 'domain-row errored'

    return rowElem
  }

  var unresolvedReportRowElem = function (domain, idnaEncodedDomain, mxFound, affiliateLink) {
    var rowElem = document.createElement('tr')
    var domainCellElem = document.createElement('td')
    var mxCellElem = document.createElement('td')
    var toolsCellElem = document.createElement('td')

    domainCellElem.appendChild(document.createTextNode(domain))
    if (domain !== idnaEncodedDomain) {
      var encodedSpan = document.createElement('span')
      encodedSpan.className = 'ed'
      encodedSpan.appendChild(document.createTextNode(' (' + idnaEncodedDomain + ')'))
      domainCellElem.appendChild(encodedSpan)
    }

    mxCellElem.className = 'mx'
    if (mxFound === true) {
      mxCellElem.className += ' found'
      mxCellElem.innerHTML = '&#x2714;'
      mxCellElem.title = 'Registering an MX record without an A record is often a sign of phishing.'
    } else {
      mxCellElem.innerHTML = '&#x2716;'
    }

    toolsCellElem.className = 'tools'

    if (affiliateLink !== null) {
      var purchaseLink = anchorElem('for sale', affiliateLink)
      purchaseLink.className = 'affiliate button'
      purchaseLink.target = '_blank'
      toolsCellElem.appendChild(purchaseLink)
    }

    rowElem.appendChild(domainCellElem)
    rowElem.appendChild(mxCellElem)
    rowElem.appendChild(toolsCellElem)
    rowElem.className = 'domain-row unresolved'

    return rowElem
  }

  var incrementCount = function (reportElem) {
    var tabElem = reportElem.parentNode.parentNode.parentNode
    var countElem = tabElem.getElementsByClassName('tab_count')[0]
    var count = parseInt(countElem.innerText)
    countElem.innerText = count + 1
  }

  var addResolvedRow = function (reportElem, domain, idnaEncodedDomain, encodedDomain, mxFound, affiliateLink) {
    if (resolvedRowMap[domain] !== undefined) {
      return
    }

    var rowElem = resolvedReportRowElem(domain, idnaEncodedDomain, encodedDomain, mxFound, affiliateLink)
    resolvedRowMap[domain] = rowElem
    if (affiliateLink !== null) {
      reportElem.insertBefore(rowElem, reportElem.childNodes[0] || null)
    } else {
      reportElem.appendChild(rowElem)
    }
    incrementCount(reportElem)
    ui.placeFooter()
  }

  var addErroredRow = function (reportElem, domain, idnaEncodedDomain, encodedDomain) {
    var rowElem = erroredReportRowElem(domain, idnaEncodedDomain, encodedDomain)
    reportElem.appendChild(rowElem)
    incrementCount(reportElem)
    ui.placeFooter()
  }

  var addUnresolvedRow = function (reportElem, domain, idnaEncodedDomain, mxFound, affiliateLink) {
    var rowElem = unresolvedReportRowElem(domain, idnaEncodedDomain, mxFound, affiliateLink)
    if (affiliateLink !== null || mxFound === true) {
      reportElem.insertBefore(rowElem, reportElem.childNodes[0] || null)
    } else {
      reportElem.appendChild(rowElem)
    }
    incrementCount(reportElem)
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
