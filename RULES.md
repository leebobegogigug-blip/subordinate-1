# subordinate-1 규칙

이 저장소의 규칙이다. [works](https://github.com/leebobegogigug-blip/Works) 의 규칙을 채택하고 **W-02 하나만 바꾼다.** 채택 근거와 표는 [docs/PLAN.md](docs/PLAN.md) 02 에 있다.

- 에이전트용 요약 → [AGENTS.md](AGENTS.md)
- 기획 → [docs/PLAN.md](docs/PLAN.md)

## works 와의 관계

- 이 파일의 규칙 문장은 works `RULES.md` 의 **복사본**이다. works 가 바뀌어도 자동으로 따라가지 않고, 이 저장소가 달리 쓰면 갈라질 수 있다.
- 복사한 때의 works 커밋: `6c9337753f34f1ec747107e9a2bfe2ab47589171` ([그 시점의 works RULES.md](https://github.com/leebobegogigug-blip/Works/blob/6c9337753f34f1ec747107e9a2bfe2ab47589171/RULES.md)).
- works 와 달라지는 조항은 이 파일에 적는다. 지금 다른 것은 W-02 하나다.
- works 의 앱 대장과 예외 대장은 이 저장소에 없다. 규칙을 어기려면 이 파일을 먼저 고친다.

## 등급

| 등급 | 뜻 | 어기면 |
|---|---|---|
| **헌법 W** | 모든 코드와 문서가 지킨다 | 머지하지 않는다. 바꾸려면 이 파일을 고치는 PR 이 먼저 들어간다 |
| **규약 S** | 따른다 | 따르지 않을 때는 이유를 PR 이나 `docs/MANUAL.md` 의 `알려진 한계` 에 적는다 |

---

## 헌법

### W-01 저장소 하나 = 도구 하나
- 이 저장소가 도구 하나다. 모양은 스킬 + opencode 어댑터 + 파이썬 패키지 `subordinate1` 이고, 명령은 `subordinate-1` 하나다 (docs/PLAN.md 06).
- 필수 구성: `README.md` · `INSTALL.md` · `docs/MANUAL.md` · `tests/` · `.gitignore` · `.gitattributes` · `.github/workflows/`. 설치 · 매뉴얼은 M0 결과가 나온 뒤에 만든다. 내용 없는 빈 파일을 먼저 두지 않는다.
- 다른 도구(Analysis–1 포함)와 코드 · 형식 · 일정을 공유하지 않는다.

### W-02 고정 의존 목록 (works 와 다른 조항)
- works 의 'Python 3.8+ 표준 라이브러리만' 을 **바꾼다.** 실행에 쓰는 외부 패키지는 `requirements.txt` 에 적은 것뿐이고, 판은 모두 `==` 로 고정한다.
- 의존의 라이선스는 허용 목록 안이어야 한다: MIT · BSD · Apache-2.0 · PSF · matplotlib 라이선스. 목록 밖(AGPL · GPL 포함)은 쓰지 않는다.
- 선택 기능은 렌더 검사뿐이다: PowerPoint COM(`pywin32`) 또는 LibreOffice. 함수 안에서 불러오고, 없으면 그 기능만 꺼진다.
- 최소 Python 판과 고정할 판은 M0 정찰 뒤에 정하고 그때 이 조항에 적는다.
- `tools/repo_check.py` 는 표준 라이브러리만 쓴다 (설치 없이 CI 첫 단계에서 돈다).

### W-03 내 PC 에서만
- 파이썬 도구는 네트워크를 쓰지 않는다. 서버를 열면 `127.0.0.1` 에만 바인딩한다.
- LLM 과의 통신은 호스트(opencode)가 사용자가 설정한 주소로 한다. 텔레메트리 · 자동 업데이트 확인 · 외부 CDN 금지.

### W-04 비밀은 어디에도 찍지 않는다
- 키 · 토큰 · 비밀번호를 화면 출력 · 로그 · 명령줄 인자 · 커밋에 남기지 않는다. 도구는 키를 다루지 않고 호스트가 다룬다.
- 설정 파일에 값 대신 참조를 쓸 때는 `{env:이름}` · `{file:경로}` 문법을 따른다.

### W-05 사용자 원문은 메모리에만
- 도구 쪽은 사용자가 확정한 `deck.json` 같은 결과만 저장하고, 무엇이 저장되는지 미리 보인다.
- opencode 가 대화를 자기 데이터베이스에 남기는 것은 이 규칙 밖이다. 알려진 한계로 `docs/MANUAL.md` 에 적고 지우는 법을 둔다 (docs/PLAN.md 리스크 9).

### W-06 저장은 깨지지 않게
- 저장 파일에 형식 버전을 적고, `.tmp` 에 쓴 뒤 바꿔치기한다. 깨진 파일은 `.broken` 으로 백업한다. 더 새 버전의 파일은 덮어쓰지 않는다.
- 사용자 데이터(템플릿 · 매핑 · 설정)는 `%LOCALAPPDATA%\subordinate-1\` (Windows 밖에서는 `~/.local/share/subordinate-1/`) 에 둔다. 저장소 폴더 안에 두지 않는다.
- 시험은 환경 변수 `SUBORDINATE_HOME` 으로 데이터 폴더를 바꿔서 한다.

### W-07 바꾸기 전에 보여 준다
- 템플릿 등록과 PPTX 저장은 미리보기 › 확정 두 단계다. 결과 파일은 덮어쓰지 않는다.

### W-08 설치는 에이전트가, 되돌릴 수 있게
- `INSTALL.md` 는 opencode 가 그대로 따라 하는 절차다. 필수: 규칙 절 · 단계마다 확인과 실패 시 할 일 · `[질문]` 표시 · 보고 형식 · 문제 해결 · 업데이트 · 제거.
- 관리자 권한 금지. 같은 이름의 파일이 있으면 덮어쓰지 않고 묻는다. 제거는 설치가 복사한 파일만 지운다.
- 설치 위치는 `D:\OPENCODE\subordinate-1` 이다.

### W-09 이름을 바꾸면 데려간다
- 이름은 `subordinate-1` (화면 `Subordinate–1`) 이다. 공개한 뒤에는 바꾸지 않는다.
- 바꿔야 하면 예전 이름의 데이터 · 설정을 첫 실행 때 자동으로 옮기고, 덮어쓰지 않는다.

### W-10 디자인은 하나
- 도구의 문서와 그림은 works 의 [DESIGN.md](https://github.com/leebobegogigug-blip/Works/blob/6c9337753f34f1ec747107e9a2bfe2ab47589171/docs/DESIGN.md) 를 따른다. 규칙과 팔레트 값은 옮겨 적지 않고 링크한다.
- 산출 PPTX 는 사용자가 등록한 회사 템플릿의 색을 쓴다. 템플릿이 없을 때의 기본 템플릿은 비상용이다.

### W-11 약속은 CI 가 지킨다
- CI 는 Windows + Ubuntu 에서 `tools/repo_check.py --strict` 와 `python -m unittest discover -s tests` 를 돌린다. 최소 Python 판이 정해지면 최소 · 최신 두 판으로 넓힌다.
- 테스트는 표준 라이브러리 `unittest` 로 쓴다. 도구가 LLM 을 부르지 않으므로 LLM 이 쓴 결과는 기록한 합성 예시로 대신한다.
- README 에 적는 숫자와 사양은 CI 나 검사기가 확인할 수 있는 것만 적는다.

### W-12 공개 저장소다
- 회사 템플릿 · 로고 · 실데이터 · 실제 장표 · 사내 주소 · 회사명 · 동료 실명 · 내부 시스템 이름을 커밋하지 않는다. 예시와 시험은 지어낸 것만 쓴다 (주소는 `example.com` 처럼 실재하지 않는 것).
- 합성 자료만 `tests/fixtures/` · `kit/**/synthetic/` · `docs/images/` 에 둘 수 있다. `.gitignore` 와 `tools/repo_check.py` 가 이 자리 밖의 Office · 데이터 · 그림 파일, 비밀처럼 보이는 문자열, 사설 IP 주소를 막는다.
- README 끝에 영감 고지문을 둔다. 저장소 라이선스는 MIT(`LICENSE`)이고, 차용한 코드와 자산의 고지는 따로 둔다.

---

## 규약

| # | 규약 |
|---|---|
| S-01 | **이름.** 화면 표기는 `Subordinate–1` (en dash `–`, U+2013), 폴더 · 명령 · 데이터 폴더는 `subordinate-1`, 파이썬 패키지는 `subordinate1`. 코드 상수는 `APP` · `NAME` · `VERSION` |
| S-02 | **버전.** `VERSION = "x.y.z"` 상수 하나를 두고 `subordinate-1 version` 으로 보여 준다 |
| S-03 | **명령과 종료 코드.** 공통 동작의 이름은 `setup` · `check` · `status` · `version` · `help`. 종료 코드는 `0` OK · `1` 점검 실패 · `2` 사용법 오류 · `3` 사람 확인 필요. 점검 출력의 마지막 줄은 `결과: OK` · `결과: 확인 필요` · `결과: 점검 실패` 중 하나다 (에이전트가 이 줄로 판단한다) |
| S-05 | **Windows 가 본 무대.** 경로는 큰따옴표로 감싸고, 명령은 cmd · PowerShell · Git Bash 에서 그대로 돌게 쓴다. PowerShell 5.1 호환. `.ps1` · `.cmd` · `.bat` 은 CRLF. 콘솔 출력은 UTF-8 |
| S-08 | **커밋.** 한국어로 `subordinate-1: 무엇 · 무엇`. 한 커밋에 한 가지 일만 담는다 |

- 번호는 works 와 맞춘다. 채택하지 않은 규약은 S-04(앱 유형 — 이 도구에는 해당 없음) · S-06(앱 대장 — 저장소가 하나) · S-07(문서 뼈대 — 앱 여럿일 때의 규칙) · S-09(LLM 설정 규격 — LLM 은 호스트가 부른다)이다.
- 문서의 구분은 ` · `, 넘어가기는 `›` 를 쓴다. 코드 · 영문 · 숫자 뒤의 조사는 띄어 쓴다. 이모지와 폭 2칸 기호를 넣지 않는다.

## 검사기

```text
python tools/repo_check.py              검사한다 (걸린 것이 있어도 종료 코드 0 — 고치는 중에 볼 때)
python tools/repo_check.py --strict     걸린 것이 있으면 종료 코드 1 (CI 가 쓰는 차단 모드)
python tools/repo_check.py --all-files  git 목록 대신 폴더 전체를 걷는다
```

- 가짜 값이 일부러 들어가야 하는 줄(시험 자료 등)은 줄 안에 `repo-check: allow` 를 적으면 글 검사를 건너뛴다. 허용 폴더 밖의 파일 종류 검사에는 통하지 않는다.
- 검사기가 못 보는 조항(W-05 · W-07 · W-09 등)은 리뷰에서 본다.

## 규칙 바꾸기

- 조항을 바꾸는 PR 은 그 조항만 바꾼다. `AGENTS.md` 요약과 검사기도 같은 PR 에서 맞춘다.
- works 에서 가져온 문장을 이 저장소 사정에 맞게 고치면 위 'works 와의 관계' 에 갈라진 점을 적는다.
