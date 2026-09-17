# 인수인계 — 로컬 PC(VS Code Claude Code + Gemini CLI)로 이어받기

브랜치: `claude/fervent-hypatia-kuzrkp` · 디렉토리: `research/paper-validity/` · 마지막 커밋 시점 상태는 아래 그대로다.

## 현재 상태 (있는 그대로)
- 설계 `design_v5.md`(= v5.3): 독립 공격 4라운드·16기 → **FATAL 1 · MAJOR ~14 → ≤ 80**. 다섯 버전 연속. **더 고치지 말 것** — 두 라운드가 반대 처방을 낸 조항이 있고(R31), 재작성이 점수를 올린 적이 없다.
- `validate_gates.py`: **미채택**(L13이 공허한 부록 E 행을 통과시킴). **CI는 빨간 것이 정상이다.** 초록으로 만들려고 기대값이나 린터를 느슨하게 하면 그것이 E23의 재발이다.
- `ERROR_LEDGER.md`: 저자(Claude) 오류 30건. 분모는 관측 불가.
- 공격 발견 ~70건 중 **Claude가 독립 재현한 것은 6건뿐**. 나머지는 에이전트 보고를 인용 대조만 했다.

## 로컬에서만 할 수 있는 것 (우선순위 순)

### 1. Gemini를 R22의 "독립 실행 경로"로 쓴다 — 가장 가치 있음
이 세션에서 못 한 것. 같은 모델 계열(Claude)의 에이전트끼리 검증한 결과는 상관된 오류를 공유한다.
Gemini CLI에 줄 것: `R11_findings.md`~`R14_findings.md`의 발견 각각에 대해 **`design_v5.md` 원문을 열고 인용이 실존하는지, 실패 시나리오가 성립하는지** 판정하게 한다. 특히:
- Claude가 재현하지 않은 ~60건 → 참/거짓/판정불가 3분류
- `ERROR_LEDGER.md` 30건 → "이것이 실제로 오류였는가" 재판정 (Claude가 자기에게 과하게 또는 덜 엄격했을 수 있다)
- 결과는 새 파일 `GEMINI_REVERIFY.md`로. **Gemini의 판정도 인용 없는 항목은 폐기**(S3 규칙 동일).

### 2. `paper_lint.py`를 실제 코퍼스에 돌린다
저장소에는 논문 원문이 없다(재배포 회피). 로컬에 `jmiao24/Paper2Agent`를 클론하면
`skills/paper2agent/paper2agent-paper/references/paper.md` + `supplement.md`가 있다.
`cat paper.md supplement.md > both.md && python3 paper_lint.py both.md` → 5건(F1·F2·C1·U1·U2) 나와야 한다. 안 나오면 README의 주장이 틀린 것이다.

### 3. R32 — PW-2 시뮬레이션을 실제로 구현한다
L13이 3번 항진명제였던 이유: "작동특성이 계산됐다"를 산문으로 검사할 수 없다.
부록 D 모형을 코드로 구현해 PW-2 곡면을 실제로 산출하고, 임계 셀마다 출력 파일 해시를 부록 E에 넣는다. 린터는 해시 실존만 본다. **시뮬레이션이 돌기 전에는 통과 못 하는 것이 의도다.**
R14-A F1이 지적한 대로 μ 재해석 규칙과 §6 거부 조건이 상쇄되어 귀무 배치가 생성 불가하다 — 구현하면 그 결함이 즉시 드러날 것이다. 그게 이 작업의 가치다.

### 4. 로컬 스킬·MCP로 할 만한 것
- `/code-review` 를 `gates/*.py`·`design_lint.py`에 — 린터 자체의 버그(E9·E14·E16·E27 계열)
- 문헌 MCP가 있으면 `cite_gate.py`의 실제 검증 대상(Kaplow 1992, Lakens 2017, Schuirmann 1987 등 REVISION_POLICY에 인용된 근거)을 축자 대조 — Claude가 E10에서 Kaplow를 반대로 요약한 전력이 있다

## 하지 말 것
- 점수를 올리려고 v5.4를 쓰지 말 것. 먼저 1번(독립 재검증)으로 발견 목록을 정제하라.
- `validate_gates.py`·`design_lint.py`의 기대값·정규식을 **문서에 맞춰** 고치지 말 것 (R23).
- 에이전트(Claude든 Gemini든)의 보고를 인용 대조 없이 대장에 올리지 말 것 (S3).
- API 키를 채팅에 붙이지 말 것. 환경변수로.

## 첫 명령 (로컬 Claude Code)
```
git fetch origin claude/fervent-hypatia-kuzrkp && git checkout claude/fervent-hypatia-kuzrkp
cd research/paper-validity && python3 validate_gates.py   # 미채택이 나와야 정상
cat HANDOFF.md PROTOCOL.md
```
## 첫 프롬프트 (Gemini CLI)
> `research/paper-validity/design_v5.md`를 읽어라. 그 다음 `R14_findings.md`의 발견 각각에 대해, 인용된 문장이 design_v5.md에 실제로 있는지 확인하고, 실패 시나리오가 그 문장에서 성립하는지 참/거짓/판정불가로 판정하라. 인용이 없는 발견은 "인용 없음"으로 표시하고 판정하지 마라. 결과를 표로.
