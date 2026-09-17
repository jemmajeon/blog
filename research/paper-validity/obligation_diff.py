#!/usr/bin/env python3
"""R15 의무 추적표 — 개정 전후 의무 집합의 차집합.
   의무 = 규범 술어(한다/않는다/금지/필수...)로 끝나는 절.
   유사도 기반이므로 후보를 내고, 최종 판정은 사람이 (a)유지 (b)의도적 폐기 (c)조용한 소실 로 표기한다.
   (c)가 1건이라도 있으면 릴리스 차단 (R15)."""
import re, sys, difflib

NORM = re.compile(r'(해야\s*한다|하지\s*않는다|않는다|한다|금지한다|허용한다|필수[이다로]|의무[이다로화])(?![가-힣])')

def obligations(path):
    t = open(path, encoding='utf-8').read()
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    t = re.sub(r'^\s*\|.*\|\s*$', '', t, flags=re.M)
    out = []
    for sent in re.split(r'(?<=[.。])\s+|\n', t):
        s = sent.strip(' -*>')
        if len(s) > 12 and NORM.search(s):
            out.append(s)
    return out

def keyset(s):
    return set(re.findall(r'[가-힣A-Za-z_]{2,}', s))

def diff(old, new, thr=0.45):
    O, N = obligations(old), obligations(new)
    nk = [keyset(n) for n in N]
    lost = []
    for o in O:
        ok = keyset(o)
        best = max((len(ok & k) / max(1, len(ok | k)) for k in nk), default=0)
        if best < thr:
            lost.append((best, o))
    return O, N, lost

if __name__ == '__main__':
    old, new = sys.argv[1], sys.argv[2]
    O, N, lost = diff(old, new)
    print(f"=== 의무 추적 (R15): {old} → {new} ===")
    print(f"  구 의무 {len(O)}건 / 신 의무 {len(N)}건 / 대응 없음(후보) {len(lost)}건\n")
    for b, o in lost:
        print(f"  [{b:.2f}] {o[:110]}")
