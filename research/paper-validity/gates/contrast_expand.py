#!/usr/bin/env python3
"""R19: 주 종점 대비의 효과코딩 전개를 손으로 쓰지 않고 생성한다 (E18 교정).
   2^3 완전요인, ±1 코딩. 대비 = (Q=q, REG=+1, DISC=+1) − (Q=q, REG=−1, DISC=−1)."""
import sys
def expand(q):
    terms = ['Q','R','D','QR','QD','RD','QRD']
    row = lambda Q,R,Dd: dict(Q=Q,R=R,D=Dd,QR=Q*R,QD=Q*Dd,RD=R*Dd,QRD=Q*R*Dd)
    a, b = row(q,1,1), row(q,-1,-1)
    return {t: a[t]-b[t] for t in terms if a[t]-b[t]}
if __name__ == '__main__':
    q = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    e = expand(q)
    print("Δ(Q=%+d) = " % q + " ".join(f"{v:+d}·β_{t}" for t,v in e.items()))
    print("맹(blind)인 항: " + ", ".join(t for t in ['RD','QRD'] if t not in e))
