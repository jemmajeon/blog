#!/usr/bin/env python3
"""R20 인용 게이트 — 축자 인용 의무.

문제: 인용 할루시네이션은 논문에서 가장 위험한 거짓이며, 저자 본인은 탐지할 수 없다.
      (이 세션의 E10: Kaplow 1992의 결론을 반대 방향으로 요약했다.)
해법: 모든 문헌 주장에 ①축자 인용문 ②출처 ③위치를 등록하고, 빌드가 인용문 실존을 대조한다.
      **대조 불가 출처는 인용하지 않는다.** 검증 불가는 통과가 아니라 실패다.

레지스트리 스키마 (citations.json):
  [{"id","claim","quote","source","locator"}]
    claim   — 원고가 그 문헌에 귀속시키는 주장
    quote   — 그 주장을 뒷받침하는 **축자** 문장 (출처에 그대로 존재해야 함)
    source  — 대조 가능한 파일 경로
    locator — 절·페이지·행 (사람이 찾아갈 수 있어야 함)
"""
import json, re, sys, os, unicodedata

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('’', "'").replace('‘', "'")
    s = s.replace('“', '"').replace('”', '"')
    s = re.sub(r'[‐-―]', '-', s)
    return re.sub(r'\s+', ' ', s).strip().lower()

def check(reg_path, root='.'):
    entries = json.load(open(reg_path, encoding='utf-8'))
    errs, oks = [], []
    for e in entries:
        eid = e.get('id', '?')
        for k in ('claim', 'quote', 'source', 'locator'):
            if not e.get(k):
                errs.append(f"[{eid}] 필수 필드 누락: {k} (R20)")
        if not e.get('quote') or not e.get('source'):
            continue
        src = e['source'] if os.path.isabs(e['source']) else os.path.join(root, e['source'])
        if not os.path.exists(src):
            errs.append(f"[{eid}] 출처 대조 불가: {e['source']} 없음 "
                        f"→ R20에 의해 인용 금지 (검증 불가는 통과가 아니다)")
            continue
        body = norm(open(src, encoding='utf-8', errors='replace').read())
        q = norm(e['quote'])
        if len(q) < 25:
            errs.append(f"[{eid}] 인용문이 너무 짧아 대조가 무의미: {len(q)}자 (25자 이상 요구)")
        elif q in body:
            oks.append(eid)
        else:
            # 부분 일치 진단: 앞 40% 는 있는데 전체가 없으면 개작(paraphrase) 의심
            head = q[:max(25, int(len(q) * .4))]
            hint = " (앞부분은 존재 — 개작·절단 의심)" if head in body else " (출처에 유사 문장 없음)"
            errs.append(f"[{eid}] **축자 인용문이 출처에 존재하지 않음**{hint}\n"
                        f"        주장 : {e['claim'][:70]}\n"
                        f"        인용 : \"{e['quote'][:70]}…\"\n"
                        f"        출처 : {e['source']} @ {e.get('locator')}")
    return oks, errs

if __name__ == '__main__':
    reg = sys.argv[1] if len(sys.argv) > 1 else 'fixtures/citations.json'
    root = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(reg) or '.'
    oks, errs = check(reg, root)
    print(f"=== cite_gate (R20): {reg} ===")
    print(f"  대조 성공 {len(oks)}건 / 실패 {len(errs)}건\n")
    for e in errs: print("  [ERROR]", e)
    print(f"\n  판정: {'빌드 실패' if errs else '통과'}")
    sys.exit(1 if errs else 0)
