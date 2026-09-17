#!/usr/bin/env python3
"""R18/R19/R21 원고 게이트. 설계문서가 아니라 '원고'에 적용하는 규칙.
   주장이 아니라 측정을 출력한다: 위반 건수를 세기만 한다."""
import re, sys

MACRO = re.compile(r'<\?reg\s+[\w.\-]+\s*\?>')
# 비수치 맥락(절 번호, 표준 식별자, 날짜, 연도, 버전)은 제외
EXEMPT = re.compile(r'(?:§\d+|R\d+|L\d+|E\d+|REG-\d+|INV-\d+|PW-\d+|D\d+|G\d+|F\d+'
                    r'|v\d+|20\d\d|ICH|ISO|RFC|\d+층|\d+석|\d+기|\d+인자|\d+수준|\d+행|\d+개|\d+건|\d+편|\d+인)')
NUM = re.compile(r'(?<![\w.<?§])\d+(?:[.,]\d+)?%?')
# R19: 'N배/N× + 비교어' 는 두 원시값의 파생량이다. 손서술 금지.
DERIVED = re.compile(r'(\d+(?:\.\d+)?)\s*(?:×|배)\s*'
                     r'(?:의\s*)?(?:더\s*)?(?:비용\s*)?'
                     r'(?:절감|감소|증가|향상|단축|빠르|저렴|싸|speedup|reduction|increase|'
                     r'cheaper|faster|slower|higher|lower|more|less|improvement|gain)',
                     re.I)
BOUND_WORD = re.compile(r'(상한|하한|경계|보수적|최악|bound)')
METHOD_TAG = re.compile(r'\[(?:독립|Fréchet|시뮬|closed-form|점추정|상한)\]')

def gate(path):
    t = open(path, encoding='utf-8').read()
    # R18 경계: 표제지(저자·소속·각주)는 수치 주장 영역이 아니다
    m = re.search(r'(?im)^\s*#*\s*(abstract|초록|summary)\b', t)
    if m: t = t[m.start():]
    m = re.search(r'(?im)^\s*#*\s*(references|참고문헌|bibliography)\b', t)
    if m: t = t[:m.start()]
    body = MACRO.sub(' <MACRO> ', t)
    body = re.sub(r'```.*?```', ' <CODE> ', body, flags=re.S)
    body = re.sub(r'^\s*\|.*\|\s*$', '', body, flags=re.M)   # 표는 레지스트리 산출로 간주
    # R18 오양성 제거: 저자 소속 첨자·각주·HTML 태그·마크다운 링크는 수치 주장이 아니다
    body = re.sub(r'<sup>.*?</sup>', ' ', body, flags=re.S)
    body = re.sub(r'<[^>]{1,80}>', ' ', body)
    body = re.sub(r'\]\(#?[^)]*\)', '] ', body)
    body = re.sub(r'\bFig(?:ure)?\.?\s*\d+[a-z]?|\bTable\s*\d+|\bref\.?\s*\d+|\[\d+(?:[,\-]\d+)*\]',
                  ' ', body, flags=re.I)

    bare = []
    for m in NUM.finditer(body):
        ctx = body[max(0, m.start()-12):m.end()+12]
        if EXEMPT.search(ctx): continue
        bare.append((m.group(0), ctx.replace('\n', ' ').strip()))

    derived = [m.group(0) for m in DERIVED.finditer(body)]

    untagged = []
    for m in BOUND_WORD.finditer(body):
        seg = body[max(0, m.start()-120):m.end()+120]
        if not METHOD_TAG.search(seg):
            untagged.append(m.group(0))

    return bare, derived, untagged

for p in sys.argv[1:]:
    b, d, u = gate(p)
    print(f"=== {p} ===")
    print(f"  R18 위반 (매크로 밖 맨 숫자)      : {len(b)}건")
    for v, c in b[:5]: print(f"        · {v!r}  …{c[:60]}…")
    print(f"  R19 위반 (파생량 손서술)          : {len(d)}건  {d[:4]}")
    print(f"  R21 위반 (경계어에 산출방법 태그 없음): {len(u)}건  {u[:6]}")
    print(f"  판정: {'빌드 실패' if (b or d or u) else '통과'}\n")
