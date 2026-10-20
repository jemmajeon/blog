// 자체 디자인을 가진 글(여행·생활)에 블로그 공통 상단 바를 붙인다. Shadow DOM이라 글의 CSS와 섞이지 않는다.
// 사용: <script src="../../assets/bar.js" data-base="../../"></script>
(function () {
  var me = document.currentScript, base = me.getAttribute("data-base") || "../";
  var host = document.createElement("div");
  var root = host.attachShadow({mode: "open"});
  root.innerHTML =
    '<style>:host{all:initial;display:block}' +
    '.bar{font:600 14px "Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;display:flex;align-items:center;gap:14px;' +
    'padding:10px max(18px,env(safe-area-inset-right,0px)) 10px max(18px,env(safe-area-inset-left,0px));background:#f8f6f2;color:#1d1a16;border-bottom:1px solid #e6e0d6}' +
    '@media (prefers-color-scheme:dark){.bar{background:#141210;color:#f1ece4;border-color:#332e29}}' +
    'a{color:inherit;text-decoration:none}a:hover{text-decoration:underline}.b{font-weight:800}.s{opacity:.55;font-weight:500}.sp{flex:1}</style>' +
    '<nav class="bar" aria-label="블로그"><a class="b" href="' + base + '">← jemmajeon <span class="s">블로그</span></a><span class="sp"></span>' +
    '<a href="' + base + '">안내서</a><a href="' + base + 'log/">기록</a></nav>';
  document.body.insertBefore(host, document.body.firstChild);
})();
