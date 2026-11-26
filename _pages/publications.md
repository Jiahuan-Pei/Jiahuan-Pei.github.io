---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% include base_path %}

{% if author.googlescholar %}
<p>You can also find my articles on <u><a href="{{ author.googlescholar }}" target="_blank">my Google Scholar profile</a></u>.</p>
{% endif %}

<div id="pub-loading" style="color:#888; margin:16px 0;">Loading publications…</div>
<div id="pub-error"   style="color:#c00; display:none;"></div>

<div id="pub-section-proceeding"><h2>Conference Papers</h2><ul class="pub-list" id="pub-proceeding"></ul></div>
<div id="pub-section-journal">   <h2>Journal Articles</h2><ul class="pub-list" id="pub-journal"></ul></div>
<div id="pub-section-arxiv">     <h2>arXiv Preprints</h2><ul class="pub-list" id="pub-arxiv"></ul></div>
<div id="pub-section-book">      <h2>Theses &amp; Books</h2><ul class="pub-list" id="pub-book"></ul></div>

<style>
.pub-list { list-style: none; padding: 0; margin: 0 0 8px; }
.pub-list li { margin-bottom: 8px; line-height: 1.5; }
.pub-list a { color: inherit; }
#pub-section-proceeding, #pub-section-journal,
#pub-section-arxiv, #pub-section-book { display: none; }
</style>

<script>
(function () {
  var HIGHLIGHT  = "Jiahuan Pei";
  var PUB_LINKS  = "/assets/js/pub_links.json";

  var CONF_KW  = ["proceedings","conference","workshop","symposium","acl","emnlp","naacl",
                  "coling","eacl","sigir","cikm","www","wsdm","ecir","aaai","ijcai",
                  "neurips","nips","icml","iclr","cvpr","iccv","eccv","acm","ieee",
                  "ntcir","nlpcc","findings","chi","uist","cscw","iui","assets"];
  var JOUR_KW  = ["journal","transactions","letters","review","magazine","frontiers",
                  "plos","nature","science","wiley","springer","inderscience","elsevier"];
  var ARXIV_KW = ["arxiv","preprint","corr"];
  var BOOK_KW  = ["thesis","dissertation"];

  function classify(venue, title) {
    var t = (venue + " " + title).toLowerCase();
    for (var k of ARXIV_KW) if (t.includes(k)) return "arxiv";
    for (var k of BOOK_KW)  if (t.includes(k)) return "book";
    for (var k of JOUR_KW)  if (t.includes(k)) return "journal";
    for (var k of CONF_KW)  if (t.includes(k)) return "proceeding";
    return "proceeding";
  }

  function formatAuthors(authors) {
    return authors.map(function(a) {
      var name = a.name || "";
      return name.toLowerCase().includes(HIGHLIGHT.toLowerCase())
        ? "<b>" + name + "</b>" : name;
    }).join(", ");
  }

  // Build a lookup map from pub_links.json: lowercase title → {code, data, demo}
  function buildOverrideMap(linkData) {
    var map = {};
    (linkData.papers || []).forEach(function(entry) {
      if (entry.title) map[entry.title.toLowerCase().trim()] = entry;
    });
    return map;
  }

  // Fetch code repo from Papers with Code by arXiv ID
  function fetchPwC(arxivId) {
    var url = "https://paperswithcode.com/api/v1/papers/?arxiv_id=" + arxivId;
    return fetch(url)
      .then(function(r) { return r.ok ? r.json() : null; })
      .then(function(data) {
        if (!data || !data.results || !data.results.length) return null;
        var paper = data.results[0];
        if (!paper.repository_url) return null;
        return paper.repository_url;
      })
      .catch(function() { return null; });
  }

  function renderPaper(p, overrides, pwcCode) {
    var title   = p.title || "Untitled";
    var year    = p.year  || "";
    var venue   = (p.venue || (p.journal && p.journal.name) || "").trim();
    var authors = formatAuthors(p.authors || []);
    var paperUrl = p.url || (p.externalIds && p.externalIds.DOI
                    ? "https://doi.org/" + p.externalIds.DOI : "");
    var arxivId  = p.externalIds && p.externalIds.ArXiv ? p.externalIds.ArXiv : "";
    var arxivUrl = arxivId ? "https://arxiv.org/abs/" + arxivId : "";

    var ov = overrides[title.toLowerCase().trim()] || {};
    var codeUrl = ov.code || pwcCode || "";
    var dataUrl = ov.data || "";
    var demoUrl = ov.demo || "";

    var kind = classify(venue, title);
    var venueClean = venue.replace(/^[Ii]n [Pp]roceedings of\s*/,"").replace(/^[Ii]n\s*/,"");

    var citation;
    if      (kind === "proceeding") citation = authors + ', "' + title + '." In Proceedings of ' + venueClean + ' (' + year + ').';
    else if (kind === "journal")    citation = authors + ', "' + title + '." ' + venueClean + ', ' + year + '.';
    else if (kind === "arxiv")      citation = authors + ', "' + title + '." arXiv, ' + year + '.';
    else                            citation = authors + ', "' + title + '." ' + venueClean + ', ' + year + '.';

    var links = "";
    if (paperUrl) links += ' <a href="' + paperUrl + '" target="_blank">[Paper]</a>';
    if (arxivUrl) links += ' <a href="' + arxivUrl + '" target="_blank">[arXiv]</a>';
    if (codeUrl)  links += ' <a href="' + codeUrl  + '" target="_blank">[Code]</a>';
    if (dataUrl)  links += ' <a href="' + dataUrl  + '" target="_blank">[Data]</a>';
    if (demoUrl)  links += ' <a href="' + demoUrl  + '" target="_blank">[Demo]</a>';

    return { kind: kind, year: year,
             html: "<li>" + citation + links + "</li>" };
  }

  var ssUrl = "/assets/js/publications.json";

  Promise.all([
    fetch(ssUrl).then(function(r) { return r.json(); }).then(function(d){ return {data: d.papers}; }),
    fetch(PUB_LINKS).then(function(r) { return r.ok ? r.json() : {papers:[]}; }).catch(function(){ return {papers:[]}; })
  ])
  .then(function(results) {
    var ssData    = results[0];
    var linksData = results[1];
    var overrides = buildOverrideMap(linksData);

    document.getElementById("pub-loading").style.display = "none";
    var papers = (ssData.data || []).slice().sort(function(a,b){ return (b.year||0)-(a.year||0); });

    // Fetch PwC code for all papers with arXiv IDs, then render
    var pwcPromises = papers.map(function(p) {
      var arxivId = p.externalIds && p.externalIds.ArXiv ? p.externalIds.ArXiv : null;
      var titleKey = (p.title || "").toLowerCase().trim();
      // Skip PwC fetch if we already have a manual code override
      if (!arxivId || (overrides[titleKey] && overrides[titleKey].code)) return Promise.resolve(null);
      return fetchPwC(arxivId);
    });

    Promise.all(pwcPromises).then(function(pwcCodes) {
      var buckets = { proceeding: [], journal: [], arxiv: [], book: [] };
      papers.forEach(function(p, i) {
        var r = renderPaper(p, overrides, pwcCodes[i]);
        if (buckets[r.kind]) buckets[r.kind].push(r.html);
      });

      ["proceeding","journal","arxiv","book"].forEach(function(k) {
        if (buckets[k].length) {
          document.getElementById("pub-" + k).innerHTML = buckets[k].join("");
          document.getElementById("pub-section-" + k).style.display = "";
        }
      });
    });
  })
  .catch(function(e) {
    document.getElementById("pub-loading").style.display = "none";
    var el = document.getElementById("pub-error");
    el.textContent = "Could not load publications. Please visit my Google Scholar profile.";
    el.style.display = "";
  });
})();
</script>
