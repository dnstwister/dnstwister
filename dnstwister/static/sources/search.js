var resolve = function(encoded_domain, callback) {
    const request = new XMLHttpRequest();
    const url='/api/ip/' + encoded_domain;
    request.open("GET", url);
    request.send();
    request.onreadystatechange = (e) => {
        if(request.readyState === 4 && request.status === 200) {
            var responseText = request.responseText;
            var response = JSON.parse(responseText);
            if (response.error === false) {
                callback(response.ip);
            }
        }
    }
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
            resolve(data.encode_domain, function(ip) {
                resolvedCount += 1;
                resolvedCountElem.innerHTML = resolvedCount;
                report_elem.appendChild(reportRowElem(data.domain, data.fuzzer, ip));
            });
        }
    });
}
