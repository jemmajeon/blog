#!/usr/bin/env python3
"""설계 문서 린터 — REVISION_POLICY.md의 R2~R6을 기계 검사한다.
반복 발생한 결함 '유형'을 규칙화한 것이지, 개별 결함 목록이 아니다.
사용: python3 design_lint.py design_vN.md   (ERROR 1건 이상이면 exit 1)"""
import re, sys

def sections(text):
    """## 또는 ### 헤딩 기준으로 (번호, 제목, 본문) 분할"""
    out, cur = [], None
    for line in text.splitlines():
        m = re.match(r'^#{2,3}\s+(\S+)\s*(.*)$', line)
        if m:
            if cur: out.append(cur)
            cur = [m.group(1), m.group(2), []]
        elif cur: cur[2].append(line)
    if cur: out.append(cur)
    return [(a, b, "\n".join(c)) for a, b, c in out]

def lint(path):
    text = open(path, encoding='utf-8').read()
    secs = sections(text)
    E, W = [], []

    # --- L1 / R2 : 게이트는 귀무·대립 하 통과 확률이 계산돼 있어야 한다 (REG-001) ---
    GATE = re.compile(r'(넘지 않을 때만|초과하면|미만이면|이하일 때만|넘으면).{0,80}?(허용|무효화|전환|채택|판정|권고|사용)')
    for num, title, body in secs:
        for m in GATE.finditer(body):
            ctx = body[max(0, m.start()-200):m.end()+200]
            if '귀무 하 통과 확률' not in ctx and '통과 확률' not in ctx:
                E.append(f"L1 [{num}] 판정 게이트에 귀무/대립 하 통과 확률 미기재 (R2, REG-001): …{m.group(0)[:50]}…")

    # --- L5 / R3 : 명칭 기반 면제 표현 금지 (REG-002) ---
    for num, title, body in secs:
        for m in re.finditer(r'(\S+)이 아닌\s+(\S+)', body):
            if any(k in m.group(0) for k in ('파일럿','예비','시범','테스트')):
                E.append(f"L5 [{num}] 명칭 기반 면제 표현 (R3, REG-002): '{m.group(0)}' — 기능으로 범위를 정의할 것")

    # --- L4 / R4 : 강등 목록과 병기 의무의 충돌 (REG-004) ---
    demoted = set()
    for num, title, body in secs:
        for m in re.finditer(r'([^\n]{0,200}?)(?:는|은)\s*\*\*전부 secondary/exploratory\*\*', body):
            demoted |= {t.strip(' *·-') for t in re.split(r'[·,/]', m.group(1)) if 2 <= len(t.strip(' *·-')) <= 12}
    for num, title, body in secs:
        if '결론 문단에 반드시 병기' in body or '결론 문단에 반드시 기재' in body:
            for d in demoted:
                if d and d in body:
                    E.append(f"L4 [{num}] '{d}' 이(가) 강등 목록에 있으면서 결론 문단 병기 의무 대상 (R4, REG-004)")

    # --- L6 / R5 : 주 종점의 이질 하위집합에는 층화 보고가 동반돼야 한다 (REG-003) ---
    for num, title, body in secs:
        for m in re.finditer(r'(NO-REF|0점 처리|0점 산입|별도 분류|하위집합)', body):
            ctx = body[max(0, m.start()-400):m.end()+400]
            if '층화' not in ctx and '분리 기록' not in ctx and '분해' not in ctx:
                W.append(f"L6 [{num}] 이질 하위집합 '{m.group(1)}' 에 층화/분해 보고 조항 없음 (R5, REG-003)")
                break

    # --- L2 : κ는 평정자 쌍을 명시해야 한다 ---
    for num, title, body in secs:
        for m in re.finditer(r'κ', body):
            ctx = body[max(0, m.start()-120):m.end()+120]
            if not re.search(r'(간\s*κ|κ[^\n]{0,40}(간|쌍)|두 (판정자|채점자|코더|분석자))', ctx):
                W.append(f"L2 [{num}] κ의 평정자 쌍 미명시")
                break

    # --- L3 : 사전 등록 임계값이 붙은 비율은 분모가 정의돼야 한다 ---
    for num, title, body in secs:
        if re.search(r'(상한|임계값|초과 시)', body) and re.search(r'\w+율', body):
            if '분모' not in body:
                W.append(f"L3 [{num}] 임계값이 걸린 비율에 분모 정의 없음")

    # --- L7 / R6 : 주 종점 상류 산출물은 사전 공개 목록에 등재돼야 한다 ---
    disclose = "\n".join(b for n, t, b in secs if '사전 공개' in t or '사전공개' in t)
    UPSTREAM = ['보정 세트', '정답 집합', '코딩 매뉴얼', '체크리스트', '라벨쌍', '작성 지침']
    for u in UPSTREAM:
        if u in text and u not in disclose:
            E.append(f"L7 주 종점 상류 산출물 '{u}' 이(가) 사전 공개 목록에 미등재 (R6)")

    # --- L8 : 명명된 역할은 역할 분리 행렬에 행이 있어야 한다 ---
    matrix = "\n".join(b for n, t, b in secs if '역할 분리' in t)
    if matrix:
        # 사람 역할로 확정되는 문맥에서만 추출: '외부/독립/제3' 수식 또는 'N인' 동반
        cand = set()
        for m in re.finditer(r'(?:외부|독립|제3)\s*([가-힣]{2,8}(?:자|가))', text): cand.add(m.group(1))
        for m in re.finditer(r'([가-힣]{2,8}자)\s*[:：]?\s*(?:외부\s*)?\d\s*인', text): cand.add(m.group(1))
        for m in re.finditer(r'(제3\s*[가-힣]{2,6}자)', text): cand.add(re.sub(r'\s+',' ',m.group(1)))
        for r in sorted(cand):
            if r in ('설계자',): continue
            if r not in matrix:
                W.append(f"L8 역할 '{r}' 이(가) 역할 분리 행렬에 행 없음")

    # --- L9 : 손으로 쓴 파생 수치 금지 (자동 생성 선언과 충돌) ---
    for num, title, body in secs:
        if '검정력' in body and re.search(r'검정력\s*0\.\d', body) and '스크립트가' in text:
            W.append(f"L9 [{num}] 파생 수치(검정력)가 본문에 리터럴로 기재됨 — 자동 주입 선언과 충돌")
            break

    # --- L10 / R11 : "보수적" 라벨은 식별 한계 증명이 있을 때만 (REG-005) ---
    for num, title, body in secs:
        for m in re.finditer(r'보수적[으로]*\s*[^\n]{0,60}?=\s*([0-9.]+)', body):
            ctx = body[max(0,m.start()-300):m.end()+300]
            if not re.search(r'(식별집합|Fr[eé]chet|한계|상한|하한)', ctx):
                E.append(f"L10 [{num}] '보수적' 라벨에 식별 한계 근거 없음 (R11, REG-005): {m.group(0)[:40]}")

    # --- L11 / R10 : 뺄셈 원칙 — **주장(claim) 수**로 센다 (위원1 경고: 조항 병합으로 게임 가능) ---
    import os
    def count_claims(t):
        # 규범적 술어 1개 = 주장 1개. 조항을 합쳐도 술어는 줄지 않는다.
        t = re.sub(r'^\s*\|.*\|\s*$', '', t, flags=re.M)   # 표 행 제외(중복 계수 방지)
        pats = [r'한다(?![가-힣])', r'않는다(?![가-힣])', r'해야\s*한다', r'하지\s*않는다',
                r'금지한다', r'허용한다', r'필수[이다로]', r'의무[이다로화]', r'등록한다',
                r'보고한다', r'삭제한다', r'고정한다', r'명시한다', r'선언한다']
        return sum(len(re.findall(x, t)) for x in pats)
    here = os.path.dirname(os.path.abspath(path)) or '.'
    mine = re.match(r'design_v(\d+)\.md', os.path.basename(path))
    if mine:
        c_cur = count_claims(text)
        # R27: 기준선은 직전 R15 준수 버전. 명시 인자(--baseline vN)로만 바꾼다.
        base_n = int(mine.group(1)) - 1
        base_tag = None
        for a in sys.argv:
            if a.startswith('--baseline=v'):
                base_tag = a.split('=v')[1]
                W.append(f"R27 적용: L11 기준선을 v{base_tag}로 명시 지정 (직전 R15 준수 버전)")
        prev = os.path.join(here, f'design_v{base_tag or base_n}.md')
        if os.path.exists(prev):
            c_prev = count_claims(open(prev, encoding='utf-8').read())
            if c_cur > c_prev:
                W.append(f"L11 주장 수 {c_prev} → {c_cur} (증가). 정책 충돌 #2에 의해 WARN — "
                         f"릴리스 게이트는 R9(작동특성)+R15(의무추적)+공격 라운드로 대체됨. 증가 사실은 릴리스 노트 기재 의무")
            else:
                W.append(f"L11 주장 수 {c_prev} → {c_cur} (감소 확인)")

    # --- L12 / R16 : 판정·분류 규칙의 분기가 상호배타적이어야 한다 (REG-008) ---
    if re.search(r'CI 전체가 0 초과.*?비결정', text, re.S):
        import itertools
        D = 0.05
        brs = [lambda L, U: L > 0,                      # "CI 전체가 0 초과"
               lambda L, U: (L > -D) and (U < D)]       # "CI 전체가 (-d,+d) 내부"
        g = [i/200 for i in range(-30, 31)]
        bad = [(L, U) for L, U in itertools.product(g, g)
               if L <= U and sum(b(L, U) for b in brs) > 1]
        if bad:
            L, U = bad[0]
            E.append(f"L12 [§1] 판정 분기가 상호배타적이 아님 (R16, REG-008): "
                     f"CI=({L:+.3f},{U:+.3f}) 등 {len(bad)}개 지점에서 '지지'와 '반증'이 동시 발화")

    # --- L13 / R9 : 임계 셀 → 부록 E 작동특성 등록표 대조 (E23 교정: 문구 화이트리스트 폐기) ---
    # 임계 셀 = 비교 연산자(≥ ≤ > < 이상 이하 미만 초과 넘으면 도달) 60자 이내에 나타나는 셀. 이름 접미사로 판정하지 않는다(R3).
    CMP = r'(≥|≤|>|<|이상|이하|미만|초과|넘으면|도달)'
    thr = set()
    for m in re.finditer(r'`([\w.]+)`', text.split('## 부록 B')[0]):
        win = text[max(0, m.start()-60):m.end()+60]
        if re.search(CMP, win): thr.add(m.group(1))
    if '## 부록 B' in text:
        cellsB_ = set(re.findall(r'`([\w.]+)`', text.split('## 부록 B')[1].split('## 부록 C')[0]))
        thr &= cellsB_
    appE = text.split('## 부록 E')[1] if '## 부록 E' in text else ''
    regE = {}
    for line in appE.splitlines():
        m = re.match(r'^\|([^|]*)\|([^|]*)\|([^|]*)\|', line)
        if not m: continue
        for c in re.findall(r'`([\w.]+)`', m.group(1)):
            regE[c] = m.group(3)
    for c in sorted(thr - set(regE)):
        E.append(f"L13 임계 셀 `{c}` 가 비교 연산자에 쓰였으나 부록 E(작동특성 등록표)에 행이 없음 (R9)")
    for c, basis in sorted(regE.items()):
        if not re.search(r'PW-2|부록 D|적격 기준|결정적 문법|셀 정의', basis):
            E.append(f"L13 부록 E `{c}` 행에 산출 근거 없음 (R9)")
    # --- L14 : 고아 셀 — 부록 B에 있으나 본문이 소비하지 않음 ---
    if '## 부록 B' in text:
        body, rest = text.split('## 부록 B', 1)
        appB = rest.split('## 부록 C')[0]
        cellsB = set(re.findall(r'`([\w.]+)`', appB))
        used  = set(re.findall(r'`([\w.]+)`', body))
        for c in sorted(cellsB - used):
            E.append(f"L14 고아 셀 `{c}` — 부록 B에 등록됐으나 본문 어디에서도 소비되지 않음")
        for c in sorted(x for x in used - cellsB if '.' in x and not x.endswith('.py')):
            E.append(f"L14 미등록 셀 `{c}` — 본문이 참조하나 부록 B에 없음")
    # --- L15 / R15 : 기술용어 토큰 소실 (E20: 유사도 diff가 '(양측)'·'BCa' 삭제를 놓침) ---
    if mine:
        prevp = os.path.join(here, f'design_v{int(mine.group(1))-1}.md')
        for a in sys.argv:
            if a.startswith('--prev='): prevp = a.split('=',1)[1]
        if os.path.exists(prevp):
            TERMS = re.compile(r'\b(BCa|양측|단측|백분위|정지규칙|SESOI|Fréchet|κ|ICC|CR2|Satterthwaite|wild|interleav\w*|해시|매니페스트|시드)\b')
            lost = set(TERMS.findall(open(prevp, encoding='utf-8').read())) - set(TERMS.findall(text))
            for w in sorted(lost):
                W.append(f"L15 기술용어 '{w}' 가 {os.path.basename(prevp)} 에 있었으나 현 버전에 없음 — R15 (a)/(b)/(c) 판정 필요")

    return E, W

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'design_v3.md'
    E, W = lint(path)
    print(f"=== design_lint: {path} ===\n")
    print(f"ERROR {len(E)}건 / WARN {len(W)}건\n")
    for e in E: print("  [ERROR]", e)
    if E and W: print()
    for w in W: print("  [WARN ]", w)
    print(f"\n판정: {'릴리스 불가 (R8)' if E else '릴리스 가능'}")
    sys.exit(1 if E else 0)
