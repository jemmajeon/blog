#!/usr/bin/env python3
"""R18/R19 실행 엔진 — 레지스트리에서 원고를 생성한다.

manuscript_gate 는 "맨 숫자 금지"를 강제하지만, 매크로를 값으로 바꿔주는 것이 없으면
R18은 규칙일 뿐 규율이 아니다. 이 스크립트가 그 구멍을 닫는다.

registry.json:
  {"values": {"key": {"v": <수 또는 문자열>, "fmt": "...", "method": "[태그]"}},
   "derived": {"key": {"proc": "ratio|delta|pct", "of": ["k1","k2"], "fmt": "...", "method": "[계산]"}}}

핵심: **파생량은 서술할 수 없다 — proc 가 계산한다.** (R19)
      **산출방법 태그는 원고가 아니라 레지스트리가 소유한다** — 원고에 손으로 적으면 중복된다.
      네이처 논문의 확정 결함 F1·F2(주장 2.8× vs 도출 1.90×)는 이 구조에서 발생 불가하다.
      경계·상한 값은 method 태그를 강제 주입한다. (R21)
"""
import json, re, sys

MACRO = re.compile(r'<\?reg\s+([\w.\-]+)\s*\?>')

PROCS = {
    'ratio': lambda a, b: a / b,
    'delta': lambda a, b: a - b,
    'pct':   lambda a, b: 100.0 * a / b,
}

def resolve(reg):
    out, errs = {}, []
    for k, s in reg.get('values', {}).items():
        v = s['v']
        # 문자열 셀(구간 표기 등)은 그대로, 수치 셀은 fmt 적용
        out[k] = (v if isinstance(v, str) else format(v, s.get('fmt', 'g')),
                  s.get('method', ''))
    for k, s in reg.get('derived', {}).items():
        proc = s.get('proc')
        if proc not in PROCS:
            errs.append(f"파생 '{k}': 알 수 없는 proc {proc!r} — 허용 {sorted(PROCS)}")
            continue
        try:
            args = [reg['values'][x]['v'] for x in s['of']]
        except KeyError as e:
            errs.append(f"파생 '{k}': 입력 {e} 가 values 에 없음")
            continue
        if len(args) != 2:
            errs.append(f"파생 '{k}': proc {proc} 는 입력 2개를 요구 (받음 {len(args)})")
            continue
        out[k] = (format(PROCS[proc](*args), s.get('fmt', '.2f')), s.get('method', '[계산]'))
    return out, errs

def build(tpl_path, reg_path, out_path=None):
    tpl = open(tpl_path, encoding='utf-8').read()
    reg = json.load(open(reg_path, encoding='utf-8'))
    vals, errs = resolve(reg)
    used = set()

    def sub(m):
        k = m.group(1)
        if k not in vals:
            errs.append(f"매크로 <?reg {k}?> 에 대응하는 레지스트리 셀이 없음 — 빌드 실패")
            return m.group(0)
        used.add(k)
        s, meth = vals[k]
        return s + (f" {meth}" if meth else "")

    text = MACRO.sub(sub, tpl)
    # 파생 셀의 입력은 간접 사용이다 — 죽은 셀로 보지 않는다
    for s in reg.get('derived', {}).values():
        used.update(s.get('of', []))
    for k in sorted(set(vals) - used):
        errs.append(f"레지스트리 셀 '{k}' 가 원고에서 쓰이지 않음 — 죽은 셀 (사후 선택 여지)")
    if errs:
        return None, errs
    if out_path:
        open(out_path, 'w', encoding='utf-8').write(text)
    return text, []

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("usage: build_manuscript.py <template.md> <registry.json> [out.md]")
    text, errs = build(*sys.argv[1:4])
    print(f"=== build_manuscript (R18/R19): {sys.argv[1]} ===")
    if errs:
        for e in errs: print("  [ERROR]", e)
        print("\n  판정: 빌드 실패")
        sys.exit(1)
    print(f"  치환 완료 — {len(MACRO.findall(open(sys.argv[1], encoding='utf-8').read()))}개 매크로")
    print("  판정: 통과")
    if len(sys.argv) < 4: print("\n--- 산출 원고 ---\n" + text)
