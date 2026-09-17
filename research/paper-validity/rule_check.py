#!/usr/bin/env python3
"""R16 판정규칙 검사 — 구문 + **의미론**.

E17 교정: 첫-일치 순서 규칙에 대해 '발화 분기 수 == 1'은 제어흐름의 정리이므로
항진명제다. 그 검사는 v5의 라벨 오류(R11-A F1)를 잡지 못했다.
의미론 검사를 추가한다: H1을 참 효과 Δ에 대한 집합 S_H1으로 전사하고,
  지지 ⇒ CI ⊆ S_H1        (CI 안의 모든 Δ가 H1을 만족)
  반증 ⇒ CI ⊆ S_H1^c      (CI 안의 모든 Δ가 H1을 위반)
을 격자 전역에서 확인한다. 라벨이 H1의 부정이 아니면 여기서 잡힌다."""
import itertools, sys
D = 0.05
G = [i/1000 for i in range(-150, 151)]

# ── 규칙 전사 ─────────────────────────────────────────────────────────
def v4_rule(L, U):
    f = [L > 0, (L > -D) and (U < D)]
    return ['지지','반증'][f.index(True)] if any(f) else '비결정'   # 병렬: 첫 참 채택
def v4_H1(delta): return delta > 0                                   # "높다"

def v5_0_rule(L, U):                       # v5 초판 (R11-A F1 대상)
    if L >= -D and U <= D: return '반증'
    if L > 0: return '지지'
    return '비결정'
def v5_0_H1(delta): return delta > 0       # H1은 여전히 "높다"

def v5_1_rule(L, U):                       # v5 개정: H1 = Δ ≥ δ (SESOI)
    if U < D: return '반증'
    if L > D: return '지지'
    return '비결정'
def v5_1_H1(delta): return delta >= D

# ── 검사 ─────────────────────────────────────────────────────────────
def check(name, rule, H1):
    over = sem = 0; ex = None
    for L, U in itertools.product(G, G):
        if L > U: continue
        v = rule(L, U)
        inside = [d for d in G if L <= d <= U]
        if v == '지지' and not all(H1(d) for d in inside): sem += 1; ex = ex or (L, U, v)
        if v == '반증' and any(H1(d) for d in inside):     sem += 1; ex = ex or (L, U, v)
    tag = '통과' if sem == 0 else '실패'
    print(f"{name:6s} 의미론 위반 {sem:5d}건  → {tag}" + (f"   예: CI=[{ex[0]:+.3f},{ex[1]:+.3f}] 라벨={ex[2]}" if ex else ""))
    return sem == 0

print(f"격자 CI 수 {sum(1 for L,U in itertools.product(G,G) if L<=U)}  (δ={D})")
r4  = check('v4',   v4_rule,   v4_H1)
r50 = check('v5.0', v5_0_rule, v5_0_H1)
r51 = check('v5.1', v5_1_rule, v5_1_H1)
print("기대: v4 실패(중첩·라벨) / v5.0 실패(라벨, E17이 놓친 것) / v5.1 통과")
sys.exit(0 if (not r4 and not r50 and r51) else 1)
