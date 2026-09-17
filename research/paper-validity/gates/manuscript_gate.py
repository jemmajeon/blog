#!/usr/bin/env python3
"""R18/R19/R21 원고 게이트 — 두 모드.

개념 교정 (2026-09-17): R18은 '기존 논문의 결함 탐지기'가 아니라
**집필 제약**이다. 매크로 규율로 쓰이지 않은 원고에 적용하면 모든 숫자가 위반이 되고,
그 건수는 아무 의미가 없다. 내가 처음 "네이처 논문 R18 위반 288건"이라 보고한 것은
규칙을 적용 영역 밖에서 쓴 것이다 (E12).

  strict 모드 — 규율 하에 집필된 원고. 예외는 아래 선언 목록뿐. 위반 1건이면 빌드 실패.
  audit  모드 — 규율 밖 원고. 위반 '건수'를 보고하지 않고 **매크로화 비율**을 보고한다.
                비율은 결함이 아니라 이행률이다.
"""
import re, sys

MACRO = re.compile(r'<\?reg\s+[\w.\-]+\s*\?>')

# 선언적 예외 목록. 휴리스틱이 아니라 명시 목록이며, 늘리려면 여기에 적어야 한다(감사 가능).
LITERAL_ALLOWLIST = [
    r'95%\s*CI', r'99%\s*CI', r'90%\s*CI',      # 구간 명칭 (데이터가 아님)
    r'p\s*<\s*0\.05', r'p\s*<\s*0\.01',          # 관례적 임계
    r'§\d+', r'R\d+\b', r'L\d+\b', r'E\d+\b', r'REG-\d+', r'INV-\d+',
    r'H[01]\b', r'2\^?3\b', r'Table\s*\d+', r'Fig(?:ure)?\.?\s*\d+[a-z]?',
    r'\[\d+(?:[,\-]\d+)*\]', r'20\d\d',          # 인용 번호·연도
]
ALLOW = re.compile('|'.join(LITERAL_ALLOWLIST), re.I)

NUM = re.compile(r'(?<![\w.])\d+(?:[.,]\d+)?\s*[%×]?')

# R19: 'N배/N× + 비교어'는 두 원시값의 파생량이다. 손서술 금지.
DERIVED = re.compile(r'(\d+(?:\.\d+)?)\s*(?:×|배)\s*(?:의\s*)?(?:더\s*)?(?:비용\s*)?'
                     r'(?:절감|감소|증가|향상|단축|빠르|저렴|싸|speedup|reduction|increase|'
                     r'cheaper|faster|slower|higher|lower|more|less|improvement|gain)', re.I)

# R21: 경계·상한·최악·보수적 주장에는 산출방법 태그가 있어야 한다.
BOUND_WORD = re.compile(r'(상한|하한|경계|보수적|최악|bound|worst[- ]case|upper limit)', re.I)
METHOD_TAG = re.compile(r'\[(?:독립|Fréchet|시뮬|계산|closed-form|점추정|상한|MC)\]')


def _strip(t, mode):
    if mode == 'audit':                      # 규율 밖 원고: 표제지·참고문헌 제외
        m = re.search(r'(?im)^\s*#*\s*(abstract|초록|summary)\b', t)
        if m: t = t[m.start():]
    m = re.search(r'(?im)^\s*#*\s*(references|참고문헌|bibliography)\b', t)
    if m: t = t[:m.start()]
    t = re.sub(r'```.*?```', ' <CODE> ', t, flags=re.S)
    t = re.sub(r'<sup>.*?</sup>', ' ', t, flags=re.S)
    t = re.sub(r'^\s*\|.*\|\s*$', '', t, flags=re.M)     # 표는 레지스트리 산출로 간주
    return t


def gate(path, mode='strict'):
    raw = open(path, encoding='utf-8').read()
    n_macro = len(MACRO.findall(raw))
    t = _strip(raw, mode)
    t = ALLOW.sub(' <ALLOWED> ', t)
    t = MACRO.sub(' <MACRO> ', t)

    bare = [(m.group(0).strip(), t[max(0, m.start()-40):m.end()+20].replace('\n', ' ').strip())
            for m in NUM.finditer(t)]
    derived = [m.group(0) for m in DERIVED.finditer(t)]
    untagged = [m.group(0) for m in BOUND_WORD.finditer(t)
                if not METHOD_TAG.search(t[max(0, m.start()-150):m.end()+150])]
    return {'mode': mode, 'macros': n_macro, 'bare': bare,
            'derived': derived, 'untagged': untagged}


def report(path, mode='strict'):
    r = gate(path, mode)
    n = len(r['bare'])
    print(f"=== {path}  [{mode}] ===")
    if mode == 'strict':
        print(f"  R18 매크로 밖 맨 숫자 : {n}건" + (" ← 빌드 실패" if n else " ✓"))
        for v, c in r['bare'][:6]:
            print(f"        · {v!r}  …{c[-55:]}…")
    else:
        tot = n + r['macros']
        pct = 100 * r['macros'] / tot if tot else 0.0
        print(f"  R18 매크로화 이행률   : {r['macros']}/{tot} = {pct:.1f}%"
              f"   (규율 밖 원고 — 위반 건수는 보고하지 않음)")
    print(f"  R19 파생량 손서술     : {len(r['derived'])}건  {r['derived'][:4]}")
    print(f"  R21 경계어 태그 누락   : {len(r['untagged'])}건  {r['untagged'][:5]}")
    fail = bool(r['derived'] or r['untagged'] or (mode == 'strict' and n))
    print(f"  판정: {'빌드 실패' if fail else '통과'}\n")
    return r, fail


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    mode = 'audit' if '--audit' in sys.argv else 'strict'
    bad = 0
    for p in args:
        _, f = report(p, mode)
        bad |= f
    sys.exit(1 if bad else 0)
