"""L12: 판정규칙이 함수인지 기계 검사.
   설계의 판정 분기를 술어로 옮겨, (L,U) 격자 전역에서
   발화 분기 수가 항상 정확히 1인지 확인한다."""
import itertools, sys

D = 0.05
def b_support(L,U):  return L > 0                       # "CI 전체가 0 초과"
def b_refute(L,U):   return (L > -D) and (U < D)        # "CI 전체가 (-d,+d) 내부"
def b_indet(L,U):    return not b_support(L,U) and not b_refute(L,U)  # "그 외"

grid = [i/1000 for i in range(-150,151)]
over, under, ex = [], [], []
for L,U in itertools.product(grid,grid):
    if L > U: continue
    n = sum([b_support(L,U), b_refute(L,U), b_indet(L,U)])
    if n > 1: over.append((L,U))
    elif n == 0: under.append((L,U))
tot = sum(1 for L,U in itertools.product(grid,grid) if L<=U)
print(f"검사 CI 수         : {tot}")
print(f"2개 이상 분기 발화 : {len(over)}  ({100*len(over)/tot:.1f}%)")
print(f"발화 분기 없음     : {len(under)}")
if over:
    print(f"  예시 : CI=({over[0][0]:+.3f},{over[0][1]:+.3f}) → 지지 AND 반증")
    print(f"  중첩역 : 0 < L <= U < {D}  (비어있지 않음)")
    # 정밀도가 높아질수록 중첩 확률이 1로 가는지
    import statistics
    for se in [0.05,0.02,0.01,0.005,0.002]:
        L,U = 0.02-1.96*se, 0.02+1.96*se
        print(f"  SE={se:<6} 참효과 0.02 → 중첩={b_support(L,U) and b_refute(L,U)}")
    sys.exit(1)
