# Paper2Agent 논리구조 감사 — 최종 보고 (S4: 치명도 등급)

**대상**: Miao et al., "Reimagining research papers as interactive and reliable AI agents", Nature (2026-09-16), DOI 10.1038/s41586-026-11044-y
**원문 출처**: 저자 저장소 `jmiao24/Paper2Agent` 내 `paper.md`(762줄) + `supplement.md`(2,085줄) + 보충표 2건
**방법**: 5개 축 병렬 에이전트 탐지(후보 25건) → 원문 직접 대조 적대적 검증
**합격선**: 신뢰도 95% = 숙련된 적대적 심사자가 실제 결함으로 동의할 추정 확률

---

## 등급 정의
| 등급 | 의미 |
|---|---|
| **치명(FATAL)** | 해당 주장·수치가 그대로는 성립 불가. 정정 필요 |
| **중대(MAJOR)** | 주장 범위 축소 또는 추가 실험 필요 |
| **경미(MINOR)** | 표현·보고 수준 |

---

## A. 게이트 통과 — 확정 결함 3건 (모두 치명)

### A-1. 실행하지 않은 실험에 결과 귀속 | 치명 | 신뢰도 96%
- 본문 Methods: "we injected **four** categories of execution-level errors" → "yielding **12** adversarial configurations"
- 보충 §8.1: "injected **four** categories" → "total of **12** adversarial configurations"
- 보충 §7: "we injected **six** categories of failures: … deprecated web APIs, and data format evolution"
- 보충 §7: "95.6%–98.3% accuracy **across all six** failure categories"

설계는 저장소 3 x 범주 4 = 12구성. 6범주면 18구성이어야 함. §7에만 등장하는 2개 범주는 Methods 설계에 부재하나 결과가 "6범주 전체"에 귀속됨. 양립 불가.

### A-2. 배수 주장 산술 오류 | 치명 | 신뢰도 97%
보충 §7 한 문장 내: "an average cost of $0.20 per query in 1.6 minutes, compared to $0.38 per query in 4.3 minutes … corresponding to a **2.8x cost reduction and 6.3x speedup**."

| 항목 | 논문 주장 | 실제 계산 | 과대 배율 |
|---|---|---|---|
| 비용 | 2.8x | 1.90x | 1.5배 |
| 속도 | 6.3x | 2.69x | 2.3배 |

### A-3. 오차막대 단위 모순 | 치명 | 신뢰도 95%
- 본문 Methods: "mean accuracy ± standard error (SE) **across questions** using a bootstrap procedure"
- 보충 §4 (튜토리얼·개방형 rubric 모두): "Mean accuracy and standard error are reported **across the 5 runs**"
- Figure 2 범례: "Data are mean ± s.e.m.; **n=5 independent runs**"

산술 재구성: 실행별 {15,15,15,15,14}/15 → 평균 98.67%, 실행간 SE = **1.33%** (논문 보고값 98.7% ± 1.3%와 소수 둘째자리 일치).
동일 정확도에서 질문(n=15) 부트스트랩 SE ≈ 2.96%.
→ Methods가 서술한 절차는 사용되지 않음.

**귀결**: 질문 집합이 5회 고정이므로 ±1.3%는 LLM 샘플링 잡음이며 일반화 불확실성을 담지 않음. "100.0% ± 0.0%"는 15문항에서 불확실성 0 주장(정확 이항 95% 하한 ≈ 78%). n=5·df=4 대응 t검정은 p<0.0001을 지탱 불가. **모든 유의성 주장의 재계산 필요.**

---

## B. 게이트 미달 — 구조적 중대 결함 (사실관계는 확정)

### B-1. 4중 순환 + 베이스라인 비대칭 | 치명급 | 사실 99% / 결함판정 89%
양 팔 프롬프트 원문 대조:
- **Paper2Agent 팔(전문)**: "Please answer the following question using the AlphaGenome MCP tools available to you. Question: {question}" — 금지 조항 **없음**
- **Claude+Repo 팔**: "Do NOT simply provide answers based on documentation or examples. **Do NOT provide answers from tutorial notebooks or the executed cells of ipython notebooks.**"

문제·정답의 출처:
- 보충 §4: "We manually curated 15 example queries **directly from the AlphaGenome tutorial**."
- 보충 §4: "Ground truth answers were obtained **directly from the executed tutorial notebooks**."
- Methods: test-verifier-improver가 "the tutorial's own example data as ground truth"로 테스트 생성, 함수당 최대 6회 수정, 실패 도구는 삭제.

→ 도구·테스트·문제·정답이 모두 동일 튜토리얼 1개 출처이고, 베이스라인만 그 자료 사용을 금지당함.
→ **미달 사유**: 금지 조항이 "베끼지 말고 실제 계산하라"는 정당한 통제라는 반론이 성립. 저자의 shortcut-learning 감사가 이를 일부 뒷받침.

### B-2. 검증 임계값 부재 | 치명급 | 사실 98% / 결함판정 85%
논문 Methods: "numerical results match tutorial outputs **exactly (with a 3% tolerance** …), … **perceptual hashing with Hamming distance < 20**"
공개 파이프라인 `paper2mcp/` 전수 검색: `3%` 0건, `Hamming` 0건, `perceptual` 0건. 실제 표현은 "**justified** floating-point tolerances"(수치 없음, LLM 재량).
"match **exactly** (with a 3% tolerance)"는 표현 자체가 자기모순 — 동일 코드·데이터 재실행은 1e-12로 일치해야 하므로 3%는 부동소수점 잡음이 아님.
→ **미달 사유**: 공개 저장소가 논문 시점 이후 리팩터링됐을 가능성.

### B-3. 기타 중대 후보
| 발견 | 등급 | 신뢰도 |
|---|---|---|
| "novel" 질의가 동일 도구 인자 교체에 불과 → 튜토리얼(98.7%)보다 높은 100.0%±0.0%. CL:0000100이 양쪽 중복 | 중대 | 88 |
| 건선 발견: Results는 "autonomous", 보충 §9.2는 인간이 전략 선택 + 유전자 제외 규칙 오류 교정(보고 수치를 결정) | 중대 | 86 |
| Scanpy "without the need for manual curation" vs Methods에 인용된 인간 작성 프롬프트가 바로 그 동작을 지시 | 중대 | 84 |
| 91.2%는 74/100 생존분 한정 → 종단 67.5%. 탈락 26편 베이스라인 미측정 | 중대 | 82 |
| 개방형 벤치마크: 본문 30문항 vs 보충 채점절차 "across all **15** queries" | 중대 | 82 |
| SORT1 근거 1번(0.99982)이 경쟁 후보(0.99998)보다 낮음 | 중대 | 80 |
| 적대적 테스트가 실행 오류만 주입 — 조용한 과학적 오류 미검출 | 중대 | 78 |
| "에이전트화 용이성 = 재현성 척도" 정의적 순환 | 중대 | 70 |

---

## C. 기각된 후보 2건 (게이트 작동 증거)

1. **보충표 1 수치 불일치 주장 → 반증.** 41행 중 수치 서술 24행 전부 일치(불일치 0). rs653953 행: 열 -0.4417/-0.1347/-0.6009 vs 서술 "-0.442, -0.135, -0.601" 완전 일치. 에이전트가 인용한 숫자는 해당 행에 부재 — 환각.
2. **"100% 거부율 단일 수치 보고" 의혹 → 기각.** 보충 §7에 "under both prompted and unprompted conditions" 명시.

---

## D. 총평

확정 3건은 **논증 붕괴가 아니라 보고 무결성 붕괴**다. 논문의 착상과 기여를 무효화하지 않으며, 정정(erratum) 사안이다. 다만 A-3은 모든 유의성 주장의 재계산을 요구한다.

실질적으로 더 중대한 것은 게이트를 통과하지 못한 **B-1(4중 순환 + 베이스라인 비대칭)** 이다. 95% 기준을 지키기 위해 확정 목록에서 제외했으나, 사실관계는 프롬프트 원문 대조로 확정되었다.

공정을 위해: 이 논문은 방어가 촘촘하다. Discussion에 한계를, 보충 §9.2에 인간 개입 전부를 공개했고("the human investigator did not write, modify, or inspect any code"), ablation·적대적 테스트·shortcut 감사를 수행했다. 다수 후보가 "저자가 이미 인정함"으로 강등된 이유다.
