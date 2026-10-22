# blog

개인 기록용 정적 사이트. <https://jemmajeon.github.io/blog/>

## 글 추가하는 법

**`posts.json` 만 고치면 된다.** `index.html` 은 건드리지 않는다.

```jsonc
{
  "title": "글 제목",
  "file": "restaurant/새글.html",   // 저장소 기준 상대경로
  "tag": "부제 한 줄",
  "category": "restaurant",         // categories 에 있는 key
  "date": "2026-10-19"              // 목록은 이 값 기준 내림차순 정렬
}
```

목록·탭·저장소 구조 카드가 전부 이 파일에서 렌더링된다.
목록에서 숨기려면 `"listed": false`, 외부 링크면 `"external": true`.

## 숨은 글 보기

목록에 띄우고 싶지 않지만 나는 봐야 하는 글은 `posts.json` 에서 `"listed": false` 로 둔다.
평소에는 목록에 안 나오고, 아래 스위치로 켜면 보인다.

```
/blog/?all=1   켜기 — 비노출 글까지 전부 표시, 「목록 비노출」 배지가 붙는다
/blog/?all=0   끄기
```

한 번 켜면 그 브라우저에 기억되므로 이후에는 `/blog/` 만 열어도 계속 보인다.
다른 사람 브라우저에는 영향이 없다.

**주의** — 이건 편의 기능이지 접근 제한이 아니다. 저장소가 public 이라
`posts.json` 과 파일 자체는 누구나 볼 수 있다. 진짜 가려야 하는 내용은 여기 두지 않는다.

## 구조

```
index.html        진입점. posts.json 을 읽어 목록을 그린다
posts.json        글 목록의 단일 진실 소스
restaurant/       맛집 가이드
travels/          여행 일정 (날짜별 폴더)
life/             생활 정보
archive/          구버전 보관
go/               UTM 링크 릴레이
```

조사 데이터(JSON)는 별도 폴더로 빼지 않고 **해당 주제 폴더 안**에 둔다.
`restaurant/gangnam-line2-jemcory.json` 처럼.

## 건드리면 안 되는 것

**`go/`** — 배포된 UTM 단축링크(`/blog/go/?to=...`)가 이 경로를 가리킨다.
폴더를 옮기면 이미 공유된 링크가 전부 죽고 복구할 방법이 없다.

## 옛 경로

파일을 옮길 때 원래 위치에 리다이렉트 스텁(meta refresh)을 남긴다.
GitHub Pages 는 서버 리다이렉트를 못 하므로 이게 유일한 방법이다.
현재 루트의 `*_dashboard.html`, `*_guide.html` 들이 그 스텁이다 — 내용은 없다.
