#!/usr/bin/env python3
"""1층(기계층) 실증 — 장부·산술·보고 오류를 자동 검출한다.
네이처 논문(Paper2Agent) 원문에 돌려, 내가 수동으로 확정한 3건을 재현하는지 본다."""
import re, sys
from math import isclose

def load(*paths):
    return "\n".join(open(p, encoding='utf-8').read() for p in paths)

def check_foldchange(t):
    """규칙 F: 'A ... B ... N배' 형태에서 배수가 입력값으로부터 도출되는지 검산"""
    out=[]
    # "$0.20 per query in 1.6 minutes, compared to $0.38 ... 4.3 minutes ... 2.8x ... 6.3x"
    pat = re.compile(r'\$([\d.]+)\s*per query in\s*([\d.]+)\s*minutes,\s*compared to\s*\$([\d.]+)\s*per query in\s*([\d.]+)\s*minutes[^.]*?([\d.]+)×\s*cost reduction and\s*([\d.]+)×\s*speedup', re.S)
    for m in pat.finditer(t):
        c1,t1,c2,t2,fc,fs = map(float, m.groups())
        real_c, real_s = c2/c1, t2/t1
        if not isclose(real_c, fc, rel_tol=0.05):
            out.append(f"F1 비용 배수 불일치: 주장 {fc}× vs 도출 {real_c:.2f}× (${c2}/${c1})")
        if not isclose(real_s, fs, rel_tol=0.05):
            out.append(f"F2 속도 배수 불일치: 주장 {fs}× vs 도출 {real_s:.2f}× ({t2}/{t1}분)")
    return out

def check_category_counts(t):
    """규칙 C: 같은 실험의 범주 수 / 구성 수가 문서 내에서 일관되는지"""
    out=[]
    words={'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8}
    cats=set(); cfgs=set()
    for m in re.finditer(r'injected\s+(\w+)\s+categories', t, re.I):
        w=m.group(1).lower()
        if w in words: cats.add(words[w])
    for m in re.finditer(r'across all\s+(\w+)\s+failure categories', t, re.I):
        w=m.group(1).lower()
        if w in words: cats.add(words[w])
    for m in re.finditer(r'(\d+)\s+adversarial configurations', t):
        cfgs.add(int(m.group(1)))
    if len(cats)>1:
        out.append(f"C1 범주 수 불일치: 문서 내 {sorted(cats)} 가 동일 실험에 공존")
    for nc in sorted(cats):
        for cf in sorted(cfgs):
            if cf % nc != 0:
                out.append(f"C2 구성 수 정합 실패: 구성 {cf}개가 범주 {nc}개로 나뉘지 않음")
    return out

def check_uncertainty_unit(t):
    """규칙 U: 불확실성의 단위가 문서 내에서 하나로 고정되는지"""
    out=[]
    units=set()
    if re.search(r'standard error \(SE\) across questions', t): units.add('across questions')
    if re.search(r'standard error are reported across the\s*\d*\s*runs', t) or \
       re.search(r'reported across the 5\s*\n?\s*runs', t): units.add('across runs')
    if re.search(r'n=\s*5 independent runs', t): units.add('across runs (figure legend)')
    if len({u.split(' (')[0] for u in units})>1:
        out.append(f"U1 불확실성 단위 불일치: {sorted(units)}")
    if re.search(r'100\.0%\s*±\s*0\.0%', t):
        out.append("U2 '± 0.0%' 보고 — 불확실성 0 주장 (n 병기 없이 해석 불가)")
    return out

if __name__=='__main__':
    t = load(*sys.argv[1:])
    print(f"=== paper_lint (1층 기계 검사) ===\n대상 길이 {len(t):,}자\n")
    total=0
    for name, fn in [("배수·산술 (F)", check_foldchange),
                     ("범주·구성 수 (C)", check_category_counts),
                     ("불확실성 단위 (U)", check_uncertainty_unit)]:
        hits=fn(t); total+=len(hits)
        print(f"[{name}] {len(hits)}건")
        for h in hits: print(f"   ✗ {h}")
    print(f"\n총 검출 {total}건")
