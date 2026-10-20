# blog

모임·여행 **안내서**와 다녀온 뒤의 **기록**. <https://jemmajeon.github.io/blog/>

## 탭

| 탭 | 주소 | 내용 |
|---|---|---|
| 안내서 | `/blog/` | 가기 전에 조사한 장소 가이드. 날짜가 지나면 "지난 안내"로 내려간다 |
| 기록 | `/blog/log/` | 다녀온 뒤의 글. 본문은 마크다운 |

## 글 추가하는 법

### 안내서
1. `restaurant/<slug>.json` 작성 — 형식은 [`assets/GUIDE_SCHEMA.md`](assets/GUIDE_SCHEMA.md)
2. `assets/guide-shell.html`을 `restaurant/<slug>.html`로 복사하고 `{{TITLE}}`, `{{SUBTITLE}}`, `{{SLUG}}` 채우기
3. `posts.json`에 한 줄 추가 (`"section": "guide"`, `kind`, `area`, `date`, `count`)

### 기록
1. `log/<slug>.md` 작성 (제목은 posts.json에서 가져오므로 본문만)
2. `posts.json`에 `{ "section": "log", "slug": "<slug>", "title": "...", "tag": "한 줄 요약", "date": "YYYY-MM-DD" }`
3. 주소는 `/blog/log/post.html?p=<slug>`

목록에서 숨기려면 `"listed": false`, 외부 링크면 `"external": true`.

## 구조

```
index.html          안내서 탭 (posts.json을 읽어 그림)
log/                기록 탭 · post.html(마크다운 렌더러) · <slug>.md
posts.json          목록의 단일 진실 소스
assets/             공통 스타일(site.css) · 안내서 렌더러(guide.js) · 상단 바(bar.js) · 껍데기 · 형식 문서
restaurant/         맛집·모임 안내서 (<slug>.html 껍데기 + <slug>.json 데이터)
travels/            여행 안내서 (자체 디자인 유지, 상단 바만 공통)
life/               생활 정보 (목록 숨김)
data/               원본 조사 데이터
archive/            구버전 보관 (archive/v1 = 2026-10 개편 전 원본)
go/                 UTM 링크 릴레이 — 경로 고정
```

## 건드리면 안 되는 것

- **`go/`** — 배포된 UTM 단축링크(`/blog/go/?to=...`)가 이 경로를 가리킨다. 옮기면 공유된 링크가 전부 죽는다.
- **글 주소** — `restaurant/<slug>.html` 등 기존 주소는 그대로 둔다. 개편 때도 주소는 바꾸지 않았다.
- **루트의 `*_dashboard.html`, `*_guide.html`** — 옛 주소용 리다이렉트 스텁(meta refresh). GitHub Pages는 서버 리다이렉트를 못 한다.

## 개인정보

공개 레포다. 안내서에는 사람 이름·가족 관계·개인 연락처를 넣지 않는다 ("친구", "동창"). 가게 정보는 공개 정보라 그대로 둔다.
