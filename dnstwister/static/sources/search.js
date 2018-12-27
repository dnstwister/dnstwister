var updatedProgress = function(checkedCount, resolvedCount) {

    var checkedCountElem = document.getElementById('checked_count');
    var resolvedCountElem = document.getElementById('resolved_count');

    if (checkedCount > 0) {
        checkedCountElem.innerHTML = checkedCount;
    }

    if (resolvedCount > 0) {
        resolvedCountElem.innerHTML = resolvedCount;
    }
}

var startProgressDots = function () {

    var searchDotsElem = document.getElementById('search_dots');

    return setInterval(function() {
        var dotsCount  = (searchDotsElem.firstChild || []).length;
        var nextDotsCount = (dotsCount + 1) % 4;

        var newDots = '';
        for(var i = 0; i < nextDotsCount; i++) {
            newDots += '.';
        }
        searchDotsElem.innerHTML = newDots;
    }, 350);
}

var markProgressAsDone = function () {
    var progressElem = document.getElementsByClassName('search_progress')[0];
    progressElem.innerHTML = 'Done!';

    Velocity(document.getElementsByClassName('wip_text'), 'fadeOut', { duration: 500, delay: 250 });
    Velocity(progressElem, 'slideUp', { duration: 500, delay: 1500 });
    Velocity(document.getElementsByClassName('search_result'), {'font-size': '150%'}, { duration: 500, delay: 1500 });
}

var resolve = function(encoded_domain, callback) {
    const request = new XMLHttpRequest();
    const url='/api/ip/' + encoded_domain;
    request.open("GET", url);
    request.send();
    request.onreadystatechange = (e) => {
        if(request.readyState === 4) {
            if(request.status === 200) {
                var responseText = request.responseText;
                var response = JSON.parse(responseText);
                if (response.error === false) {
                    callback(response.ip);
                }
                else {
                    callback(null);
                }
            }
            else {
                callback(null);
            }
        }
    }
}

var reportRowElem = function(domain, tweak, ipText, show) {
    var rowElem = document.createElement('tr');
    var domainCellElem = document.createElement('td');
    var tweakCellElem = document.createElement('td');
    var ipCellElem = document.createElement('td');

    domainCellElem.appendChild(document.createTextNode(domain));
    tweakCellElem.appendChild(document.createTextNode(tweak));
    ipCellElem.appendChild(document.createTextNode(ipText));

    rowElem.appendChild(domainCellElem);
    rowElem.appendChild(tweakCellElem);
    rowElem.appendChild(ipCellElem);

    rowElem.className = 'domain-row';
    if (show === true) {
        rowElem.className = 'resolved';
    }

    return rowElem;
}


var search = function(encoded_domain) {

    var checkedCount = 0;
    var resolvedCount = 0;
    var resolveQueue = [];
    var startedResolving = false;
    var allFound = false;
    var cleaningUp = false;

    var reportElem = document.getElementById('report_target');

    var progressTimer = startProgressDots();

    var resolveNext = function(queue) {
        var data = queue.pop();
        if (data === undefined) {
            if (allFound === true) {
                if (cleaningUp === false) {
                    cleaningUp = true;
                    clearInterval(progressTimer);
                    markProgressAsDone();
                }
                return;
            }
            else {
                // If queue exhausted, wait for more.
                setTimeout(function() {
                    resolveNext(queue);
                }, 1000);
                return;
            }
        }

        resolve(data.encode_domain, function(ip) {
            checkedCount += 1;
            updatedProgress(checkedCount, resolvedCount);

            if (ip === null) {
                reportElem.appendChild(
                    reportRowElem(data.domain, data.fuzzer, 'Error!', true)
                );
                resolveNext(queue);
                return;
            }
            else if (ip === false) {
                reportElem.appendChild(
                    reportRowElem(data.domain, data.fuzzer, 'None resolved', false)
                );
                resolveNext(queue);
                return;
            }

            resolvedCount += 1;
            updatedProgress(checkedCount, resolvedCount);
            reportElem.appendChild(
                reportRowElem(data.domain, data.fuzzer, ip, true)
            );

            resolveNext(queue);
        });
    }

    jsonpipe.flow('/api/fuzz_chunked/' + encoded_domain, {
        'success': function(data) {
            resolveQueue.push(data);

            if (startedResolving !== true) {
                startedResolving = true;
                for(var i = 0; i < 5; i++) {
                    setTimeout(function() {
                        resolveNext(resolveQueue);
                    }, 500);
                }
            }
        },
        'complete': function() {
            allFound = true;
        }
    });
}
