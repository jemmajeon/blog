#!/usr/bin/env python3
"""R23 게이트 교정 하네스.

R23: 게이트는 ①기지결함 코퍼스에서 모든 기지결함을 검출하고
     ②기지정상 구간에서 0건을 산출하는 것을 확인하기 전에는 채택하지 않는다.
     "작성했다"는 "작동한다"가 아니다.

근거: 이 세션에서 저자가 R18–R22를 작성한 직후, 자기 게이트가
      오음성 1종(E11)·오양성 1종(E12)을 냈다. 게이트를 만드는 행위도 오류의 대상이다.

기대값은 아래에 **명시**한다. 게이트를 고쳐 기대값을 맞추는 것은 허용되지만,
기대값을 고쳐 게이트를 맞추는 것은 금지한다 (R7 자기채점 금지의 연장).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gates'))
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

import manuscript_gate as MG
import cite_gate as CG
import build_manuscript as BM

FAILS = []
UNVERIFIED = []
def expect(name, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {got}" + ('' if ok else f"  (기대 {want})"))
    if not ok: FAILS.append(name)

def unverified(name, got, want, reason):
    """REG-014 처분 — 기대값은 그대로 두고, 그 규칙만 릴리스 게이트에서 제외한다.

    기대값을 고쳐 게이트를 맞추는 것은 여전히 금지다(R7). 여기서 바뀌는 것은
    기대값이 아니라 **게이트 소속**이며, 그 근거는 REVISION_POLICY REG-014의
    처분("L13은 미검증으로 표기하고 릴리스 게이트에서 제외")이다.

    R33 준수: 조용히 건너뛰지 않는다. 실제값·기대값·제외 사유를 모두 출력하고
    판정문에 미검증 항목으로 열거한다. 통과하면 PASS로 기록되므로
    나중에 R32가 구현돼 실제로 통과해도 이 표기가 그것을 가리지 않는다.
    """
    ok = got == want
    print(f"  {'PASS' if ok else 'XFAIL'}  {name}: {got}"
          + ('' if ok else f"  (기대 {want} — 미검증, 릴리스 게이트 제외)"))
    if not ok: UNVERIFIED.append(f"{name} — {reason}")

print("=== R23 게이트 교정 하네스 ===\n")

print("[0] 파이프라인 순서 — 게이트는 템플릿이 아니라 **빌드 산출물**에 돌린다")
print("    (산출방법 태그는 레지스트리가 소유하고 빌드가 주입하므로,")
print("     템플릿을 게이트하면 R21이 오양성을 낸다 — 이 하네스가 그것을 잡았다)")
built, berrs = BM.build('fixtures/clean_manuscript.md', 'fixtures/registry.json',
                        'fixtures/_built_clean.md')
expect('빌드 오류', len(berrs), 0)

print("\n[1] manuscript_gate — 기지정상 코퍼스 (빌드 산출물)")
r = MG.gate('fixtures/_built_clean.md', 'strict')
expect('R19 오양성', len(r['derived']), 0)
expect('R21 오양성', len(r['untagged']), 0)

print("\n[1b] manuscript_gate R18 — 템플릿 단계 (맨 숫자 금지는 집필 제약이다)")
r = MG.gate('fixtures/clean_manuscript.md', 'strict')
expect('R18 오양성', len(r['bare']), 0)

print("\n[2] manuscript_gate — 기지결함 코퍼스 (결함 10건 의도적 삽입)")
r = MG.gate('fixtures/defect_manuscript.md', 'strict')
expect('R18 맨 숫자 검출', len(r['bare']), 6)      # 0.71 380 0.61 0.1426 34x 15x
expect('R19 파생량 검출', len(r['derived']), 2)     # 34x cheaper, 15x faster
expect('R21 태그누락 검출', len(r['untagged']), 2)  # 보수적, 상한

print("\n[3] cite_gate (R20) — 기지답 인용 레지스트리")
oks, errs = CG.check('fixtures/citations.json', 'fixtures')
expect('참 인용 통과', sorted(oks), ['C1-TRUE', 'C2-TRUE'])
expect('거짓 인용 검출 수', len(errs), 4)
ids = [e.split(']')[0].lstrip('[') for e in errs]
for cls in ['C3-PARAPHRASE', 'C4-FABRICATED', 'C5-UNVERIFIABLE', 'C6-TOOSHORT']:
    expect(f'{cls} 검출', cls in ids, True)

print("\n[4] rule_check (R16) — 판정규칙 배타성")
import subprocess
rc = subprocess.run([sys.executable, 'rule_check.py'], capture_output=True, text=True)
# 기대값 변경 기록(R23): rule_check가 3개 규칙(v4/v5.0/v5.1)을 한 번에 검사하도록 재작성됨(E17 교정).
# 이전 기대 'returncode==1'은 v4 단독 검사 기준이었다. 새 기대는 패턴 전체.
expect('rule_check 종료코드(기대 패턴 충족)', rc.returncode, 0)
expect('v4 의미론 실패 검출', 'v4     의미론 위반' in rc.stdout and '실패' in rc.stdout.split('v4 ')[1].split('\n')[0], True)
expect('v5.0 라벨 오류 검출 (E17이 놓친 것)', '3825' in rc.stdout, True)
expect('v5.1 의미론 통과', 'v5.1   의미론 위반     0건' in rc.stdout, True)

print("\n[5] design_lint L13 (R9 기계화) — E23 교정 검증")
import shutil
shutil.copy('fixtures/l13_defect.md', 'design_v99.md')
rl = subprocess.run([sys.executable, 'design_lint.py', 'design_v99.md'], capture_output=True, text=True)
os.remove('design_v99.md')
expect('기지결함 픽스처(통과 확률 미계산 게이트) 차단', rl.returncode, 1)
expect('L13 위반 2건 검출', rl.stdout.count('L13 임계 셀'), 2)
rv = subprocess.run([sys.executable, 'design_lint.py', 'design_v5.md', '--baseline=v5.1', '--prev=design_v5.2.md'], capture_output=True, text=True)
expect('v5.3 (부록 E 보유) L13 통과', 'L13' in rv.stdout, False)
expect('L15 prev 파일 실존 (E27: 조용한 no-op 금지)', 'L15 직전 버전 파일 없음' in rv.stdout, False)
# E26: 공허한 부록 E 행 픽스처. 현 L13은 이것을 통과시킨다 — 기대값은 '차단'이며, 실패는 R23 미충족을 뜻한다.
shutil.copy('fixtures/l13_vacuous_row.md', 'design_v98.md')
rz = subprocess.run([sys.executable, 'design_lint.py', 'design_v98.md'], capture_output=True, text=True)
os.remove('design_v98.md')
# L13 자체가 잡아야 한다. 다른 규칙(L15 등)의 부수효과로 차단되는 것은 통과가 아니다 (E30: 거짓 PASS).
unverified(
    '공허한 부록 E 행("셀 정의"만)을 L13이 차단', 'L13' in rz.stdout, True,
    'REG-014/R32 — R9(작동특성 없는 장치 금지)는 산문 린트로 기계화할 수 없다. '
    '문구 근접·문구 화이트리스트·등록표 화이트리스트 3회 구현이 모두 항진명제였다. '
    '검사 가능한 형태는 PW-2 산출물 해시 실존 확인(R32)뿐이며 아직 미구현이다.')

print("\n" + "=" * 46)
if UNVERIFIED:
    print(f"미검증 {len(UNVERIFIED)}건 — 릴리스 게이트에서 제외 (REG-014):")
    for u in UNVERIFIED: print(f"   · {u}")
    print()
if FAILS:
    print(f"판정: 게이트 세트 **미채택** — {len(FAILS)}개 기대값 불일치")
    for f in FAILS: print(f"   · {f}")
    sys.exit(1)
print("판정: 릴리스 게이트 대상 규칙은 R23 충족 — 채택 가능")
if UNVERIFIED:
    print(f"     단, 위 미검증 {len(UNVERIFIED)}건은 '통과'가 아니라 '검사하지 못함'이다.")
print("한계: 기대값은 픽스처에 대한 것이다. 실제 원고의 미지 결함을 잡는다는 보장이 아니다.")
