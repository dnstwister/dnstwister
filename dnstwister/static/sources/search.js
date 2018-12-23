var resolve = function(domain, callback) {
    setTimeout(function() {
        callback('127.0.0.1');
    }, 1000);
}

var reportRowElem = function(domain, tweak, ip) {
    var rowElem = document.createElement('tr');
    var domainCellElem = document.createElement('td');
    var tweakCellElem = document.createElement('td');
    var ipCellElem = document.createElement('td');

    domainCellElem.appendChild(document.createTextNode(domain))
    tweakCellElem.appendChild(document.createTextNode(tweak))
    ipCellElem.appendChild(document.createTextNode(ip))

    rowElem.appendChild(domainCellElem);
    rowElem.appendChild(tweakCellElem)
    rowElem.appendChild(ipCellElem);

    return rowElem
}

var search = function(encoded_domain) {

    var foundCount = 0;
    var resolvedCount = 0;

    var foundCountElem = document.getElementById('discovered_count');
    var resolvedCountElem = document.getElementById('resolved_count');

    var report_elem = document.getElementById('report_target');

    jsonpipe.flow('/api/fuzz_chunked/' + encoded_domain, {
        'success': function(data) {
            foundCount += 1;
            foundCountElem.innerHTML = foundCount;
            resolve(data.domain, function(ip) {
                resolvedCount += 1;
                resolvedCountElem.innerHTML = resolvedCount;
                report_elem.appendChild(reportRowElem(data.domain, data.fuzzer, ip));
            });
        }
    });
}
