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
<div id="pub-error" style="color:#c00; display:none;"></div>

<div id="pub-section-proceeding" style="display:none"><h2>Conference Papers</h2><ul class="pub-list" id="pub-proceeding"></ul></div>
<div id="pub-section-journal"   style="display:none"><h2>Journal Articles</h2><ul class="pub-list" id="pub-journal"></ul></div>
<div id="pub-section-arxiv"     style="display:none"><h2>arXiv Preprints</h2><ul class="pub-list" id="pub-arxiv"></ul></div>
<div id="pub-section-book"      style="display:none"><h2>Theses &amp; Books</h2><ul class="pub-list" id="pub-book"></ul></div>

<style>
.pub-list { list-style: none; padding: 0; margin: 0 0 8px; }
.pub-list li { margin-bottom: 8px; line-height: 1.5; }
</style>

<script>
(function () {
  var HIGHLIGHT = "Jiahuan Pei";
  var CSV_URL   = "/markdown_generator/citations.csv";

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

  function parseCSV(text) {
    var rows = [], cur = "", inQ = false, row = [];
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (c === '"') { inQ = !inQ; }
      else if (c === ',' && !inQ) { row.push(cur.trim()); cur = ""; }
      else if ((c === '\n' || c === '\r') && !inQ) {
        if (cur || row.length) { row.push(cur.trim()); rows.push(row); }
        cur = ""; row = [];
        if (c === '\r' && text[i+1] === '\n') i++;
      } else { cur += c; }
    }
    if (cur || row.length) { row.push(cur.trim()); rows.push(row); }
    return rows;
  }

  function parseAuthors(raw) {
    return raw.split(";").map(function(e) {
      e = e.trim().replace(/,$/, "");
      if (!e) return null;
      if (e.indexOf(",") !== -1) {
        var p = e.split(","); return (p[1]||"").trim() + " " + p[0].trim();
      }
      return e;
    }).filter(Boolean);
  }

  function formatAuthors(authors) {
    return authors.map(function(name) {
      return name.toLowerCase().includes(HIGHLIGHT.toLowerCase())
        ? "<b>" + name + "</b>" : name;
    }).join(", ");
  }

  fetch(CSV_URL)
    .then(function(r) { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(function(text) {
      var rows   = parseCSV(text);
      var header = rows[0].map(function(h){ return h.replace(/^﻿/,""); });
      var col    = {};
      header.forEach(function(h, i){ col[h] = i; });

      var papers = rows.slice(1).filter(function(r){ return r[col["Title"]]; });
      // Sort newest-first
      papers.sort(function(a, b){
        return (parseInt(b[col["Year"]])||0) - (parseInt(a[col["Year"]])||0);
      });

      var buckets = { proceeding:[], journal:[], arxiv:[], book:[] };

      papers.forEach(function(r) {
        var title   = r[col["Title"]]       || "";
        var venue   = r[col["Publication"]] || "";
        var year    = r[col["Year"]]        || "";
        var authors = formatAuthors(parseAuthors(r[col["Authors"]] || ""));
        var kind    = classify(venue, title);

        var v = venue.replace(/^[Ii]n [Pp]roceedings of\s*/,"").replace(/^[Ii]n\s*/,"");
        var citation;
        if      (kind==="proceeding") citation = authors+', "'+title+'." In Proceedings of '+v+' ('+year+').';
        else if (kind==="journal")    citation = authors+', "'+title+'." '+v+', '+year+'.';
        else if (kind==="arxiv")      citation = authors+', "'+title+'." arXiv, '+year+'.';
        else                          citation = authors+', "'+title+'." '+v+', '+year+'.';

        if (buckets[kind]) buckets[kind].push("<li>"+citation+"</li>");
      });

      document.getElementById("pub-loading").style.display = "none";
      ["proceeding","journal","arxiv","book"].forEach(function(k) {
        if (buckets[k].length) {
          document.getElementById("pub-"+k).innerHTML = buckets[k].join("");
          document.getElementById("pub-section-"+k).style.display = "";
        }
      });
    })
    .catch(function() {
      document.getElementById("pub-loading").style.display = "none";
      var el = document.getElementById("pub-error");
      el.textContent = "Could not load publications.";
      el.style.display = "";
    });
})();
</script>
