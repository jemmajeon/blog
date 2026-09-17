#!/usr/bin/env python3
"""R16: 판정규칙이 함수인지 기계 검사.
   각 버전의 §1 분기를 술어로 전사하고, (L,U) 격자 전역에서 발화 분기 수가 항상 1인지 확인한다.
   v4: 비순서 병렬 분기 → 중첩 (REG-008). 실패해야 정상.
   v5: 순서 평가·첫 참에서 정지 → 구성상 배타·전수. 통과해야 정상."""
import itertools, sys
D = 0.05
G = [i/1000 for i in range(-150, 151)]

def v4(L, U):
    return [L > 0, (L > -D) and (U < D)]                       # 병렬 평가; 나머지는 "그 외"
def v5(L, U):
    if L >= -D and U <= D: return [True, False, False]         # (1) 등가
    if L > 0:              return [False, True, False]         # (2) 지지
    return                        [False, False, True]         # (3) 비결정

def scan(pred, has_else):
    over = under = 0
    for L, U in itertools.product(G, G):
        if L > U: continue
        f = pred(L, U); n = sum(f)
        if has_else and n == 0: n = 1
        over += n > 1; under += n == 0
    return over, under

tot = sum(1 for L, U in itertools.product(G, G) if L <= U)
o4, u4 = scan(v4, True)
o5, u5 = scan(v5, False)
print(f"격자 CI 수 {tot}")
print(f"v4: 2개 이상 발화 {o4}건 ({100*o4/tot:.1f}%) / 발화 없음 {u4}건  → {'실패(정상)' if o4 else '??'}")
print(f"v5: 2개 이상 발화 {o5}건 / 발화 없음 {u5}건  → {'통과' if not (o5 or u5) else '실패'}")
if '--v4' in sys.argv: sys.exit(1 if o4 else 0)
sys.exit(1 if (o5 or u5) else 0)
