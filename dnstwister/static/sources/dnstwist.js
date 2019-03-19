/* globals tldjs */
var dnstwistjs = (function () {
  // https://wsvincent.com/javascript-array-range-function/
  var range = function (start, edge, step) {
    // If only 1 number passed make it the edge and 0 the start
    if (arguments.length === 1) {
      edge = start
      start = 0
    }

    // Validate edge/start
    edge = edge || 0
    step = step || 1

    // Create array of numbers, stopping before the edge
    var arr = []
    for (arr; (edge - start) * step > 0; start += step) {
      arr.push(start)
    }
    return arr
  }

  var longestPropertyLength = function (obj) {
    var longestLength = 0
    for (var srcChar in obj) {
      var length = obj[srcChar].length
      if (length > longestLength) {
        longestLength = length
      }
    }
    return longestLength
  }

  var homoglyphs = {
    'a': ['à', 'á', 'â', 'ã', 'ä', 'å', 'ɑ', 'а', 'ạ', 'ǎ', 'ă', 'ȧ', 'ӓ'],
    'b': ['d', 'lb', 'ib', 'ʙ', 'Ь', 'b̔', 'ɓ', 'Б'],
    'c': ['ϲ', 'с', 'ƈ', 'ċ', 'ć', 'ç'],
    'd': ['b', 'cl', 'dl', 'di', 'ԁ', 'ժ', 'ɗ', 'đ'],
    'e': ['é', 'ê', 'ë', 'ē', 'ĕ', 'ě', 'ė', 'е', 'ẹ', 'ę', 'є', 'ϵ', 'ҽ'],
    'f': ['Ϝ', 'ƒ', 'Ғ'],
    'g': ['q', 'ɢ', 'ɡ', 'Ԍ', 'Ԍ', 'ġ', 'ğ', 'ց', 'ǵ', 'ģ'],
    'h': ['lh', 'ih', 'һ', 'հ', 'Ꮒ', 'н'],
    'i': ['1', 'l', 'Ꭵ', 'í', 'ï', 'ı', 'ɩ', 'ι', 'ꙇ', 'ǐ', 'ĭ', 'ì'],
    'j': ['ј', 'ʝ', 'ϳ', 'ɉ'],
    'k': ['lk', 'ik', 'lc', 'κ', 'ⲕ', 'κ', '𝖐', '𝓴', '𝚔', '𝔨', '𝒌', '𝘬', '𝓀', '𝙠', '𝐤', '𝗄', '𝑘', '𝗸', '𝕜'],
    'l': ['1', 'i', 'ɫ', 'ł'],
    'm': ['n', 'nn', 'rn', 'rr', 'ṃ', 'ᴍ', 'м', 'ɱ'],
    'n': ['m', 'r', 'ń'],
    'o': ['0', 'ο', 'о', 'Օ', 'ȯ', 'ọ', 'ỏ', 'ơ', 'ó', 'ö', 'ӧ'],
    'p': ['ρ', 'р', 'ƿ', 'Ϸ', 'Þ'],
    'q': ['g', 'զ', 'ԛ', 'գ', 'ʠ'],
    'r': ['ʀ', 'Г', 'ᴦ', 'ɼ', 'ɽ'],
    's': ['Ⴝ', 'Ꮪ', 'ʂ', 'ś', 'ѕ'],
    't': ['τ', 'т', 'ţ'],
    'u': ['μ', 'υ', 'Ս', 'ս', 'ц', 'ᴜ', 'ǔ', 'ŭ'],
    'v': ['ѵ', 'ν', 'v̇'],
    'w': ['vv', 'ѡ', 'ա', 'ԝ'],
    'x': ['х', 'ҳ', 'ẋ'],
    'y': ['ʏ', 'γ', 'у', 'Ү', 'ý'],
    'z': ['ʐ', 'ż', 'ź', 'ʐ', 'ᴢ']
  }
  var longestHomoglyph = longestPropertyLength(homoglyphs)

  var keyboardLayouts = [
    // qwerty
    {
      '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
      'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
      'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
      'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
    },
    // qwertz
    {
      '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7zt5', '7': '8uz6', '8': '9iu7', '9': '0oi8', '0': 'po9',
      'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6zgfr5', 'z': '7uhgt6', 'u': '8ijhz7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
      'a': 'qwsy', 's': 'edxyaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'zhbvft', 'h': 'ujnbgz', 'j': 'ikmnhu', 'k': 'olmji', 'l': 'kop',
      'y': 'asx', 'x': 'ysdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
    },
    // azerty
    {
      '1': '2a', '2': '3za1', '3': '4ez2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7', '9': '0oi8', '0': 'po9',
      'a': '2zq1', 'z': '3esqa2', 'e': '4rdsz3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7', 'i': '9okju8', 'o': '0plki9', 'p': 'lo0m',
      'q': 'zswa', 's': 'edxwqz', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'iknhu', 'k': 'olji', 'l': 'kopm', 'm': 'lp',
      'w': 'sxq', 'x': 'wsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhj'
    }
  ]
  var totalLayouts = keyboardLayouts.length
  var longestSet = Math.max.apply(null, keyboardLayouts.map(function (kl) {
    return longestPropertyLength(kl)
  }))

  var vowels = 'aeiou'

  var tweaks = [
  ].concat(

    // Original
    function (d, i) {
      if (i === 0) {
        return d
      }
      return null
    }

  ).concat(

    // Addition
    range(97, 123).map(function (c) {
      return function (d, i) {
        if (i === d.length - 1) {
          return d + String.fromCharCode(c)
        }
        return null
      }
    })

  ).concat(

    // Bitsquatting
    range(8).map(function (m) {
      var mask = Math.pow(2, m)

      return function (d, i) {
        var newChar = d.charCodeAt(i) ^ mask
        if ((newChar >= 48 && newChar <= 57) || (newChar >= 97 && newChar <= 122) || newChar === 45) {
          return d.substr(0, i) + String.fromCharCode(newChar) + d.substr(i + 1)
        } else {
          return null
        }
      }
    })

  ).concat(

    // Homoglyph
    range(longestHomoglyph).map(function (m) {
      return function (d, i) {
        var h = homoglyphs[d[i]]
        if (h === undefined) {
          return null
        }

        var newChar = h[m]
        if (newChar === undefined) {
          return null
        }

        return d.substr(0, i) + newChar + d.substr(i + 1)
      }
    })

  ).concat(

    // Hyphenation
    function (d, i) {
      if (i === 0 || i === d.length) {
        return null
      }
      if (d[i] === '.' || d[i - 1] === '.' || d[i] === '-') {
        return null
      }
      return d.substr(0, i) + '-' + d.substr(i)
    }

  ).concat(

    // Insertion
    range(totalLayouts * longestSet * 2).map(function (l) {
      return function (d, i) {
        if (i === 0) {
          return null
        }

        var layoutIndex = l % totalLayouts
        var charIndex = Math.floor((l / totalLayouts) / 2)

        var keyboardSet = keyboardLayouts[layoutIndex][d[i]]
        if (keyboardSet === undefined) {
          return null
        }

        var insertedChar = keyboardSet[charIndex]
        if (insertedChar === undefined) {
          return null
        }

        if (l % 2 === 0) {
          return d.substr(0, i) + insertedChar + d[i] + d.substr(i + 1)
        } else {
          return d.substr(0, i) + d[i] + insertedChar + d.substr(i + 1)
        }
      }
    })

  ).concat(

    // Omission
    function (d, i) {
      return d.substr(0, i) + d.substr(i + 1)
    }

  ).concat(

    // Repetition
    function (d, i) {
      return d.substr(0, i) + d[i] + d.substr(i)
    }

  ).concat(

    // Replacement
    range(totalLayouts * longestSet).map(function (l) {
      return function (d, i) {
        var layoutIndex = l % totalLayouts
        var charIndex = Math.floor(l / totalLayouts)

        var keyboardSet = keyboardLayouts[layoutIndex][d[i]]
        if (keyboardSet === undefined) {
          return null
        }

        var replacedChar = keyboardSet[charIndex]
        if (replacedChar === undefined) {
          return null
        }

        return d.substr(0, i) + replacedChar + d.substr(i + 1)
      }
    })

  ).concat(

    // Sub-domain
    function (d, i) {
      if (i === 0 || i === d.length) {
        return null
      }
      if (d[i] === '.' || d[i - 1] === '.' || d[i] === '-' || d[i - 1] === '-') {
        return null
      }
      return d.substr(0, i) + '.' + d.substr(i)
    }

  ).concat(

    // Transposition
    function (d, i) {
      if (d[i] === d[i + 1] || d[i + 1] === undefined) {
        return null
      }
      return d.substr(0, i) + d[i + 1] + d[i] + d.substr(i + 2)
    }

  ).concat(

    // Vowel swap
    range(vowels.length).map(function (v) {
      return function (d, i) {
        var vowelIndex = v % vowels.length

        if (vowels.indexOf(d[i]) === -1 || vowels[vowelIndex] === d[i]) {
          return null
        }

        return d.substr(0, i) + vowels[vowelIndex] + d.substr(i + 1)
      }
    })

  ).concat(

    // Miscellaneous
    range(4).map(function (m) {
      return function (d, i) {
        if (i === 0) {
          if (m === 0) {
            if (d.substring(0, 4) !== 'www.') {
              return 'ww' + d
            }
            return null
          } else if (m === 1) {
            if (d.substring(0, 4) !== 'www.') {
              return 'www' + d
            }
            return null
          } else if (m === 2) {
            if (d.substring(0, 4) !== 'www.') {
              return 'www-' + d
            }
            return null
          } else if (m === 3) {
            return d + 'com'
          }
        }
        return null
      }
    })

  )

  // Return the domain and TLD as two array elements.
  var split = function (domain) {
    var tld = tldjs.getPublicSuffix(domain)
    return [domain.slice(0, domain.length - tld.length - 1), tld]
  }

  var tweak = function (domain, cursor) {
    var parts = split(domain)

    var subdomains = parts[0]
    var tld = parts[1]

    var funcIndex = cursor % tweaks.length
    var tweakFunc = tweaks[funcIndex]
    if (tweakFunc === undefined) {
      return null
    }

    var charIndex = Math.floor(cursor / tweaks.length)
    if (charIndex > (subdomains.length - 1)) {
      return null
    }

    var tweakedDomain = tweakFunc(subdomains, charIndex)
    if (tweakedDomain === null) {
      return tweak(domain, cursor + 1)
    }

    return {
      'domain': tweakedDomain + '.' + tld,
      'cursor': cursor
    }
  }

  return {
    tweak: tweak
  }
})()
