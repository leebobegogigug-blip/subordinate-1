# Subordinate–1

원자료와 차트 그림, 그리고 인터뷰로 엔지니어링 보고 장표를 만드는 opencode 플러그인입니다.

> **상태: 기획 · M0 정찰 단계입니다.** 아직 쓸 수 있는 기능이 없습니다. 앱 코드도 없고, 설치 문서(`INSTALL.md`)와 매뉴얼(`docs/MANUAL.md`)은 정찰 결과가 나온 뒤에 만듭니다.

## 무엇을 하려는가

CSV · XLSX 원자료와 차트 그림(PNG)을 받습니다. 사용자와 짧게 인터뷰합니다. 그 결과로 회사 템플릿에 맞춘, 고칠 수 있는 PPTX 초안을 만듭니다. 이야기 순서는 현상 › 분석 › 의견입니다. 장표의 숫자는 모두 근거에 묶이고, 의견은 사용자가 말한 것만 씁니다.

## 지금 읽을 것

| 문서 | 내용 |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | 기획서 · 무엇을 왜 어떻게 만드는지 |
| [RULES.md](RULES.md) | 이 저장소의 규칙 |
| [AGENTS.md](AGENTS.md) | 이 저장소를 고치는 에이전트용 요약 |
| [LICENSE](LICENSE) | MIT |

## 설치 자리

설치 위치는 `D:\OPENCODE\subordinate-1` 로 정했습니다. 설치 절차는 아직 없습니다.

## 점검

공개 저장소라서 비밀 · 사설 주소 · 자료 파일이 올라가지 않았는지 검사합니다.

```text
python tools/repo_check.py --strict
python -m unittest discover -s tests -v
```

<br>

<p align="center"><sub>
화면 문법은 소형 하드웨어 계측기(Teenage Engineering 류)에서 영감을 받았고, 해당 회사와는 관련이 없습니다.
</sub></p>
