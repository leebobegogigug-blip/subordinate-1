# Subordinate–1 기획서 (5판)

- 상태: 기획 5판 · 2026-11-03. M0 정찰을 마쳤다 — 사용자가 사내에서 돌린 결과 6줄과 결정은 00 에 있다. **결정: PPTX 를 짓는 파이썬 도구는 만들지 않는다 (N)** — 미리 적은 '만들지 않을 기준' 을 기성품이 넘었고 사용자가 확정했다. 남기는 것은 인터뷰 · 보고 문법 · 질문 은행을 묶은 opencode 스킬과 결과물 `deck.md` 다. 01 – 10 의 4판 내용은 기록으로 남기고, 접은 절에는 머리에 5판 표시를 달았다. 갈린 결정은 부록 E – H. works 문서 링크는 works `main` 커밋 (`6c93377`) 으로 고정했다.
- 무엇: 원자료 (CSV · XLSX) 와 차트 그림 (PNG — 분석 도구 캡처 등) 을 받아, 사용자 인터뷰로 **현상 › 분석 › 의견** 을 채우고, 회사 PPT 템플릿에 맞춘 편집 가능한 PPTX 초안을 만드는 에이전트 플러그인.
- 표기: [실험] 이 세션에서 직접 잰 값 (GitHub 별 수 · 라이선스 · 최근 push 는 2026-11-03 GitHub 검색 API 조회) · [문헌] 저장소 문서 · README · 라이선스 파일 · 공개 문헌에서 읽은 것 · [추정] 계산하거나 늘린 값 · [미확인] 확인하지 못한 사실 · [제안] 근거 없이 정한 문턱 (M0 결과로 고친다).
- 번호: 목표 G1–G6 · 보고 문법 P-01–P-08 · 인터뷰 규칙 I-01–I-11 · 검사 V-01–V-10 · 정찰 KIT-1–KIT-6 · 리스크 대장 1–24 · 질문 Q1–Q10 · 열어 둔 것 U1–U4 · M0 결과 K1–K6 · 마일스톤 M0–M4 · 작업 T1–T23. [DEVELOP.md](https://github.com/leebobegogigug-blip/Works/blob/6c9337753f34f1ec747107e9a2bfe2ab47589171/docs/DEVELOP.md) 의 D-01–D-11 과 겹치지 않게 골랐다.

## 00 5판 — M0 결과와 결정

결과 (2026-11-03 · 사용자가 사내에서 돌린 M0 키트의 6줄 · 형식은 `kit/README.md`):

```text
K1 G 3.13 0
K4 Y 10 0 -
K5 ? 0 -
K2 G B O T 5
K3 Y 14 6 0
K6 N 100 4
```

| 줄 | 읽은 것 | 5판에 주는 것 |
|---|---|---|
| K1 | 사내 Python 3.13 · 필수 패키지를 모두 불러옴 | 파이썬 코드가 남는다면 최소 Python 은 3.13. 3.8 맞춤 제약 (AGENTS.md) 은 키트와 함께 거둔다 (T21) |
| K4 | 레이아웃 10 · 제목 + 본문/그림 자리표시자를 함께 가진 레이아웃 0 · 이전 판 없음 | 키트는 내용 (OBJECT) 자리표시자까지 센다 [실험: `kit/env/check_env.py` 의 `BODY_TYPES`] — 키트 탓이 아니라 템플릿이 자리표시자 대신 도형 · 글상자로 짜였다 [추정]. 자리표시자에 끼워 넣는 방식은 이 템플릿에서 안 통한다 (리스크 10 현실화) |
| K5 | 복구 대화상자 없이 열림 · 판정 · 넘침 칸은 비움 | 열림은 통과. 넘침은 미확인 (U4) |
| K2 | 그림은 `modalities` 를 넣어야 닿음 (B) · 셸 도구 호출 됨 · 질문은 선택 화면 대신 글 목록 · deck-lite 구조 5/5 | `modalities` 는 설치의 필수 단계. 질문은 번호 목록으로 묻는다. 사내 LLM 은 정해 준 형식을 지킨다 |
| K3 | 범주 14/17 (초록) · 숫자 6/9 (노랑) · 정답 파일 안 봄 | 그림은 '무엇이 보이나' 까지 맡긴다. 그림에서 읽은 숫자는 후보로만 (I-06 그대로) |
| K6 | 결정 N · 가장 잘한 기성품 갈래 G2 100% · G3 4점 | 미리 적은 '만들지 않을 기준' (`kit/baseline/README.md`) 을 넘었다 |

- **결정 — 만들지 않는다 (N).** 미리 적은 기준대로이고 사용자가 확정했다 (2026-11-03). 06 · 07 의 파이썬 빌드 도구 (profile · images · template · build · validate · render) 와 작업 T5 – T15 는 접는다.
- **남기는 것 — 프롬프트 묶음 (opencode 스킬).** 인터뷰 (05 · I-01 – I-10) · 보고 문법 (04 · P-01 – P-08) · 질문 은행 (부록 B) 을 opencode 의 스킬 · 명령 · 에이전트로 묶는다. 결과물은 `deck.md` 하나 — 현상 › 분석 › 의견 순서, 장마다 한 문장 제목, 그림마다 근거 줄, 문장마다 종류 (사실 · 해석 · 의견 · `[미확인]`) 와 출처 id 를 적은 마크다운이다. 사용자는 이것을 Presenton 에 붙여 넣거나 pandoc 으로 PPTX 로 바꾼다. 파이썬 실행 의존은 없다 (RULES.md › W-02 를 다시 고친다 — T21).
- **판정의 구멍 — 기록.** 4판의 판정 기준과 6줄 양식에는 세 칸이 없었다: 이긴 갈래 (Presenton · pandoc) · Presenton 을 두 번 돌려 둘 다 통과했는지 · 기준선 장표가 회사 템플릿 위였는지. 사용자는 셋을 답하지 않고 N 을 확정했다. 그래서 남기는 것을 셋 어느 경우에도 쓰이는 모양 (`deck.md` 하나로 두 기성품) 으로 정했고, 셋은 10 › 5판에서 열어 둔 것 (U1 – U4) 으로 둔다. 이 구멍은 기준을 설계한 기획의 실수다 — 다음 판정 기준에는 '회사 템플릿 위에서' 와 '누가 내용을 썼나' 를 넣는다.
- **알려진 한계.** 회사 템플릿 맞추기 (K4) 는 이 묶음이 풀지 않는다. 기성품이 회사 템플릿을 받는지, 손으로 옮기는 데 얼마나 드는지는 T22 시범에서 잰다 (리스크 23).
- **다음** — 부록 C 의 T16 – T23: `deck.md` 형식 › 스킬 · 명령 · 에이전트 › 기성품에 넣는 법 · 설치 › 적대 검토 › README · 그림 갱신 › 사내 시범 › 키트 정리.

## 00-4 4판 한 장 요약 (기록)

> 5판: 아래는 4판의 요약이다. 빌드 도구에 관한 부분은 접었다 (00).

- **누구**: 데이터와 그림은 이미 있는데, 그것을 상사 · 유관 부서가 납득하는 보고 장표로 옮기는 데 시간이 드는 공정 · 설비 · 연구 엔지니어. Analysis–1 과 같은 사람이다.
- **핵심 결정 셋 (2026-11-03 사용자 답으로 확정)**
  1. **모양은 스킬 + opencode 어댑터 + 파이썬 도구 · 지금은 사내 LLM 전용.** 인터뷰 · 보고 문법 · 질문 은행은 `SKILL.md` 한 벌이고, opencode 에는 얇은 어댑터 — 전용 에이전트 (`agents/subordinate-1.md` · 권한) + 명령 (`/subordinate`) — 로 붙는다. 질문은 `question` 도구로 하고 [문헌: opencode docs › tools], 그림은 사내 LLM 이 본다 (사용자 답). 결정적 파이썬 도구가 데이터 사실 · 그림 보관 · 조립 · 검사를 맡고, LLM 은 좌표를 쓰지 않는다. opencode 의 JS 플러그인 (이벤트 훅) 은 쓰지 않는다. **Claude 는 나중에** — 회사가 엔터프라이즈 판을 들이면 사용자가 사내에서 어댑터를 더해 튜닝한다 (M5). 그때 비용이 작도록 지금 지키는 것은 둘뿐이다: `SKILL.md` 에 호스트 이름에 묶인 문장을 두지 않기 · `deck.json` 에 `meta.host` 칸 두기.
  2. **자리는 works 밖 별도 저장소 (Q1).** works 규칙을 채택하되 W-02 를 '고정 의존 목록' 으로 바꾼다 (02). 사내 PC 에서 pip 설치가 되므로 (Q5) python-pptx · pandas · openpyxl · matplotlib · scipy 를 실행 의존으로 쓴다. Analysis–1 과는 코드 · 형식 · 일정을 아예 나누지 않는다 (Q4).
  3. **보고 문법이 제품이다.** 장마다 제목 = 한 문장 주장, 몸통 = 증거 하나. 문장마다 종류 (사실 · 해석 · 의견 · 미확인) 와 근거 id 가 붙는다. 의견은 사용자 입에서만 나온다. 근거에 묶이지 않은 숫자는 장표에 들어가지 못한다 (Report–1 의 근거 칩 개념 — 코드 공유 아님).
- **가져다 쓰는 것** (03 판정): 실행 = python-pptx · pandas (+ openpyxl) · matplotlib · scipy. 설계 차용 = SciencePlots (스타일 파일을 고지와 함께 옮겨 회사 팔레트로 튜닝) · ppt-master (닫힌 중간 언어 + 검사 게이트) · superpowers brainstorming (보기 전에 묻지 않기 · 한 번에 한 질문) · academic-pptx-skill (행동 제목 · ghost deck test) · CyberPPT (증거표 먼저 · 게이트 실패 시 납품 금지) · K-Dense scientific-slides (그림 원본 보존) · PPTAgent (참고 장표 분석 · 평가 축). **쓰지 않음** = Anthropic pptx 스킬 (2차 저작 · 재배포 금지 라이선스 [문헌]) · AGPL 묶음 (PPTist · WebPlotDigitizer · banana-slides …).
- **가장 큰 위험 셋**: ① opencode 가 사내 모델에 그림을 실제로 넘기는가 (사용자 정의 provider 의 `modalities` 설정 [문헌: opencode 소스] · 그림 자동 축소) 와 사내 LLM 이 판독 · 도구 호출 · 질문 도구를 얼마나 해내는가 ② 개발 고리가 끊겨 있다 — 이 도구를 짓는 개발 세션 (Claude Code) 은 사내 LLM 도 사내 PC 도 회사 템플릿도 못 본다. 인터뷰 품질 · 템플릿 매핑 · Office 열림은 사용자가 사내에서 돌린 결과로만 확인된다 (리스크 22) ③ 엔지니어링 보고의 지어낸 원인 · 숫자 — 한 번 나오면 도구는 끝난다. 그래서 **M0 정찰 (앱 코드 0줄 · 1주 [추정] — pip 가능으로 줄었다)** 을 먼저 하고, 기성품 Presenton (사내 LLM 연결 가능 [문헌]) 을 같은 자료로 돌려 **만들지 않을 기준** (08) 부터 판정한다.

## 01 문제 · 목표 · 비목표

### 문제

- 엔지니어의 보고 PPT 는 대개 "그림 붙이기 · 그림마다 한 문장 · 결론 쓰기 · 양식 맞추기" 다. 시간이 드는 곳 [추정 — KIT-6 에서 잰다]: ① 그림을 골라 이야기 순서를 정하기 ② 그림마다 "그래서 무엇" 한 문장 ③ 현상 · 해석 · 의견이 섞이지 않게 쓰기 ④ 회사 양식.
- 별 많은 AI PPT 도구 (03) 는 주제 · 문서에서 **보기 좋은** 장표를 만든다. 엔지니어 보고에 필요한 것은 반대 방향이다: 그림은 원본 그대로, 숫자는 근거 그대로, 원인은 말한 사람이 말한 만큼만.

### 목표 (잴 수 있게)

| # | 목표 | 재는 법 | 문턱 [제안] |
|---|---|---|---|
| G1 | 자료 → 첫 초안이 빠르다 | CSV 1개 + 그림 5장, 인터뷰 포함 | 20분 안 · 손 작업의 1/3 이하 (손 작업 시간은 KIT-6) |
| G2 | 장표의 숫자가 모두 근거에 묶인다 | V-03 통과 | 100% (`직접` 표시로 사람이 책임진 것 포함) |
| G3 | 제목만 이어 읽어도 현상 › 분석 › 의견 이야기가 된다 | ghost deck 사람 판정 (5점) | 4 이상 |
| G4 | 사용자가 고칠 것이 적다 | 초안 대비 고친 글자 비율 | 30% 이하 |
| G5 | 사내 PowerPoint 가 복구 대화상자 없이 연다 | KIT-5 · 실제 보고 3건 | 3/3 |
| G6 | 묻는 것이 적다 | 인터뷰 질문 수 · 데이터가 답하는 것을 물은 수 | 12개 이하 · 0 |

### 비목표

- 분석 도구가 아니다. 분석은 Analysis–1 · 기존 분석 도구가 한다. 프로파일은 "보고에 쓸 사실" 을 뽑는 데까지다.
- 디자인 생성기가 아니다. 이미지 생성 · 아이콘 · 애니메이션 없음. 회사 템플릿이 디자인이다.
- 받은 그림을 다시 그리거나 보정하지 않는다. 원자료로 새 그림을 그리는 것은 사용자가 고를 때만이다.
- 결론을 대신 내리지 않는다.

## 02 works 와의 관계 — 규칙 채택표

works 밖 별도 저장소로 정했다 (Q1 · 2026-11-03). 그래서 1판의 W-02 충돌 (works 안이면 python-pptx 등이 `works_check.py --strict` 에 걸린다) 은 생기지 않는다. works 헌법이 이 도구를 직접 묶지는 않고, 새 저장소가 아래 표대로 스스로 따른다 (Analysis–1 의 AN 표 방식). 표는 이 저장소 `RULES.md` 의 원고다 (T6).

| 조항 | 이 도구에서 | 채택 |
|---|---|---|
| W-01 | 저장소 하나 = 도구 하나. 모양은 스킬 + opencode 어댑터 + 파이썬 패키지 (06) | 자리에 맞게 옮김 — README · INSTALL · MANUAL · tests · 워크플로 필수 |
| W-02 | python-pptx (lxml) · pandas · openpyxl · matplotlib · scipy 를 실행에 쓴다. pip 설치 가능 (Q5) | **바꿈** — 고정 의존 목록 (버전 고정 · `requirements.txt` · 라이선스 허용 목록). 선택 기능은 렌더 검사 (PowerPoint COM `pywin32` · LibreOffice) 뿐 — 없으면 그 기능만 꺼진다 |
| W-03 | 도구 (파이썬) 는 네트워크를 쓰지 않는다. LLM 통신은 opencode 가 사내 LLM 과 한다 | 채택 — 부딪힘 없음. 이 도구를 짓는 개발 세션 (Claude Code · 회사 밖) 에는 합성 자료만 넣는다 (리스크 8) |
| W-04 | 도구는 키를 다루지 않는다 (호스트가 다룬다) | 채택 |
| W-05 | 인터뷰 답 원문 · 그림 | 채택 — 도구 쪽은 확정한 `deck.json` 만 저장. opencode 는 대화를 `%USERPROFILE%\.local\share\opencode\opencode.db` 에 남긴다 [문헌: opencode docs › troubleshooting]. 알려진 한계로 적고 지우는 법을 MANUAL 에 둔다 (리스크 9) |
| W-06 | 템플릿 · 매핑 · 설정은 `%LOCALAPPDATA%\subordinate-1\` · 형식 버전 · 원자적 쓰기 · 테스트는 `SUBORDINATE_HOME` 으로 데이터 폴더를 바꾼다 | 채택 |
| W-07 | 템플릿 등록 · PPTX 저장은 미리보기 › 확정. 결과 파일은 덮어쓰지 않는다 | 채택 |
| W-08 | INSTALL 은 opencode 가 따라 하는 절차 — 설치 · 업데이트 · 제거 | 채택 |
| W-09 | 이름을 바꾸면 데려간다 | 채택 — 이름은 `subordinate-1` (화면 Subordinate–1 · Q6). 공개 저장소에 올린 뒤에는 바꾸지 않는다 |
| W-10 | 산출 PPTX 는 회사 템플릿의 색을 쓴다 (Q3) | 채택 + 해석 — 도구의 문서 · 그림은 works DESIGN, 산출물은 사용자 템플릿이 정한다 (Analysis–1 의 AN-09 와 같은 갈래) |
| W-11 | CI · unittest · 검증 가능한 숫자만. 도구가 LLM 을 부르지 않아 가짜 서버는 거의 필요 없다 | 채택 |
| W-12 | 회사 템플릿 · 로고 · 실데이터 · 실제 장표 금지 · 예시 · 테스트는 합성만 | 채택 — 공개 저장소다 (Q9). 저장소 라이선스는 MIT (Q10 · `LICENSE`) — 차용한 코드의 고지는 따로 둔다 |

- works 쪽에 바꾼 것: 설치 자리를 `D:\OPENCODE\subordinate-1` 로 골라 (Q7) works `.gitignore` 에 `/subordinate-1/` 한 줄을 넣었다 (`/analysis-1/` 선례 · works 커밋 따로). 그 자리에 표준 라이브러리 밖 import 를 둔 빈 뼈대를 만들어, works 검사기가 앱으로 세지 않고 (위반 0) `git status` 가 깨끗한 것을 확인했다 [실험]. 그 밖에는 없다.

## 03 자료조사 — GitHub 도구 지도

- 방법: GitHub 검색 API 로 별 수 · 라이선스 · 최근 push 를 쟀고 [실험: 2026-11-03], 핵심 후보는 README · `SKILL.md` · 요구 패키지 · 라이선스 파일을 직접 읽었다 [문헌]. 별 수는 인기이지 품질이 아니다 — 판정은 아래 넷 중 하나다.
- 판정: **채택** (실행 의존) · **차용** (설계 · 규칙 · 프롬프트 — MIT/Apache 면 문장을 인용하고 고지) · **기준선** (같은 자료로 비교 실험) · **금지** (복사 · 묶음 금지).

### A. AI 장표 생성기 · 에이전트 스킬

| 저장소 | ★ | 라이선스 | 최근 push | 무엇 | 판정 · 까닭 |
|---|---:|---|---|---|---|
| `hugohe3/ppt-master` | 72,587 | MIT | 2026-11-02 | 문서 → 네이티브 PPTX. SVG 를 닫힌 중간 언어로 쓰고 검사기 › 변환기 › 품질 보고 게이트. Claude Code 플러그인 마켓 지원 | **차용** (중간 언어 + 검사 게이트 + 작업 기록). 실행은 안 씀: Python 3.10+ · 의존 19개 (numpy · PyMuPDF · skia-pathops · uharfbuzz · flask …) [문헌: requirements] 라 사내 PC 위험이 크고, LLM 이 기하를 쓰게 해 강한 모델이 필요하다 (README 의 권장 모델) |
| `presenton/presenton` | 11,635 | Apache-2.0 | 2026-11-02 | 셀프호스팅 AI 발표 생성기 · Windows 데스크톱 앱 · OpenAI 호환 LLM · 자기 PPT 디자인 [문헌] | **기준선** — KIT-6 에서 같은 자료로 돌려 '만들지 않을 기준' 을 판정 |
| `icip-cas/PPTAgent` | 5,190 | MIT | 2026-11-02 | EMNLP 2025 · 참고 장표 분석 › 편집으로 생성 · PPTEval (내용 · 디자인 · 일관성) · Claude Code / Codex / OpenCode 스킬 | **차용** (평가 축 · 참고 장표 분석). 실행은 안 씀: Linux · WSL · macOS + uv + npm + LibreOffice 요구 [문헌] — Windows 사내 PC 에서 바로 못 돈다 |
| `K-Dense-AI/scientific-agent-skills` › scientific-slides | 55,832 | MIT | 2026-11-02 | 과학 발표 스킬. 결과 장표는 편집 가능 PPTX, 원본 그림은 그대로 넣거나 원자료로 결정적으로 다시 그린다 | **차용** (그림 원본 보존 규칙 P-08). 실행은 안 씀 (Python 3.12+ · 외부 이미지 생성 API) |
| `Gabberflast/academic-pptx-skill` | 1,429 | MIT | 2026-07-14 | 행동 제목 · SCR 논증 · ghost deck test · 결과 장표당 증거 하나 · 결론 장표로 끝냄 | **차용** (보고 문법 04 의 뼈대) |
| `crazyykhllc-bit/CyberPPT` | 1,848 | MIT | 2026-07-20 | 증거표 먼저 › 줄거리 › 장별 계획 › 게이트 (구조 · 넘침 · 편집성) | **차용** (증거표 먼저 · 게이트가 하나라도 실패하면 납품하지 않음) |
| `GongRzhe/Office-PowerPoint-MCP-Server` | 1,861 | MIT | 2025-12-31 | python-pptx 를 MCP 도구로 | 참고. v1 은 명령줄 도구로 충분 |
| `anthropics/skills` › pptx | 186,768 (저장소) | pptx 스킬은 "All rights reserved" · 복제 · 2차 저작 · 재배포 금지 [문헌: `skills/pptx/LICENSE.txt`] | 2026-10-28 | html2pptx · 템플릿 편집 | **금지** (복사 · 개조 · 묶음 모두). K-Dense 도 같은 까닭으로 뺐다 [문헌: K-Dense README 2.72.0] |
| `pipipi-pikachu/PPTist` · `Anionex/banana-slides` · `op7418/guizang-ppt-skill` · `chuspeeism/dashi-ppt-skill` | 9,455 · 15,937 · 29,155 · 10,286 | AGPL-3.0 | 2026 | 웹 편집기 · AI 장표 · HTML 장표 | **금지** (섞으면 공개 의무가 번진다) |
| `GordenSun/GordenPPTSkill` · `BMAD-METHOD` · `pandas-ai` | 3,866 · 54,906 · 23,924 | 표기 없음 · NOASSERTION | — | — | **금지** (라이선스 불명은 쓰지 않는다) |

### B. PPTX 를 쓰는 라이브러리 · 변환기

| 저장소 | ★ | 라이선스 | 최근 push | 판정 · 까닭 |
|---|---:|---|---|---|
| `scanny/python-pptx` | 3,579 | MIT | 2024-08-07 | **채택** (렌더러 핵심 — 슬라이드 마스터 · 레이아웃 · 자리표시자 · 네이티브 차트 · 표 · 노트). 위험: 2024-08 이후 push 없음 [실험] → 버전 고정 · 얇은 어댑터 한 겹 (리스크 12) |
| `gitbrent/PptxGenJS` | 6,345 | MIT | 2025-11-28 | 쓰지 않음. Anthropic · K-Dense 스킬이 쓰지만 Node 가 사내 PC 에 있다는 보장이 없다 [미확인]. 실행 언어를 파이썬 하나로 둔다 |
| `jgm/pandoc` · `quarto-dev/quarto-cli` | 46,787 · 6,149 | GPL-2.0 · NOASSERTION (GitHub 표기) | 2026-11-02 | **기준선 후보** (마크다운 → pptx, `reference-doc` 로 회사 템플릿). 묶지 않는다 — 설치 크기 · GPL |
| `marp-team/marp` · `slidevjs/slidev` · `hakimel/reveal.js` | 12,710 · 49,334 · 72,509 | MIT | 2026 | 범위 밖. HTML 발표이고 PPTX 는 장마다 그림이라 편집이 안 된다 (marp 의 편집 가능 내보내기는 실험 기능 · LibreOffice 필요 [미확인]) |
| `MartinPacker/md2pptx` | 516 | MIT | 2026-10-26 | **차용** (마크다운 › 레이아웃 매핑 아이디어). 별이 적어 실행 의존으로는 안 씀 |
| `microsoft/markitdown` · `docling-project/docling` | 193,593 · 70,026 | MIT | 2026 | 선택 (M4) — 지난 보고서 · 회사 장표를 읽어 목차 · 문체를 배우는 데 |

### C. 데이터 · 그림

| 저장소 | ★ | 라이선스 | 판정 · 까닭 |
|---|---:|---|---|
| `matplotlib/matplotlib` · `garrettj403/SciencePlots` | 23,413 · 9,363 | matplotlib 자체 라이선스 · MIT | matplotlib **채택** (원자료로 다시 그릴 때) · SciencePlots **차용** — 공학 · 과학 스타일 파일의 필요한 부분을 MIT 고지와 함께 옮겨 회사 팔레트 · 글꼴로 튜닝한다 (의존 하나를 줄인다) |
| pandas · `pola-rs/polars` · `duckdb/duckdb` | — · 40,254 · 42,754 | BSD · MIT · MIT | pandas + openpyxl (XLSX 읽기) **채택**. Analysis–1 과 아예 별개라 엔진을 맞추지 않는다 (Q4) |
| `scipy/scipy` · `statsmodels/statsmodels` | 15,179 · 11,735 | BSD-3 | scipy **채택** — v1 은 검정 · 효과 크기만 [제안]. statsmodels 는 쓰지 않는다 |
| `microsoft/data-formulator` · `microsoft/lida` | 17,652 · 3,288 | MIT | **차용** — LIDA 의 "데이터 요약 › 목표 후보" 를 현상 후보 질문 생성에 쓴다. LIDA 는 2024-08 이후 push 없음 [실험] |
| `automeris-io/WebPlotDigitizer` | 3,181 | AGPL-3.0 | **금지** (묶지 않음). 사용자가 따로 쓰는 것은 자유 |
| 그림 판독 모델 (DePlot 류) | — | — | 쓰지 않음 — torch 무게. 그림의 뜻은 비전 LLM 또는 사용자 답에서 받는다 |
| works 의 Ascii–1 (선 차트 · 웨이퍼 맵 PNG → 글자) | — | works | 사내 LLM 이 그림을 보므로 (사용자 답) 다리로는 필요 없다. 웨이퍼 맵의 작은 점 개수처럼 비전 판독이 약할 수 있는 곳의 보조로만 KIT-3 에서 비교한다. 코드는 복사하지 않고 명령으로만 부른다 (W-01 의 정신) |

### D. 인터뷰 · 작업 흐름

| 저장소 | ★ | 라이선스 | 판정 · 까닭 |
|---|---:|---|---|
| `obra/superpowers` › brainstorming | 311,233 | MIT | **차용** — 보기 전에 묻지 않는다 · 한 번에 한 질문 · 첫 질문은 답이 결과를 가장 크게 바꾸는 것 (I-01 · I-02) |
| `github/spec-kit` | 145,504 | MIT | **차용** — 빈칸을 명시하고 그 목록을 질문으로 바꾸는 clarify 단계 (I-08) |
| `anomalyco/opencode` | 224,109 | MIT | **호스트** (사용자 답 · Claude 는 M5) — 에이전트 (`agents/` · 파일 이름 = 에이전트 이름 · 권한) · 명령 (`commands/` · `$ARGUMENTS`) · 스킬 (`skills/`) · `question` 도구 (머리 · 질문 · 선택지 · 직접 입력) · 그림 첨부 자동 축소 (기본 2000×2000 · base64 5,242,880 바이트 · `attachment.image`) [문헌: docs › agents · commands · skills · tools · config] |

### 조사에서 얻은 결론

1. 2026년의 AI PPT 생태계는 **에이전트 스킬 + 결정적 스크립트** 로 모였다 (ppt-master · PPTAgent · K-Dense · CyberPPT 모두). 이 모양을 따른다.
2. 별이 많은 것은 거의 다 디자인 · 이미지 생성 쪽이다. **근거 추적 · 현상/분석/의견 문법에 특화된 공개 도구는 찾지 못했다** — 'assertion evidence slides' 검색의 최고가 45★ 템플릿 저장소다 [실험]. 빈자리다.
3. **라이선스가 첫 관문이다.** 가장 유명한 pptx 스킬 (Anthropic) 은 재사용 금지이고, 장표 생성기 상위권에 AGPL 이 많다. 허용 목록 (MIT · BSD · Apache-2.0 · PSF · matplotlib) 밖은 들이지 않는다.
4. 실행 의존의 핵심은 python-pptx 다. 사내 PC 에서 pip 가 되므로 (Q5) pandas · matplotlib · scipy 도 실행 의존으로 둔다 — 선택 기능은 렌더 검사 (PowerPoint COM · LibreOffice) 뿐이다.

## 04 보고 문법 — 현상 › 분석 › 의견

근거 [문헌]: Assertion-evidence 장표 (Michael Alley — 제목 = 한 문장 주장, 몸통 = 시각 증거. 공학 교육에서 이해도가 더 높았다는 실험: Garner & Alley 2013, International Journal of Engineering Education [원문은 이 세션에서 다시 확인하지 않음]) · Minto 피라미드 / SCR (결론부터) · Kepner-Tregoe 문제 분석의 Is / Is-Not (현상의 범위) · 8D (D2 문제 기술 · D4 근본 원인 · D5–D7 조치) · Claim-Evidence-Reasoning (주장 · 증거 · 추론을 나눠 쓴다) · Naegle 2021 "Ten simple rules for effective presentation slides" (PLOS Computational Biology).

### P-01 문장의 종류

| 종류 | 뜻 | 근거 (필수) | 장표에서 |
|---|---|---|---|
| 사실 | 데이터 · 그림이 직접 말하는 것 | facts id (`f012`) 또는 그림 id (`img3`) | 표시 없음 |
| 해석 | 사실을 이어 내린 판단 | 사실 id 둘 이상 + 추론 한 줄 | 노트에 추론 · 검토판에서 `해석` 칩 |
| 의견 | 사람의 판단 · 제안 · 요청 | 인터뷰 답 id (`a07`) — 사용자 진술만 | 의견 절에만 |
| 미확인 | 필요한데 자료도 답도 없음 | — | `[미확인]` 을 장표에 그대로 남긴다 |

- LLM 이 쓴 의견 · 근거 없는 사실은 `ERR` — 빌드가 막힌다 (V-02).

### 장표 규칙

- **P-02** 제목은 완결된 한 문장 주장이다 (40자 안 [제안] · 숫자 하나 이상 권장). "데이터 분석" 같은 주제어 제목은 쓰지 않는다.
- **P-03** 결과 장표 하나 = 증거 하나 (그림 또는 표). 그림 둘은 비교일 때만.
- **P-04** 그림 아래 근거 줄: 출처 파일 · 기간 · n (lot · wafer 등 단위를 밝혀) · 필터 · 집계 수준 · 검정. Analysis–1 08 의 근거 줄과 같은 모양이다 [문헌] — 칩이 사라진 출력물에서도 상사의 첫 질문 (몇 개 · 언제부터 · 무엇을 걸렀나) 에 그림이 스스로 답한다.
- **P-05** 순서: 요약 › 현상 › 분석 › 의견 › 한계 · 다음. 분석 절은 가설마다 증거 › 판정 (지지 · 기각 · 미정).
- **P-06** Ghost deck test: 제목만 뽑아 이어 읽어도 이야기가 된다. 빌드 전에 제목 목록을 사용자에게 먼저 보인다.
- **P-07** '확인하지 못한 것' 장은 지울 수 없다 (숨기기만 · 부록에 남는다). Analysis–1 의 반론 절 원칙과 같다 — 설득은 약점을 먼저 꺼낼 때 강하다.
- **P-08** 그림 원본 보존: 받은 그림은 픽셀 그대로 (크기 조절만). 화살표 · 강조 상자 · 주석은 PPT 도형으로 그림 위에 얹는다.

### 기본 뼈대 — 보고 유형 셋 [제안]

| 절 | 이상 보고 (문제 발생) | 실험 결과 보고 | 정기 · 진척 보고 |
|---|---|---|---|
| 요약 | 결론 한 줄 · 현상 / 원인 / 조치 세 줄 · 요청 | 목적 · 결과 한 줄 · 결론 | 지표 요약 · 변화 · 요청 |
| 현상 | 무엇이 · 언제부터 · 얼마나 (기준 대비) — 추세 + 기준선 | 조건 (DOE) · 결과 그림 | 지표 추세 |
| 현상 범위 | Is / Is-Not — 설비 · 제품 · 위치 (웨이퍼 맵) | 재현성 · 반복 | 구간 · 부문별 |
| 분석 | 가설마다 증거 › 판정 · 마지막에 가설 판정표 | 해석 · 메커니즘 · 통계 | 변화의 원인 |
| 의견 | 결론 · 확신 정도와 가장 약한 고리 · 조치 (봉쇄 · 재발 방지) · 결정 요청 | 결론 · 다음 실험 | 계획 · 위험 · 요청 |
| 한계 · 다음 | 확인하지 못한 것 (P-07) | 같음 | 같음 |
| 부록 | 데이터 · 방법 · 원 그림 목록 | 같음 | 같음 |

## 05 인터뷰 설계

```text
0 자료 받기    파일 · 그림 목록 (사용자)
1 미리 보기    profile → facts.json (f001…) · images → images.json (img1… · 크기 · sha256)
               사내 LLM 이 그림마다 판독 메모 (축 · 계열 · 추세 · 이상점 — 숫자는 [추정])
2 틀 잡기      보고 유형 · 독자 · 결론 한 줄 (모르면 '아직')               질문 3개 이하
3 현상         데이터 · 그림 판독이 말하는 후보를 보이고 고르게 한다        질문 3개 이하
               "3/12 부터 평균이 +0.6σ — 이것이 보고할 현상이 맞습니까?"
4 분석         가설 받기 › 가설마다 증거 그림 짝짓기 › 판정                 질문 4개 이하
5 의견         결론 · 확신 · 조치 · 요청을 사용자 말로 받고 다듬기만 제안    질문 2개 이하
6 줄거리 확인   제목 목록 (ghost deck) 을 보이고 고치기
7 빌드 · 검사   deck.json › validate › build › (되면) render › 사용자 확정
```

- **I-01** 보기 전에 묻지 않는다. 데이터 · 그림 · 앞의 답이 답하는 것은 묻지 않고 "이렇게 봤습니다 — 맞습니까" 로 확인만 한다.
- **I-02** 한 번에 한 질문. 선택지 2–4개 + 직접 입력, 추천을 맨 앞에. `question` 도구를 쓰고, 사내 모델이 도구 호출을 못 하면 번호 목록으로 묻고 번호로 받는다 (KIT-2).
- **I-03** 질문 예산: 틀 3 · 현상 3 · 분석 4 · 의견 2 = 12 [제안 — G6].
- **I-04** '모름 · 나중에' 는 언제나 고를 수 있다. 그 칸은 `[미확인]` 으로 장표에 남는다. 지어서 채우지 않는다.
- **I-05** 원인은 열린 질문이 먼저다 ("무엇 때문이라고 보십니까?"). LLM 의 가설 후보는 그 다음에 `제안` 표시로만 낸다 — 사용자가 고르면 그때 사용자 가설이 된다. 유도 질문 · 맞장구를 줄이려는 규칙이다 (Analysis–1 의 아첨 방지 개념 차용).
- **I-06** 그림에서 읽은 숫자는 늘 확인 질문으로 바꾼다: "약 3.2 로 읽힙니다 — 정확한 값이 있습니까?" 판독 숫자는 장표에 `[추정]` 없이 들어가지 못한다. 판독 메모와 원자료가 어긋나면 원자료가 이기고, 어긋남을 사용자에게 보인다 — 그림이 다른 필터 · 기간으로 그려졌을 수 있다 (리스크 19).
- **I-07** 답 원문은 메모리에만 (W-05 채택). 저장은 사용자가 확정한 `deck.json` 과 답 요약 (사용자가 본 것) 뿐이다.
- **I-08** 이어 할 수 있다. `deck.json` 의 `open_items` 가 곧 남은 질문 목록이다.
- **I-09** 독자에 따라 무게를 바꾼다. 경영진 = 요약 · 의견 · 요청, 팀 = 분석 · 근거.
- **I-10** 질문은 **질문 은행** (부록 B) 이 기본이다. LLM 은 은행에서 고르고 빈칸을 채운다. 자유 생성은 은행에 없을 때만 — 약한 사내 LLM 에서도 인터뷰 품질의 바닥을 지키려는 것이다.
- **I-11** 호스트를 더할 때의 규칙 (지금은 opencode + 사내 LLM 하나라 쓰지 않는다). 회사 밖 모델 (Claude 등) 을 붙일 때는 어댑터보다 **데이터 등급 문턱을 먼저** 정한다. 3판에서 설계해 둔 모양: 어댑터가 도구에 `--host` 를 넘기고, 설정 `policy.external_real_data` (기본 `false`) 가 합성 표시 (`--sample`) 없는 입력을 거부하며, 회사가 허용하면 사용자가 연다 (W-07). 이 문턱은 과속방지턱이지 보안 경계가 아니다 — 모델이 파일 읽기 도구로 직접 여는 것까지는 막지 못한다 (M5).

## 06 아키텍처

> 5판: 이 절의 파이썬 빌드 도구는 만들지 않기로 했다 (00 · K6 N). 4판 기록으로 남긴다. 인터뷰 (05) 와 보고 문법 (04) 은 5판의 프롬프트 묶음이 그대로 쓴다.

### 모양 (별도 저장소 · Q1)

```text
subordinate-1/                       공개 저장소 (Q6 · Q9)
├─ skills/subordinate-1/SKILL.md     인터뷰 · 보고 문법 (04) · 줄거리 규칙. 호스트 이름에 묶인 문장을 두지 않는다 (M5 대비)
├─ skills/subordinate-1/references/  질문 은행 · 장표 유형 · 합성 예시
├─ opencode/agents/subordinate-1.md  opencode 어댑터 — 전용 에이전트 · 권한 (bash 는 `subordinate-1` 명령만 · 편집은 작업 폴더만)
├─ opencode/commands/subordinate.md  opencode 어댑터 — `/subordinate <자료 폴더>`
├─ subordinate1/                     결정적 도구 — 명령 하나 `subordinate-1`
│   profile · images · template · build · validate · render · check · version
├─ subordinate1/styles/              SciencePlots 에서 옮겨 튜닝한 그림 스타일 (MIT 고지)
├─ tests/                            unittest · 합성 데이터 · 합성 템플릿 둘 · 골든 구조
├─ requirements.txt                  고정 의존 목록 (W-02 바꿈)
├─ INSTALL.md                        opencode 가 따라 하는 설치 (W-08 채택)
└─ docs/MANUAL.md · docs/PLAN.md · RULES.md (02 의 채택표)
```

- opencode: INSTALL 이 `skills/subordinate-1/` 와 `opencode/agents` · `opencode/commands` 를 opencode 설정 폴더 (`%USERPROFILE%\.config\opencode\`) 의 `skills` · `agents` · `commands` 로 복사하고, 제거 절에서 그 파일만 지운다 (W-08 · 같은 이름이 있으면 덮어쓰지 않고 묻는다). 복사본이라 업데이트 절이 다시 복사한다. 전역에 둔다 [제안].
- **호스트에 묶인 것은 어댑터에만 둔다.** `SKILL.md` 에는 호스트 이름 (opencode 의 도구 이름 · 권한 문법) 에 묶인 문장을 두지 않고 능력으로 쓴다 ("선택지 질문 도구가 있으면 그것으로, 없으면 번호 목록" — I-02). 나중에 Claude 를 붙일 때 어댑터만 더하면 되게 하려는 것이다 (M5).

### 누가 무엇을 만드나

| 일 | LLM (opencode + 사내 LLM) | 도구 (파이썬 · 결정적) | 사용자 |
|---|---|---|---|
| 데이터 사실 | — | `profile` → `facts.json` (통계 · 추세 · 변화점 · 이상점 · id) | 확인 |
| 그림 | 판독 메모 (사내 LLM · 숫자는 `[추정]`) | 원본 보관 · sha256 · 크기 · (선택) 다시 그리기 | 고르기 · 순서 |
| 질문 | 은행에서 고르고 채움 | 빈칸 목록 | 답 |
| 글 | 제목 · 문장 초안 (근거 id 를 달아야만) | 검사 | 고치기 · 확정 |
| 배치 | — | 템플릿 매핑 → `build` | 매핑 1회 확인 |
| 판정 | — | `validate` (V-01–V-10) | 예외 승인 |

**LLM 은 좌표를 쓰지 않는다** — ppt-master 와 반대로 간 결정이다. 레이아웃은 회사 템플릿의 자리표시자가 정하고, LLM 은 의미 (어느 절 · 어느 장표 유형 · 무슨 문장 · 무슨 근거) 만 쓴다. 약한 사내 LLM 에서도 장표가 깨지지 않게 하려는 것이다.

### `deck.json` — 닫힌 중간 언어 (계약)

ppt-master 의 "닫힌 중간 언어 + 검사 게이트" 를 빌리되 기하가 아니라 의미를 담는다. 초안은 부록 A. 요점:

- `format` 으로 형식 버전을 밝힌다 (works W-01 의 공개 명령 방식). 이 도구 안의 형식이다 — Analysis–1 과 아예 별개로 두기로 해 (Q4) 다른 도구와의 계약으로 약속하지 않는다.
- 장표마다 `section` (요약 · 현상 · 분석 · 의견 · 한계 · 부록) · `layout` (장표 유형 — 템플릿 레이아웃이 아니라 의미 유형) · `title` · `figure` · `bullets` · `notes`.
- 글 조각마다 `kind` (P-01) · `refs` (facts id · 그림 id · 답 id) · 해석이면 `reasoning`.
- 숫자 검사 (V-03): 글 속 숫자를 뽑아 `refs` 가 가리키는 값과 단위 · 유효숫자 · 반올림 · % · σ 규칙으로 맞춘다. 안 맞으면 `숫자?`.

### 템플릿

회사 템플릿이 있고, 바뀔 수 있다 (Q3). 그래서 템플릿을 **여러 벌 등록** 하고 **바뀜을 감지** 한다.

- `template add <파일> --name <이름>`: 회사 `.pptx` · `.potx` 를 데이터 폴더 (`%LOCALAPPDATA%\subordinate-1\templates\<이름>\`) 로 복사하고, 레이아웃 · 자리표시자 목록과 `mapping.json` 초안을 만든다 (예: 장표 유형 `title_figure` → 레이아웃 '제목 및 내용' 의 자리표시자 idx 0 · 1). 사용자가 한 번 확인 · 고친다 (W-07).
- 바뀜 감지: 등록할 때 sha256 과 레이아웃 지문 (레이아웃 이름 · 자리표시자 종류 · idx) 을 적어 둔다. `build` 때 다르면 멈추고 `template diff` 로 무엇이 바뀌었는지 (사라진 레이아웃 · 바뀐 자리표시자) 보인다.
- 새 판은 새 이름으로 등록하고 옛 판은 지우지 않는다 — 지난 보고를 같은 모양으로 다시 만들 수 있게.
- `deck.json` 은 템플릿을 모른다 (장표 유형은 의미 단위). 템플릿을 바꿔도 같은 `deck.json` 으로 다시 빌드한다 — 바뀐 템플릿에서 할 일은 매핑 확인뿐이다.
- 저장소에는 자리표시자 배치가 서로 다른 합성 템플릿 둘만 둔다 — 특정 템플릿에 맞춘 코드가 숨어들지 않게 (W-12 · T13).
- 템플릿이 없을 때의 기본 템플릿 (흰 바탕 · 무채색 + 강조 한 색 [제안]) 은 비상용으로만 둔다.

### 그림

- 받은 그림: 원본 복사 · sha256 · 픽셀 크기 → 자리표시자 안에 비율을 지켜 맞춘다 (늘리지 않음 · P-08).
- 다시 그리기 (사용자가 고를 때만): `facts.json` 의 계열로 matplotlib · `subordinate1/styles/` (SciencePlots 에서 옮겨 튜닝) · 회사 팔레트 (등록한 템플릿의 테마 색에서 읽기 [제안]) · 라이트 · 2× [제안].
- 네이티브 차트 (M4 · 선택): python-pptx 차트 — PPT 안에서 고칠 수 있지만 모양이 PowerPoint 에 달린다.

### 렌더 · 검사

- 구조 검사는 늘 한다 (python-pptx 로 다시 열기 · 빈 자리표시자 · 글자 예산).
- 그림 검사 (선택): Windows + PowerPoint 가 있으면 COM 으로 장마다 PNG (`pywin32` 선택 기능 — works W-02 의 Outlook 예와 같은 방식), 없으면 LibreOffice, 둘 다 없으면 건너뛰고 사용자 눈에 맡긴다.
- 시각 검토: 렌더 PNG 를 사내 LLM 이 장마다 보고 넘침 · 겹침 · 잘림 · 읽기 어려운 글자를 알린다 (알림만 · 막지 않음 · 판정은 사용자). PPTAgent · K-Dense 의 시각 검토 고리와 같은 모양이다.

### 호스트 — opencode + 사내 LLM (지금은 이것 하나 · 4판)

| 항목 | 어떻게 | 확인 |
|---|---|---|
| 설치 | `skills` · `agents` · `commands` 를 opencode 설정 폴더로 복사 (INSTALL) | KIT-1 |
| 시작 | `/subordinate <자료 폴더>` 또는 Tab 으로 `subordinate-1` 에이전트 | — |
| 질문 | `question` 도구 [문헌] · 도구 호출이 안 되면 번호 목록 | KIT-2 |
| 그림 보기 | 사내 LLM 비전 (사용자 답). 사용자 정의 provider 모델은 `modalities.input` 에 `image` 가 있어야 할 수 있다 [문헌: opencode 소스 `provider.ts` · 사용자 문서에는 없음 · 없을 때의 동작은 미확인] | KIT-2 |
| 그림 크기 | 2000×2000 · base64 5,242,880 바이트를 넘으면 opencode 가 줄여 보낸다 [문헌] — 웨이퍼 맵의 작은 점 · 작은 축 글자가 사라질 수 있다. 도구가 잘라 (축 · 범례 · 본문) 보이는 것을 KIT-3 에서 비교한다 | KIT-3 |
| 권한 | 에이전트 권한으로 bash 를 `subordinate-1` 명령에 묶는다 | — |
| 대화 저장 | `opencode.db` (리스크 9) | — |
| 나중 호스트 | Claude — 회사가 엔터프라이즈 판을 들인 뒤 사용자가 사내에서 어댑터로 더한다 (M5 · I-11) | — |

## 07 검사 V-01–V-10

> 5판: 검사기는 빌드 도구와 함께 접었다. V-02 · V-03 의 뜻 (근거 없는 문장 · 근거에 없는 숫자는 장표에 못 올라간다) 은 스킬의 글쓰기 규칙으로 남는다 (T16 · T17).

| # | 검사 | 실패하면 |
|---|---|---|
| V-01 | `deck.json` 스키마 · `format` | 막음 |
| V-02 | 근거 없는 사실 · 사용자 답 id 없는 의견 → `ERR` | 막음 |
| V-03 | 숫자 대조 (단위 · 유효숫자 · % · σ) → `숫자?` | 막음 — 사용자가 `직접` 으로 책임지면 풀림 (Report–1 개념) |
| V-04 | 제목 규칙 — 문장인가 · 길이 · 주제어 제목 | 알림 |
| V-05 | 절 순서 · 한계 장 있음 | 막음 |
| V-06 | 그림 원본 — sha256 이 `images.json` 과 같음 | 막음 |
| V-07 | 글자 예산 — 자리표시자마다 상한 (한글 폭 고려) [제안 값 · KIT-5 로 고침] | 알림 |
| V-08 | 빈 자리표시자 · 남은 자리표시 문자열 | 막음 |
| V-09 | 그림 장표마다 근거 줄 | 알림 |
| V-10 | 파일 열림 — python-pptx 다시 열기 + (되면) PowerPoint COM 열기 | 막음 |

- 막는 검사가 하나라도 실패하면 납품하지 않는다 (CyberPPT 원칙). 사용자가 예외를 승인하면 그 사실을 노트와 부록에 남긴다.

## 08 로드맵

### M0 정찰 — 앱 코드 0줄 · 1주 [추정 — pip 가능 (Q5) 으로 줄었다]

정찰 스크립트는 버리는 코드다. 문턱은 결과를 보기 전에 적는다 (Analysis–1 M0 방식).

| # | 무엇 | 초록 | 빨강이면 |
|---|---|---|---|
| KIT-1 | 사내 PC 확인 (pip 는 된다 — Q5): Python 판 (최소 Python 을 여기서 정한다) · `pip install` 고정 목록 · import · PowerPoint COM (`pywin32`) 유무 | 다 돈다 | 걸린 패키지만 판을 낮추거나 대체 검토 |
| KIT-2 | opencode + 사내 LLM: 그림이 모델에 실제로 닿는가 (`modalities` 있음 · 없음 두 번) · 도구 호출 · `question` 도구 · 맥락 길이 (그림 5장 + facts) · 한국어 문장 · `deck.json` 스키마 통과율 | 그림이 닿고 스키마 통과 80% 이상 [제안] | 설정 보강 · 장 단위로 쓰기 · 질문 은행 비중을 올림 · 고치기 루프 |
| KIT-3 | 그림 판독 정확도: 사용자 그림 10장 (선 · 웨이퍼 맵 · 박스 · 산점) 을 사내 LLM 이 읽은 것 vs 원자료 · 사용자 답 — 모양 서술 · 숫자 오차 · 작은 점 (웨이퍼 맵은 Ascii–1 개수 추정과도 비교) · opencode 축소 전후 · 잘라 보이기 전후 | 모양 서술 맞음 80% 이상 [제안] | 판독은 '후보 제시' 로만 쓰고 그림의 뜻은 인터뷰로 받는다 (I-06) |
| KIT-4 | 회사 템플릿 (지금 판 + 있으면 이전 판) 을 python-pptx 로 열어 레이아웃 · 자리표시자 목록이 나오는가 · 두 판의 지문 차이가 보이는가 | 목록이 나오고 매핑 가능 | 빈 레이아웃 + 도형 배치 |
| KIT-5 | Office: python-pptx 로 만든 PPTX 를 사내 PowerPoint 가 복구 없이 여는가 · 한글 글자 넘침 | 열림 | 요소별 (그림 · 표 · 노트) 로 원인을 좁힌다 |
| KIT-6 | 기준선: 같은 자료로 ① 손 작업 시간 ② Presenton + 사내 LLM ③ (되면) pandoc `reference-doc` | — | — |

**만들지 않을 기준** [제안]: KIT-6 ② 가 G2 · G3 를 프롬프트만으로 80% 채우면 만들지 않는다. 대신 질문 은행 · 보고 문법 · 템플릿 매핑을 프롬프트 묶음으로만 낸다.

### M1 – M4

> 5판: M1 – M4 는 접었다. 새 순서는 부록 C 의 T16 – T23 이다.

| 단계 | 범위 | 합격 |
|---|---|---|
| M1 뼈대 | `profile` · `images` · `template` · `build` · `validate` (V-01 · V-05 · V-06 · V-08 · V-10) · 합성 데이터 테스트. LLM 없이 손으로 쓴 `deck.json` 으로도 PPTX 가 나온다 | 합성 보고 3종이 열린다 (G5) |
| M1 · 템플릿 | 템플릿 여러 벌 등록 · 바뀜 감지 · `template diff` (M1 에 넣는다 — Q3 '바뀔 수 있음') | 합성 템플릿 둘에서 같은 `deck.json` 이 빌드된다 |
| M2 인터뷰 | 스킬 · opencode 어댑터 · 질문 은행 · 그림 판독 메모 · V-02 · V-03 · V-04 · ghost deck 확인 | 사내에서 실제 보고 3건 — G1 · G2 · G4 · G6 (사용자가 돌리고 결과 요약을 넘긴다 · 리스크 22) |
| M3 그림 · 렌더 | 다시 그리기 · 근거 줄 · 렌더 검사 · 사내 LLM 시각 검토 · V-07 · V-09 | G3 |
| M4 다듬기 | 보고 유형 셋 · 독자 노브 · 지난 보고서 학습 (markitdown) · 네이티브 차트 | — |
| M5 (나중 · 조건부) Claude 어댑터 | 회사가 엔터프라이즈 판을 들인 뒤 사용자가 사내에서 튜닝: 데이터 보존 · 학습 사용 조건을 회사 계약에서 확인 [미확인] · I-11 의 데이터 등급 문턱 먼저 · 어댑터 (플러그인 · 명령) · 같은 합성 시나리오로 두 호스트 비교 | 회사 확인 · G2 |

## 09 리스크 대장

| # | 위험 | 가능성 | 영향 | 조기 신호 | 대응 |
|---|---|---|---|---|---|
| 1 | pip 는 되지만 (Q5) 특정 휠이 막히거나, 최신 pandas · matplotlib 이 사내 Python 판을 지원하지 않음 [미확인] | 낮음 | 상 | KIT-1 | 고정 판을 사내 Python 판에 맞춤 · 오프라인 휠 묶음 |
| 2 | 사내 LLM 은 그림을 보지만 (사용자 답) opencode 가 그림을 못 넘기거나 (`modalities`) 줄이면서 작은 점 · 글자가 사라지거나, 그림 여러 장이 맥락을 채움 | 중 | 상 | KIT-2 · KIT-3 | provider 설정 보강 · 그림은 한 장씩 보이고 판독 메모만 남긴다 · 잘라 보이기 · 판독은 후보로만 (I-06) |
| 3 | 사내 LLM 이 약해 `deck.json` 을 자주 깨뜨림 | 중 | 상 | KIT-2 통과율 | 스키마 검사 › 고치기 루프 2회 · 질문 은행 · 장 단위로 쓰기 |
| 4 | 지어낸 원인 · 숫자 | 중 | 최상 (신뢰 붕괴) | V-02 · V-03 걸림 수 | 문장 종류 · 근거 id · 의견은 사용자만 · `[미확인]` 남기기 · T14 적대 검증 |
| 5 | 그림 판독 숫자 오독 | 상 | 상 | KIT-3 오차 | 판독 숫자는 늘 `[추정]` · 장표 숫자는 facts 또는 사용자 답에서만 |
| 6 | 라이선스 오염 (Anthropic 스킬 · AGPL 복사) | 낮음 | 상 (공개 저장소) | 리뷰 | 허용 목록 · 고지 파일 · CI 의존 라이선스 검사 |
| 7 | 회사 템플릿 · 실데이터 커밋 (W-12) | 중 | 최상 | — | 템플릿은 데이터 폴더 · `.gitignore` · 합성 예시 · 사설 주소 검사 |
| 8 | 이 도구를 짓는 개발 세션 (Claude Code · 회사 밖) 에 실데이터 · 회사 템플릿이 들어감 | 낮음 | 최상 (규정 위반) | — | 개발 · 테스트는 합성 자료만 · 저장소에 실데이터 금지 (리스크 7) · M0 결과는 원문 없이 숫자 · 판정만 넘긴다 |
| 9 | opencode 가 대화 원문 · 그림을 `opencode.db` 에 남김 (W-05 밖) [문헌] | 확실 | 중 | — | 알려진 한계로 적고 지우는 법을 MANUAL 에 · 도구 쪽 저장은 확정본만 · 쓰는 opencode 판에 세션을 밖으로 공유하는 기능이 있으면 끈다 [미확인 — 지금 문서에서 찾지 못함] |
| 10 | 템플릿이 제각각 (자리표시자 이름 · 깨진 마스터) | 상 | 중 | KIT-4 | 매핑 1회 확인 · 실패 시 빈 레이아웃 + 도형 |
| 11 | 한글 글자 넘침 | 상 | 중 | KIT-5 | 글자 예산 · 렌더 검사 · 자동 맞춤은 PowerPoint 가 열 때만 계산된다 [미확인] |
| 12 | python-pptx 유지 정체 (2024-08 이후 push 없음 [실험]) | 중 | 중 | 새 Office 와 어긋남 | 버전 고정 · 어댑터 한 겹. 표준 라이브러리 OOXML 비상구는 미리 만들지 않는다 — pip 가 되니 급하지 않고, 일이 생기면 어댑터 뒤에서 바꾼다 |
| 13 | 인터뷰 피로로 중간에 그만둠 | 중 | 상 | 이탈 | 질문 예산 12 · 모름 허용 · 이어 하기 |
| 14 | Analysis–1 08 (보고서 · PPTX v0) 과 겹침 | 확실 | 낮음 | — | 받아들인다 — 아예 별개 (Q4). 코드 · 형식 · 일정 공유 없음. 보고 문법 같은 개념만 서로 참고한다 |
| 15 | 확증 편향 — LLM 이 사용자 가설에 맞장구 | 중 | 상 | — | I-05 · 분석 절의 '배제한 가설' 칸 필수 · 판정은 증거 기준 |
| 16 | 만들 필요가 없음 (기성품으로 충분) | 낮음–중 | 중 | KIT-6 | 만들지 않을 기준 |
| 17 | 렌더 검사 도구가 없음 (COM · LibreOffice 둘 다) | 중 | 낮음 | KIT-5 | 구조 검사만 · 사용자 눈 |
| 18 | 1인 유지 부담 | 상 | 중 | — | 범위 상한 · 호스트 하나 · 호스트에 묶인 것은 어댑터에만 |
| 19 | 그림 판독과 원자료가 어긋남 (그림이 다른 필터 · 기간 · 집계로 그려짐) | 중 | 상 | 판독 메모 ↔ facts 차이 | 원자료가 이긴다 · 어긋남을 보이고 사용자 확인 (I-06) · 근거 줄에 그림의 출처를 따로 적음 |
| 20 | 회사 템플릿이 바뀌어 매핑이 깨짐 (Q3 '바뀔 수 있음') | 상 | 중 | `build` 의 지문 불일치 | 바뀜 감지 › `template diff` › 새 이름으로 등록 · 옛 판 보존 · `deck.json` 은 템플릿을 모른다 |
| 21 | (없앰 — 4판에서 호스트가 하나가 됨 · 번호는 다시 매기지 않는다) | — | — | — | M5 에서 다시 본다 |
| 22 | 개발 고리가 끊김 — 개발 세션은 사내 LLM · 사내 PC · 회사 템플릿을 못 본다. 인터뷰 품질 · 템플릿 매핑 · Office 열림은 사용자가 사내에서 돌린 결과로만 확인된다 | 확실 | 상 | 사내 실행 결과가 늦게 옴 | 결정적 도구는 CI 에서 끝까지 검증 · 사내 실행은 키트와 점검표로 짧게 · 결과는 원문 없이 숫자 · 판정 · 오류 이름만 넘긴다 · 인터뷰는 합성 시나리오 기록으로 먼저 다듬는다 |
| 23 | 판정 기준의 구멍 — N 이 '기성품이 회사 템플릿까지 해 준다' 를 뜻하지 않을 수 있다 (U1 – U3) | 중 | 상 | T22 의 템플릿 맞추기 시간 | 시범에서 회사 템플릿 위로 옮기는 시간을 따로 잰다 · 오래 걸리면 '템플릿 맞추기만 하는 작은 도구' 를 다시 판정한다 (기준을 바꾼 것으로 기록) |
| 24 | 실제 보고에서 사실 목록을 누가 만드나 — M0 는 합성 facts_lite 를 주었다 | 상 | 상 | 시범에서 숫자가 지어짐 · `[미확인]` 이 많음 | 스킬이 핵심 숫자를 사용자에게 받거나 분석 도구의 요약을 붙여 넣게 한다 · 그림에서 읽은 숫자는 후보로만 (K3) · 숫자마다 출처 (자료 파일 · 사용자 답 id) 를 `deck.md` 에 적는다 |

## 10 사용자에게 물을 것

### 해결한 질문 (2026-11-03 사용자 답)

| # | 질문 | 답 | 바뀐 것 |
|---|---|---|---|
| Q1 | 모양 · 자리 | ① 에이전트 플러그인 + 파이썬 도구 · 별도 저장소 | 02 를 규칙 채택표로 · W-02 를 고정 의존 목록으로 · 표준 라이브러리 OOXML 가지를 뺌 |
| Q2 | 실데이터를 돌릴 호스트 | ③ 둘 다 (opencode + Claude Code) — 앞서 'opencode 로 쓴다' 를 넓힌 답으로 읽었다 | 공용 스킬 + 호스트 어댑터 둘 (06) · I-11 · 리스크 8 · 21 · Q8 |
| Q3 | 회사 PPT 템플릿 | ① 있음 — 바뀔 수 있음 | 템플릿 여러 벌 등록 · 바뀜 감지를 M1 으로 (06 · 08) · KIT-4 · 리스크 20 |
| Q4 | Analysis–1 과의 관계 | 아예 별개 | `deck.json` 공용 계약을 뺌 · 리스크 14 를 받아들임 · 엔진을 맞추지 않음 |
| Q5 | 사내 PC pip 설치 | 된다 | KIT-1 을 확인으로 줄임 · M0 1주 · 리스크 1 낮춤 |
| — | (질문 밖) 사내 LLM 의 그림 보기 | 본다 | 판독 메모 · 시각 검토 · Ascii–1 은 보조로 (03 · 05 · 06) |

### 해결한 질문 (2026-11-03 사용자 답 · 둘째)

| # | 질문 | 답 | 바뀐 것 |
|---|---|---|---|
| Q6 | 이름 | `subordinate-1` (화면 Subordinate–1) | 저장소 · 폴더 · 명령 `subordinate-1` · 데이터 폴더 `%LOCALAPPDATA%\subordinate-1` · 환경 변수 `SUBORDINATE_*` · 파이썬 패키지 `subordinate1` · 호스트 명령 `/subordinate` [제안] · 이 파일 이름 (`git mv`) |
| Q7 | 설치 자리 | `D:\OPENCODE\subordinate-1` | works `.gitignore` 에 `/subordinate-1/` (works 커밋 따로 · 02) |
| Q8 | Claude Code 로 실데이터 | 지금은 회사가 막음 · 엔터프라이즈 판으로 풀릴 예정 | 도구 문턱 `policy.external_real_data` 기본 `false` (I-11) · M5 (조건부) · 리스크 8 · 21 다시 씀 |
| Q9 | 저장소 공개 여부 | 공개 | W-12 그대로 — 예시 · 테스트는 합성만 |

### 해결한 질문 (2026-11-03 사용자 제안 · 셋째)

| 제안 | 정한 것 | 바뀐 것 |
|---|---|---|
| 지금은 사내 LLM 전용으로 · Claude 는 들어오면 사용자가 사내에서 튜닝 | 동의 — 4판 | Claude 어댑터 · 호스트 문턱 · 두 호스트 시험을 뺌 · I-11 을 '호스트를 더할 때의 규칙' 으로 · M5 를 나중 · 조건부로 · 리스크 21 없앰 · 22 더함 · 작업표 T2 · T4 · T6 · T11 · T14 · T15 |

### 해결한 질문 (2026-11-03 사용자 답 · 넷째)

| # | 질문 | 답 | 바뀐 것 |
|---|---|---|---|
| Q10 | 저장소 라이선스 | MIT | `LICENSE` 를 더함 (저작권자 표기는 GitHub 계정 이름) · T6 은 이제 M0 결과만 기다린다 |

### 남은 질문

- 없음 — 5판 결정은 사용자가 확정했다 (2026-11-03).

### 5판에서 열어 둔 것 (막지 않음)

| # | 모르는 것 | 왜 막지 않나 | 언제 알게 되나 |
|---|---|---|---|
| U1 | KIT-6 에서 이긴 갈래 (Presenton · pandoc) | `deck.md` 하나로 두 기성품을 다 받게 만든다 (T16 · T18) | T22 시범 |
| U2 | Presenton 을 두 번 돌려 둘 다 통과했나 (기준의 조건) | 사용자가 답 없이 N 을 확정했다 | T22 |
| U3 | 기준선 장표가 회사 템플릿 위였나 | 템플릿 맞추기는 이 묶음 밖 — 알려진 한계 (리스크 10 · 23) | T22 에서 템플릿 맞추기 시간을 따로 잰다 |
| U4 | K5 의 글자 넘침 장 수 | 빌드 도구를 접어 영향이 작다 | — |

## 부록

### A `deck.json` 초안 (format 1)

```json
{
  "format": 1,
  "meta": {"type": "anomaly", "audience": "team", "title": "PRD_B 두께 상승 보고", "date": "2026-11-03", "host": "opencode", "data_class": "real"},
  "sources": {"facts": "facts.json", "facts_sha256": "<앞 16자>", "images": "images.json"},
  "slides": [
    {
      "id": "s3",
      "section": "현상",
      "layout": "title_figure",
      "title": {"text": "PRD_B 두께가 3/12 부터 평균 +0.6σ 올랐다", "kind": "사실", "refs": ["f012", "f013"]},
      "figure": {"image": "img2", "evidence_line": "auto"},
      "bullets": [
        {"text": "같은 기간 PRD_A 는 변화가 없다", "kind": "사실", "refs": ["f020"]},
        {"text": "제품 공통 원인보다 PRD_B 조건 쪽이다", "kind": "해석", "refs": ["f012", "f020"], "reasoning": "같은 설비 · 같은 기간에 한 제품만 움직였다"}
      ],
      "notes": ""
    }
  ],
  "open_items": [{"slot": "s5.title", "why": "원인 가설을 아직 받지 않음"}]
}
```

- 예시의 이름 · 숫자는 지어낸 것이다 (W-12).
- `layout` 은 의미 유형 (`title_only` · `title_figure` · `title_figure_compare` · `title_table` · `hypothesis_verdict` · `summary_bluf` · `limits`) 이고, 템플릿 레이아웃과의 짝은 `mapping.json` 이 정한다.

### B 질문 은행 (예시 10)

| # | 단계 | 질문 | 선택지 (추천 먼저 · 직접 입력은 늘 있음) |
|---|---|---|---|
| B1 | 틀 | 이 보고는 무엇을 위한 것입니까? | 이상 보고 · 실험 결과 · 정기 보고 |
| B2 | 틀 | 누가 읽습니까? | 팀 · 팀장 · 경영진 · 다른 부서 |
| B3 | 틀 | 결론을 한 줄로 말하면? | (직접) · 아직 — 인터뷰 끝에 다시 묻기 |
| B4 | 현상 | 데이터에서 이 변화가 보입니다: {f-id 요약}. 이것이 보고할 현상입니까? | 예 · 아니오 (다른 것) · 일부만 |
| B5 | 현상 | 이 현상이 **나타나지 않는** 곳은? (Is-Not) | {데이터가 말하는 후보} · 모름 |
| B6 | 분석 | 무엇 때문이라고 보십니까? | (직접 — 열린 질문 먼저 · I-05) |
| B7 | 분석 | 가설 {h} 의 증거로 어느 그림을 쓰겠습니까? | {img 목록} · 원자료로 다시 그리기 · 증거 없음 (미정) |
| B8 | 분석 | 배제한 가설과 그 까닭은? | (직접) · 없음 |
| B9 | 의견 | 이 결론을 얼마나 확신하십니까? | 확정 · 유력 · 가설 단계 |
| B10 | 의견 | 이 보고로 무엇을 요청합니까? | 결정 · 자원 · 공유만 · 기타 |

### C 작업표 (하위 에이전트용 · 5판)

이 세션의 사용자 설정 (4단 모델 배정) 에 따른 작업표다. 4판 작업의 처리:

| 작업 | 처리 |
|---|---|
| T1 – T3 | 끝남 — M0 키트 (PR #2 · #3) · 사용자가 사내에서 돌림 (00) |
| T4 | 끝남 — 이 5판 |
| T5 – T15 | 접음 — 파이썬 빌드 도구 (K6 N) |

새 작업 T16 – T23:

```json
{
  "project_title": "Subordinate–1 (5판) — 인터뷰 › deck.md › 기성품 PPTX · 현상 › 분석 › 의견 프롬프트 묶음",
  "executive_summary": "M0 결과 (K6 N) 에 따라 PPTX 를 짓는 파이썬 도구는 만들지 않고, 인터뷰 · 보고 문법 · 질문 은행을 opencode 스킬로 묶어 근거 달린 deck.md 를 쓰게 한다. 사용자는 deck.md 를 Presenton 에 붙여 넣거나 pandoc 으로 PPTX 로 바꾼다. 회사 템플릿 맞추기와 판정 기준의 구멍 (이긴 갈래 · 회사 템플릿) 은 사내 시범에서 따로 잰다.",
  "total_estimated_effort": 48,
  "tasks": [
    {"task_id": "T16", "task_name": "deck.md 형식 명세", "description": "결과물 deck.md 의 마크다운 형식을 정한다 — 절 (현상 · 분석 · 의견 · 한계) · 장마다 한 문장 제목 · 그림 자리 (img id · 원본 파일 이름) 와 근거 줄 · 문장마다 종류 (사실 · 해석 · 의견 · [미확인]) 와 출처 id (자료 파일 · 사용자 답 id) · 발표자 노트. 같은 파일을 Presenton 에 붙여 넣어도, pandoc 으로 PPTX 로 바꿔도 장 나눔 · 제목 · 그림이 깨지지 않게 두 쪽 규칙을 함께 맞춘다 (pandoc 의 장 나눔 규칙은 실제로 돌려 확인). 합성 예시 하나와 반례 (근거 없는 숫자 · 사용자 말이 아닌 의견) 를 함께 낸다.", "tier": "Tier 1", "difficulty": "High", "effort_level": 6, "assigned_model": "claude-opus-5.5", "agent_role": "Spec_Designer", "expected_output": "docs/SPEC-deck-md.md · examples/deck_synthetic.md", "dependencies": []},
    {"task_id": "T17", "task_name": "opencode 스킬 · 명령 · 에이전트", "description": "skills/subordinate-1/SKILL.md (인터뷰 I-01–I-10 · 보고 문법 P-01–P-08 · 질문 은행 · deck.md 쓰기) · opencode/agents/subordinate-1.md (권한: 자료 읽기 · 작업 폴더에 deck.md 쓰기만 · 셸 없음) · opencode/commands/subordinate.md (/subordinate <자료 폴더>) 를 만든다. 질문은 번호 목록 (K2) · 그림은 판독 메모만, 그림에서 읽은 숫자는 후보로 되묻기 (K3) · 의견은 사용자 답 id 로만 · 사실 숫자는 자료 파일이나 사용자 답에서 온 것만 출처를 달아 쓴다 (리스크 24). 호스트 이름에 묶인 문장을 두지 않는다 (M5 대비). kit 의 facts_lite · interview_lite 로 합성 대화 기록을 남긴다.", "tier": "Tier 1", "difficulty": "High", "effort_level": 7, "assigned_model": "claude-opus-5.5", "agent_role": "Interview_Designer", "expected_output": "skills/subordinate-1/ · opencode/agents/subordinate-1.md · opencode/commands/subordinate.md · 합성 대화 기록", "dependencies": ["T16"]},
    {"task_id": "T18", "task_name": "기성품에 넣는 법", "description": "docs/USE-presenton.md · docs/USE-pandoc.md 를 쓴다 — deck.md 를 Presenton 에 붙여 넣는 절차 (사내 LLM 연결 · 외부 공급자 끄기 · 그림 넣기 · 내보내기) 와 pandoc --reference-doc 로 PPTX 로 바꾸는 절차. 회사 템플릿을 쓸 수 있는지와 손으로 옮기는 법은 [미확인] 으로 적고 T22 에서 채운다. 관리자 권한이 필요한 설치는 쓰지 않는다.", "tier": "Tier 3", "difficulty": "Medium", "effort_level": 5, "assigned_model": "claude-sonnet", "agent_role": "Documentation_Specialist", "expected_output": "docs/USE-presenton.md · docs/USE-pandoc.md", "dependencies": ["T16"]},
    {"task_id": "T19", "task_name": "INSTALL — opencode 설치 · 제거", "description": "opencode 가 따라 하는 INSTALL.md 를 쓴다 — 스킬 · 명령 · 에이전트를 opencode 설정 폴더로 복사 (같은 이름이면 덮어쓰지 않고 묻기) · 사내 provider 모델에 modalities (image) 넣기 (K2 B — 필수) · 업데이트 · 제거 때 그 파일만 지우기 · 키는 {env:…} 로만.", "tier": "Tier 3", "difficulty": "Medium", "effort_level": 5, "assigned_model": "claude-sonnet", "agent_role": "Documentation_Specialist", "expected_output": "INSTALL.md", "dependencies": ["T17"]},
    {"task_id": "T20", "task_name": "README · 그림을 5판에 맞춤", "description": "README 를 5판에 맞춘다 — 결과물은 deck.md 이고 PPTX 는 기성품 (Presenton · pandoc) 이 만든다는 것, M0 결과 요약, 알려진 한계 (회사 템플릿 맞추기). 빌드 도구를 그린 그림 (hero 의 subordinate-1 validate · template 의 build 출력 · grammar 의 validate 표시) 을 deck.md 와 기성품 모습으로 고치거나 뺀다. docs/images/src 를 고치고 tools/readme_pages.mjs 로 다시 찍고, 라이트 · 다크 모두 눈으로 확인한다.", "tier": "Tier 2", "difficulty": "Medium-High", "effort_level": 8, "assigned_model": "claude-sonnet", "agent_role": "UI_Engineer", "expected_output": "README.md · docs/images/page/*.png · docs/images/src/*", "dependencies": ["T17", "T18"]},
    {"task_id": "T21", "task_name": "키트 정리 · 규칙 되돌리기", "description": "시범 (T22) 이 끝나면 kit/ 와 tests/test_kit_*.py 를 지우고 CI 의 python-pptx 설치 단계를 뺀다. RULES.md W-02 를 '실행 의존 없음' 으로 고치고 AGENTS.md 의 Python 3.8 문장을 고친다. tools/repo_check.py 와 그 시험은 남긴다.", "tier": "Tier 3", "difficulty": "Medium", "effort_level": 4, "assigned_model": "claude-sonnet", "agent_role": "Repo_Maintainer", "expected_output": "kit 삭제 커밋 · RULES · AGENTS · CI 수정", "dependencies": ["T22"]},
    {"task_id": "T22", "task_name": "사내 시범 양식", "description": "실제 보고 몇 건을 opencode + 스킬로 deck.md 를 만들고 기성품으로 PPTX 를 만들어 재는 양식을 만든다 — G1 시간 · 지어낸 숫자 수 · G3 제목 이야기 점수 · 회사 템플릿 위로 옮기는 데 든 분 (U3 · 리스크 23) · 엔지니어 입에 넣은 의견 수 · 쓴 기성품 (U1). 결과는 6줄 양식처럼 한 줄씩 원문 없이 받고, 판정 문턱은 결과 전에 적는다.", "tier": "Tier 3", "difficulty": "Medium", "effort_level": 5, "assigned_model": "claude-sonnet", "agent_role": "Benchmark_Analyst", "expected_output": "docs/PILOT.md (절차 · 판정 문턱 · 보낼 줄 양식)", "dependencies": ["T17", "T18", "T19"]},
    {"task_id": "T23", "task_name": "적대 검토", "description": "합성 시나리오로 스킬을 레드팀한다 — 근거 없는 숫자를 쓰게 유도 · 사용자 말이 아닌 의견을 쓰게 유도 · 그림에서 읽은 숫자를 사실로 쓰게 유도 · 질문 예산을 넘기게 유도 · 회사 이름 같은 민감한 말을 deck.md 에 옮기게 유도. 막지 못한 경로는 SKILL.md 를 고쳐 막고, 고칠 수 없는 것은 알려진 한계로 적는다.", "tier": "Tier 0", "difficulty": "Extreme", "effort_level": 8, "assigned_model": "claude-opus-5.5", "agent_role": "Security_Integrity_Auditor", "expected_output": "검토 보고서 · SKILL.md 수정", "dependencies": ["T17"]}
  ]
}
```

### D 조사 원자료

- 별 수 · 라이선스 · 최근 push: `gh api -X GET search/repositories -f q="repo:<owner>/<name> …"` (2026-11-03). 개별 저장소 API 는 이 세션에서 막혀 검색 API 로 쟀다.
- 직접 읽은 문서: ppt-master README · requirements · docs/technical-design.md · PPTAgent README · Presenton README · K-Dense README · scientific-slides `SKILL.md` · academic-pptx-skill README · CyberPPT README · superpowers brainstorming `SKILL.md` · opencode docs (skills · tools · plugins) · Anthropic skills README · `skills/pptx/LICENSE.txt` · md2pptx · LIDA · Office-PowerPoint-MCP-Server README.
- 읽지 않은 것 (별 수만): jinba-consulting-pptx-skill · huashu-design · genoffice · univer · data-formulator 본문.

### E 갈린 결정 — 1판 › 2판 (2026-11-03 사용자 답)

| 결정 | 1판 | 2판 | 까닭 |
|---|---|---|---|
| 자리 | 별도 저장소 (제안) · works 안 OOXML 가지를 대안으로 | 별도 저장소 (확정) · OOXML 가지 없앰 | Q1 · Q5 |
| 호스트 | Claude Code + opencode 겸용 (1판) › opencode 하나 (1판 고침) | opencode + Claude Code 둘 다 · 공용 스킬 + 어댑터 둘 | Q2 ③ — 회사 규정은 Q8 로 남김 |
| 그림 읽기 | 비전이 있으면 · Ascii–1 다리 | 호스트 모델이 판독 메모 · 시각 검토 · Ascii–1 보조 | 사내 LLM 이 그림을 본다 |
| 실행 의존 | python-pptx 필수 · 나머지 선택 기능 | python-pptx · pandas · openpyxl · matplotlib · scipy 필수 · 선택은 렌더 검사뿐 · SciencePlots 는 의존 대신 스타일 차용 | Q5 (pip 가능) — 선택 기능 분기가 코드 · 테스트를 늘린다 |
| 템플릿 | 하나 등록 · 매핑 1회 | 여러 벌 등록 · 지문으로 바뀜 감지 · `template diff` · 옛 판 보존 · M1 으로 당김 | Q3 '바뀔 수 있음' |
| Analysis–1 | `deck.json` 을 공용 계약으로 (제안) | 아예 별개 — 계약 · 코드 · 일정 공유 없음 · 겹침을 받아들임 | Q4 |
| M0 | 2주 · 설치 정찰이 큰 몫 | 1주 · 설치는 확인만 · 호스트 둘의 시험지 | Q5 · Q2 |
| 작업표 | 15 작업 · 노력도 합 112 | 15 작업 · 노력도 합 110 (T1 을 Tier 3 로 내리고 T2 를 올림) | 위의 결정들 |

### F 갈린 결정 — 2판 › 3판 (2026-11-03 사용자 답 · 둘째)

| 결정 | 2판 | 3판 | 까닭 |
|---|---|---|---|
| 이름 | 가칭 Deck–1 | `subordinate-1` (Subordinate–1) · 이 파일 이름도 옮김 | Q6 |
| 설치 자리 | 미정 | `D:\OPENCODE\subordinate-1` · works `.gitignore` 한 줄 | Q7 |
| Claude Code 실데이터 | 시작 때 등급 질문 (확인 장치) | 도구 설정 문턱으로 기본 거부 · 엔터프라이즈 뒤 M5 에서 연다 | Q8 — 지금은 회사가 막음 |
| 저장소 | 공개 여부 미정 | 공개 · W-12 그대로 | Q9 |
| 다음 판 | 3판 = M0 결과와 남은 답 | 4판 = M0 결과 (남은 질문 없음) | 위의 답 |
| 작업표 | 노력도 합 110 | 노력도 합 111 (T6 에 설정 · 호스트 문턱을 더함) | Q8 |

### G 갈린 결정 — 3판 › 4판 (2026-11-03 사용자 제안)

| 결정 | 3판 | 4판 | 까닭 |
|---|---|---|---|
| 호스트 | opencode + Claude Code · 어댑터 둘 | opencode + 사내 LLM 하나 · Claude 는 M5 (나중 · 조건부) | Claude 가 언제 들어올지 모른다 · 들어오면 사용자가 사내에서 튜닝한다 |
| Claude 실데이터 문턱 | 도구 설정 문턱으로 기본 거부 | 만들지 않는다 · 설계는 I-11 에 남김 | 호스트가 하나면 쓸 곳이 없다 |
| 미리 남기는 것 | — | `SKILL.md` 의 호스트 중립 문장 · `deck.json` 의 `meta.host` | 나중 비용을 줄이는 값싼 이음매 |
| 기획서 자리 | works `docs/plans/` 초안 | 이 저장소 `docs/PLAN.md` · works 링크는 `6c93377` 로 고정 | 저장소가 생겼다 |
| 작업표 | 노력도 합 111 | 노력도 합 107 (T2 · T6 · T11 · T15 를 줄임) | 호스트 하나 |

### H 갈린 결정 — 4판 › 5판 (2026-11-03 M0 결과 · 사용자 확정)

| 결정 | 4판 | 5판 | 까닭 |
|---|---|---|---|
| 만들 것 | 인터뷰 스킬 + 파이썬 빌드 도구 (python-pptx · 템플릿 등록부 · 검사 · 렌더) | 프롬프트 묶음 (스킬 · 명령 · 에이전트) + `deck.md` | K6 N — 미리 적은 기준 · 사용자 확정 |
| 결과물 | 회사 템플릿 위의 PPTX | `deck.md` (Presenton 붙여 넣기 · pandoc 변환) | 기성품이 PPTX 를 만든다 |
| 실행 의존 | python-pptx · pandas · openpyxl · matplotlib · scipy | 없음 | 빌드 도구를 접음 |
| 최소 Python | M0 뒤 결정 | 3.13 — 파이썬 코드가 남을 때만 | K1 |
| 그림 | 판독 메모 · 다시 그리기 | 판독 메모 · 숫자는 후보로만 | K3 숫자 6/9 |
| 질문 | question 도구 · 안 되면 번호 목록 | 번호 목록이 기본 | K2 T |
| 설치 | `modalities` 확인 단계 | `modalities` 필수 단계 | K2 B |
| 회사 템플릿 | 자리표시자 매핑 · 바뀜 감지 | 이 묶음 밖 — 알려진 한계 · 시범에서 잼 | K4 (자리표시자 0) · U3 |
| 작업표 | T5 – T15 | T16 – T23 (노력도 합 48) | 위 결정 |
