// 안내서 렌더러: <body data-guide="./sadang.json"> 를 읽어 본문을 그린다. 형식은 assets/GUIDE_SCHEMA.md.
// 2026-11 개편: 메뉴 사진, 1인/4인 가격 상자, 후기 블록, 접는 메모, 상단 탭(tabs), 금액 막대(bars). 옛 JSON 도 그대로 그린다.
(function () {
  var root = document.getElementById("guide");
  var src = document.body.getAttribute("data-guide");
  var base = document.body.getAttribute("data-base") || "../";
  var IMGS = {};

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
  function photo(key, alt) {
    var im = IMGS[key]; if (!im || !im.src) return null;
    var i = el("img"); i.src = im.src; i.alt = alt || ""; i.loading = "lazy"; i.decoding = "async"; i.width = 960; i.height = 600;
    return i;
  }
  // notes 에서 라벨이 같은 항목을 꺼낸다 (꺼낸 항목은 '더 보기'에 다시 나오지 않음)
  function take(notes, label) {
    for (var k = 0; k < notes.length; k++) if (notes[k][0] === label) return notes.splice(k, 1)[0][1];
    return null;
  }

  // "1인 29,000원 / 4인 총 116,000원 (저녁, 주말)" → 1인, 4인 총, 덧붙임
  var PRICE = /^1인\s+((?:약\s*)?[\d,]+(?:-[\d,]+)?원)\s*\/\s*4인 총\s+((?:약\s*)?[\d,]+(?:-[\d,]+)?원)\s*(.*)$/;
  function priceBox(price) {
    var box = el("div", "pbox"), m = PRICE.exec(price || "");
    if (!m) { box.classList.add("raw"); box.append(el("b", null, price)); return box; }
    var a = el("div", "pp"); a.append(el("small", null, "1인"), el("b", null, m[1]));
    var b = el("div", "pt"); b.append(el("small", null, "4인 총액"), el("b", null, m[2]));
    box.append(a, b);
    var rest = m[3].replace(/^\((.*?)\)/, "$1").replace(/^,\s*/, "").trim();
    if (rest) box.append(el("p", "pnote", rest));
    return box;
  }
  function review(tone, title, text) {
    var d = el("div", "review" + (tone ? " " + tone : "")); d.append(el("b", null, title), el("p", null, text)); return d;
  }
  function notesList(notes) {
    var dl = el("dl", "notes"); notes.forEach(function (n) { dl.append(el("dt", null, n[0]), el("dd", null, n[1])); }); return dl;
  }

  function place(p, i, s, area) {
    var c = el("article", "card place");
    var im = photo(p.img || s.img, (p.kind || p.name) + " 참고 사진");
    if (im) { var ph = el("div", "ph"); ph.append(im, el("span", "ph-tag", "참고 이미지")); c.append(ph); }
    var bd = el("div", "bd");
    var hd = el("div", "hd"); hd.append(el("span", "no", String(i + 1)));
    var h = el("h3", null, p.name); if (p.kind) h.append(el("span", "kind", p.kind)); hd.append(h); bd.append(hd);
    if (p.price) bd.append(priceBox(p.price));
    if (p.tags && p.tags.length) { var t = el("div", "tags"); p.tags.forEach(function (x) { t.append(chip(x)); }); bd.append(t); }

    var notes = (p.notes || []).map(function (n) { return n.slice(); });
    var facts = el("ul", "facts");
    function fact(icon, text) { if (!text) return; var li = el("li"); li.append(el("span", "ic", icon), el("span", null, text)); facts.append(li); }
    fact("📍", p.address); fact("⏰", p.hours); fact("🅿️", take(notes, "주차")); fact("☎", p.phone);
    if (p.rating) fact("⭐", p.rating);
    if (facts.childNodes.length) bd.append(facts);

    var good = take(notes, "좋다는 후기"), bad = take(notes, "아쉽다는 후기"), rv = take(notes, "후기"), todo = take(notes, "확인 필요");
    if (good) bd.append(review("good", "👍 좋다는 후기", good));
    if (bad) bd.append(review("bad", "👎 아쉽다는 후기", bad));
    if (rv) bd.append(review("", "💬 후기", rv));
    if (todo) bd.append(el("p", "todo", "전화로 확인: " + todo));

    var hasMenu = p.menu && p.menu.length;
    if (hasMenu || notes.length > 2) {
      var det = el("details", "more"); det.append(el("summary", null, hasMenu ? "메뉴, 메모 더 보기" : "메모 더 보기"));
      if (hasMenu) { var tb = el("table", "menu"); p.menu.forEach(function (m) { var tr = el("tr"); tr.append(el("td", null, m[0]), el("td", null, m[1] || "")); tb.append(tr); }); det.append(tb); }
      if (notes.length) det.append(notesList(notes));
      bd.append(det);
    } else if (notes.length) bd.append(notesList(notes));

    var links = el("div", "links");
    var tel = (p.phone || "").match(/0\d{1,3}-\d{3,4}-\d{4}|1\d{3}-\d{4}/);
    if (tel) { var ta = el("a", "btn primary", "📞 전화"); ta.href = "tel:" + tel[0].replace(/-/g, ""); links.append(ta); }
    var ls = (p.links && p.links.length) ? p.links : [{label: "네이버지도", url: mapLink(p, area)}];
    ls.forEach(function (l) { var a = el("a", "btn", "↗ " + l.label); a.href = l.url; a.target = "_blank"; a.rel = "noopener"; a.setAttribute("data-place", p.name.slice(0, 60)); links.append(a); });
    bd.append(links);
    c.append(bd);
    return c;
  }

  function section(s, g) {
    var sec = el("section", "g-sec"); sec.id = s.id; sec.setAttribute("data-zone", "sec-" + s.id);
    sec.append(el("h2", null, s.title));
    if (s.intro) sec.append(el("p", "intro", s.intro));
    if (s.type === "places") { var w = el("div", "places"); (s.places || []).forEach(function (p, i) { w.append(place(p, i, s, g.area)); }); sec.append(w); }
    else if (s.type === "steps") {
      var ol = el("ol", "steps");
      (s.steps || []).forEach(function (st) { var li = el("li"); if (st.time) li.append(el("span", "t", st.time)); li.append(el("b", null, st.title)); if (st.text) li.append(el("p", null, st.text)); ol.append(li); });
      sec.append(ol);
    } else if (s.type === "picks") {
      var pw = el("div", "picks");
      (s.items || []).forEach(function (it, i) {
        var d = el("div", "card pick" + (i === 0 ? " top" : "")); d.append(el("span", "pn", String(i + 1)));
        var tx = el("div"); tx.append(el("b", null, it.title)); if (it.text) tx.append(el("p", null, it.text)); d.append(tx); pw.append(d);
      });
      sec.append(pw);
    } else if (s.type === "bars") {
      var vals = (s.items || []).filter(function (x) { return x.value; }).map(function (x) { return x.value; });
      var max = vals.length ? Math.max.apply(null, vals) : 1, bl = el("ol", "bars");
      (s.items || []).forEach(function (x) {
        var li = el("li", x.hl ? "hl" : null), top = el("div", "bl");
        top.append(el("span", "bn", x.label), el("span", "bv", x.text || "")); li.append(top);
        if (x.sub) li.append(el("span", "bs", x.sub));
        if (x.value) { var f = el("span", "bf"); f.style.width = Math.max(2, x.value / max * 100).toFixed(1) + "%"; li.append(f); }
        bl.append(li);
      });
      sec.append(bl);
    } else if (s.type === "table") {
      var wrap = el("div", "tablewrap"), tbl = el("table", "ctable"), tr = el("tr");
      (s.columns || []).forEach(function (h) { tr.append(el("th", null, h)); }); tbl.append(tr);
      (s.rows || []).forEach(function (r) { var row = el("tr"); r.forEach(function (v) { row.append(el("td", null, v)); }); tbl.append(row); });
      wrap.append(tbl); sec.append(wrap);
    } else {
      var ul = el("ul", "blist" + (s.style ? " " + s.style : "")); (s.items || []).forEach(function (x) { ul.append(el("li", null, x)); }); sec.append(ul);
    }
    return sec;
  }

  // 가로로 넘치는 칩/탭 줄에서 고른 칸을 가운데로 (페이지는 움직이지 않음)
  function centerIn(row, a) {
    var r = a.getBoundingClientRect(), rr = row.getBoundingClientRect();
    row.scrollBy({left: (r.left - rr.left) - (rr.width - r.width) / 2, behavior: "smooth"});
  }

  function render(g) {
    IMGS = g.images || {};
    document.title = g.title + " — jemmajeon 블로그";
    if (window.jjTrack) window.jjTrack("view_guide", {guide: (src.match(/([\w-]+)\.json/) || [])[1] || src, guide_kind: g.kind || "", guide_area: g.area || ""});
    var past = g.date && g.date < today();
    var hero = el("header", "g-hero");
    var back = el("a", "back", "← 안내서 목록"); back.href = base; hero.append(back);
    var h1 = el("h1", null, g.title), heroImg = g.hero && photo(g.hero, "");
    if (heroImg) { var fig = el("div", "hero-img"); fig.append(heroImg, h1); hero.append(fig); } else hero.append(h1);
    if (g.subtitle) hero.append(el("p", "sub", g.subtitle));
    var meta = el("div", "meta");
    if (g.kind) meta.append(chip(g.kind, "accent"));
    if (g.date) meta.append(chip("📅 " + fmtDate(g.date) + (g.time ? " " + g.time : "")));
    if (g.area) meta.append(chip("📍 " + g.area));
    var n = (g.sections || []).reduce(function (a, s) { return a + (s.places ? s.places.length : 0); }, 0);
    if (n) meta.append(chip("🏠 " + n + "곳"));
    if (past) meta.append(chip("지난 안내", "past"));
    hero.append(meta);
    if (past) hero.append(el("p", "past-note", "이미 지난 모임의 안내예요. 영업시간, 가격은 조사 당시 기준이니 다시 가실 땐 지도에서 확인해 주세요."));
    root.append(hero);

    if (g.summary && g.summary.length) {
      var gl = el("section", "card glance"); gl.append(el("h2", null, "한눈에"));
      var ul = el("ul"); g.summary.forEach(function (s) { ul.append(el("li", null, s)); }); gl.append(ul); root.append(gl);
    }
    var secs = g.sections || [];
    if (g.tabs && g.tabs.length) renderTabs(g, secs);
    else renderFlat(g, secs);

    var foot = el("div", "g-foot");
    foot.append(el("p", null, (g.source ? "조사 기준: " + g.source + ". " : "") + "가격, 영업시간은 바뀔 수 있어요."));
    var keys = Object.keys(IMGS).filter(function (k) { return IMGS[k].page; });
    if (keys.length) {
      var det = el("details", "credits"); det.append(el("summary", null, "사진 출처 (메뉴 참고 이미지, 실제 매장 사진 아님)"));
      var cl = el("ul");
      keys.forEach(function (k) {
        var im = IMGS[k], li = el("li"), a = el("a", null, im.title || k); a.href = im.page; a.target = "_blank"; a.rel = "noopener";
        li.append(a, document.createTextNode(", " + (im.artist ? im.artist + ", " : "") + (im.license || "") + ", 위키미디어 공용")); cl.append(li);
      });
      det.append(cl); foot.append(det);
    }
    root.append(foot);
  }

  // 탭 없는 안내서: 섹션을 차례로 + 상단 칩으로 지금 섹션 표시
  function renderFlat(g, secs) {
    if (secs.length > 1) {
      var nav = el("nav", "secnav"), row = el("div", "row"); nav.setAttribute("aria-label", "섹션");
      secs.forEach(function (s) { var a = el("a", null, s.title); a.href = "#" + s.id; a.dataset.id = s.id; row.append(a); });
      nav.append(row); root.append(nav);
    }
    secs.forEach(function (s) { root.append(section(s, g)); });
    if ("IntersectionObserver" in window && secs.length > 1) {
      var links = root.querySelectorAll(".secnav a"), navRow = root.querySelector(".secnav .row"), cur = null;
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting || e.target.id === cur) return;
          cur = e.target.id;
          links.forEach(function (a) { var on = a.dataset.id === cur; a.classList.toggle("on", on); if (on) centerIn(navRow, a); });
        });
      }, {rootMargin: "-130px 0px -60% 0px"});
      secs.forEach(function (s) { var t = document.getElementById(s.id); if (t) io.observe(t); });
    }
  }

  // 탭 안내서: 가로 탭 1단, 섹션이 여럿인 탭은 안에 바로가기(넓은 화면에선 왼쪽 세로 목록)
  function renderTabs(g, secs) {
    var byId = {}; secs.forEach(function (s) { byId[s.id] = s; });
    var nav = el("nav", "gtabs"), row = el("div", "row"); nav.setAttribute("aria-label", "안내서 탭"); row.setAttribute("role", "tablist");
    var used = {}, panels = [], btns = [];
    g.tabs.forEach(function (t) {
      var b = el("button", null, t.label); b.type = "button"; b.setAttribute("role", "tab"); b.dataset.tab = t.id;
      b.addEventListener("click", function () { open(t.id, true); });
      row.append(b); btns.push(b);
    });
    nav.append(row); root.append(nav);
    g.tabs.forEach(function (t) {
      var ss = (t.sections || []).map(function (id) { used[id] = 1; return byId[id]; }).filter(Boolean);
      var pn = el("div", "gpanel" + (ss.length > 2 ? " has-sub" : "")); pn.id = "tab-" + t.id; pn.setAttribute("role", "tabpanel"); pn.hidden = true;
      if (ss.length > 2) {
        var sub = el("nav", "subnav"); sub.setAttribute("aria-label", t.label + " 안 바로가기");
        ss.forEach(function (s) { var a = el("a", null, s.title); a.href = "#" + s.id; sub.append(a); });
        pn.append(sub);
      }
      var body = el("div", "gpbody"); ss.forEach(function (s) { body.append(section(s, g)); }); pn.append(body);
      root.append(pn); panels.push(pn);
    });
    secs.forEach(function (s) { if (!used[s.id]) root.append(section(s, g)); });

    function open(id, scroll) {
      panels.forEach(function (p) { p.hidden = p.id !== "tab-" + id; });
      btns.forEach(function (b) { var on = b.dataset.tab === id; b.setAttribute("aria-selected", on ? "true" : "false"); if (on) centerIn(row, b); });
      if (scroll) {
        var top = nav.getBoundingClientRect().top + window.scrollY - 56;
        if (window.scrollY > top) window.scrollTo(0, top);
        if (history.replaceState) history.replaceState(null, "", "#" + id);
      }
    }
    // 주소 끝 #탭 또는 #섹션 으로 들어오면 그 탭을 연다 (처음 열 때 + 같은 페이지에서 # 만 바뀔 때)
    function fromHash(initial) {
      var h = decodeURIComponent((location.hash || "").slice(1)), tab = initial ? g.tabs[0].id : null, target = null;
      g.tabs.forEach(function (t) { if (t.id === h) tab = t.id; else if ((t.sections || []).indexOf(h) >= 0) { tab = t.id; target = h; } });
      if (tab) open(tab, false);
      if (target) { var te = document.getElementById(target); if (te) te.scrollIntoView(); }
    }
    fromHash(true);
    window.addEventListener("hashchange", function () { fromHash(false); });
    // 탭 안 바로가기를 누르면 그 섹션이 든 탭을 연다
    root.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest('.subnav a, .g-sec a[href^="#"]'); if (!a) return;
      var id = a.getAttribute("href").slice(1);
      g.tabs.forEach(function (t) { if ((t.sections || []).indexOf(id) >= 0 && document.getElementById("tab-" + t.id).hidden) open(t.id, false); });
    });
  }

  fetch(src, {cache: "no-cache"}).then(function (r) { return r.json(); }).then(render).catch(function () {
    root.append(el("p", "empty", "안내서를 불러오지 못했어요. 새로고침해 주세요."));
  });
})();
