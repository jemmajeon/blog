// 안내서 렌더러: <body data-guide="./sadang.json"> 를 읽어 본문을 그린다. 형식은 assets/GUIDE_SCHEMA.md.
(function () {
  var root = document.getElementById("guide");
  var src = document.body.getAttribute("data-guide");
  var base = document.body.getAttribute("data-base") || "../";

  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function chip(text, tone) { return el("span", "chip" + (tone ? " " + tone : ""), text); }
  function today() { var d = new Date(); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function fmtDate(s) {
    if (!s) return "";
    var d = new Date(s + "T00:00:00");
    return (d.getMonth() + 1) + "월 " + d.getDate() + "일 (" + "일월화수목금토"[d.getDay()] + ")";
  }
  function mapLink(p, area) {
    return "https://map.naver.com/p/search/" + encodeURIComponent(p.name.replace(/\s*[\(（].*$/, "") + " " + (area || ""));
  }

  function place(p, i, area) {
    var c = el("article", "card place");
    var hd = el("div", "hd"); hd.append(el("span", "no", String(i + 1)));
    var h = el("h3", null, p.name); if (p.kind) h.append(el("span", "kind", p.kind)); hd.append(h); c.append(hd);
    if (p.tags && p.tags.length) { var t = el("div", "tags"); p.tags.forEach(function (x) { t.append(chip(x)); }); c.append(t); }
    var f = el("div", "facts");
    [["📍", p.address], ["⏰", p.hours], ["☎", p.phone]].forEach(function (r) { if (r[1]) f.append(el("div", null, r[0] + " " + r[1])); });
    if (p.price) f.append(el("div", "price", "💰 " + p.price));
    if (p.rating) f.append(el("div", null, "⭐ " + p.rating));
    if (f.childNodes.length) c.append(f);
    if (p.menu && p.menu.length) {
      var tb = el("table", "menu"); p.menu.forEach(function (m) { var tr = el("tr"); tr.append(el("td", null, m[0]), el("td", null, m[1] || "")); tb.append(tr); }); c.append(tb);
    }
    if (p.notes && p.notes.length) {
      var dl = el("dl", "notes"); p.notes.forEach(function (n) { dl.append(el("dt", null, n[0]), el("dd", null, n[1])); }); c.append(dl);
    }
    var links = el("div", "links");
    var ls = (p.links && p.links.length) ? p.links : [{label: "네이버지도", url: mapLink(p, area)}];
    ls.forEach(function (l) { var a = el("a", "btn", "↗ " + l.label); a.href = l.url; a.target = "_blank"; a.rel = "noopener"; a.setAttribute("data-place", p.name.slice(0, 60)); links.append(a); });
    c.append(links);
    return c;
  }

  function section(s, g) {
    var sec = el("section", "g-sec"); sec.id = s.id; sec.setAttribute("data-zone", "sec-" + s.id);
    sec.append(el("h2", null, s.title));
    if (s.intro) sec.append(el("p", "intro", s.intro));
    if (s.type === "places") { var w = el("div", "places"); (s.places || []).forEach(function (p, i) { w.append(place(p, i, g.area)); }); sec.append(w); }
    else if (s.type === "steps") {
      var ol = el("ol", "steps");
      (s.steps || []).forEach(function (st) { var li = el("li"); if (st.time) li.append(el("span", "t", st.time)); li.append(el("b", null, st.title)); if (st.text) li.append(el("p", null, st.text)); ol.append(li); });
      sec.append(ol);
    } else if (s.type === "picks") {
      var pw = el("div", "picks"); (s.items || []).forEach(function (it) { var d = el("div", "card pick"); d.append(el("b", null, it.title)); if (it.text) d.append(el("p", null, it.text)); pw.append(d); }); sec.append(pw);
    } else if (s.type === "table") {
      var wrap = el("div", "tablewrap"), tbl = el("table", "ctable"), tr = el("tr");
      (s.columns || []).forEach(function (h) { tr.append(el("th", null, h)); }); tbl.append(tr);
      (s.rows || []).forEach(function (r) { var row = el("tr"); r.forEach(function (v) { row.append(el("td", null, v)); }); tbl.append(row); });
      wrap.append(tbl); sec.append(wrap);
    } else {
      var ul = el("ul", "blist"); (s.items || []).forEach(function (x) { ul.append(el("li", null, x)); }); sec.append(ul);
    }
    return sec;
  }

  function render(g) {
    document.title = g.title + " — jemmajeon 블로그";
    if (window.jjTrack) window.jjTrack("view_guide", {guide: (src.match(/([\w-]+)\.json/) || [])[1] || src, guide_kind: g.kind || "", guide_area: g.area || ""});
    var past = g.date && g.date < today();
    var hero = el("header", "g-hero");
    var back = el("a", "back", "← 안내서 목록"); back.href = base; hero.append(back);
    hero.append(el("h1", null, g.title));
    if (g.subtitle) hero.append(el("p", "sub", g.subtitle));
    var meta = el("div", "meta");
    if (g.kind) meta.append(chip(g.kind, "accent"));
    if (g.date) meta.append(chip("📅 " + fmtDate(g.date) + (g.time ? " " + g.time : "")));
    if (g.area) meta.append(chip("📍 " + g.area));
    var n = (g.sections || []).reduce(function (a, s) { return a + (s.places ? s.places.length : 0); }, 0);
    if (n) meta.append(chip("🏠 " + n + "곳"));
    if (past) meta.append(chip("지난 안내", "past"));
    hero.append(meta);
    if (past) hero.append(el("p", "past-note", "이미 지난 모임의 안내예요. 영업시간·가격은 조사 당시 기준이니 다시 가실 땐 지도에서 확인해 주세요."));
    root.append(hero);

    if (g.summary && g.summary.length) {
      var gl = el("section", "card glance"); gl.append(el("h2", null, "한눈에"));
      var ul = el("ul"); g.summary.forEach(function (s) { ul.append(el("li", null, s)); }); gl.append(ul); root.append(gl);
    }
    var secs = g.sections || [];
    if (secs.length > 1) {
      var nav = el("nav", "secnav"), row = el("div", "row"); nav.setAttribute("aria-label", "섹션");
      secs.forEach(function (s) { var a = el("a", null, s.title); a.href = "#" + s.id; a.dataset.id = s.id; row.append(a); });
      nav.append(row); root.append(nav);
    }
    secs.forEach(function (s) { root.append(section(s, g)); });
    var foot = el("p", "g-foot", (g.source ? "조사 기준: " + g.source + " · " : "") + "가격·영업시간은 바뀔 수 있어요.");
    root.append(foot);

    // 지금 보고 있는 섹션을 상단 칩에 표시
    if ("IntersectionObserver" in window && secs.length > 1) {
      var links = root.querySelectorAll(".secnav a");
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) links.forEach(function (a) { var on = a.dataset.id === e.target.id; a.classList.toggle("on", on); if (on) a.scrollIntoView({block: "nearest", inline: "nearest"}); }); });
      }, {rootMargin: "-130px 0px -60% 0px"});
      secs.forEach(function (s) { var t = document.getElementById(s.id); if (t) io.observe(t); });
    }
  }

  fetch(src, {cache: "no-cache"}).then(function (r) { return r.json(); }).then(render).catch(function () {
    root.append(el("p", "empty", "안내서를 불러오지 못했어요. 새로고침해 주세요."));
  });
})();
