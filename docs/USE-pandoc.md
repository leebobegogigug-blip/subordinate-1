# deck.md 를 pandoc 으로 PPTX 로 바꾸기

`Subordinate–1` 이 써 준 보고 장표 원고 `deck.md` 를 pandoc 으로 PPTX 파일로 바꾸는 절차입니다. `deck.md` 의 형식은 [SPEC-deck-md.md](SPEC-deck-md.md) 에 있습니다.

> **알려진 한계.** 회사 양식(템플릿)에 맞추는 일은 이 묶음 밖입니다 ([PLAN.md](PLAN.md) › 00). 회사 양식을 pandoc 이 받는지, 손으로 옮기는 데 얼마나 드는지는 [미확인] 이고 사내 시범(T22)에서 잽니다. 이 문서의 회사 양식 `[미확인]` (4 · 5 절) 은 [PILOT.md](PILOT.md) 5 절 표의 9 – 12 번과 템플릿분으로 잽니다. 아래 `[실험: pandoc 3.1.3]` 은 이 저장소에서 합성 예시 (`docs/examples/deck_synthetic.md`) 로 돌려 본 것, `[문헌]` 은 공식 자료만 본 것, `[추정]` 은 그 위에서 늘린 판단입니다. pandoc 3.1.3 보다 새 판의 동작은 [미확인] 입니다.

## 1 설치 (관리자 권한 없이)

pandoc 은 이미 있으면 설치하지 않습니다.

1. 명령 창(cmd 또는 PowerShell)에서 `pandoc --version` 을 칩니다. 첫 줄에 판이 나오면 이 절은 건너뜁니다.
2. 없으면 pandoc 공식 배포의 **zip 파일** 을 받습니다. 받는 곳은 pandoc 의 GitHub 릴리스 쪽 `https://github.com/jgm/pandoc/releases` 입니다. 공식 설치 안내는 zip 에 대해 "pandoc 의 실행 파일과 문서가 들어 있다 · 압축을 풀어 원하는 폴더에 두면 된다" 고 합니다 [문헌]. zip 파일 이름은 이 세션에서 확인하지 못했습니다 [미확인 — 릴리스 목록에서 Windows 용 zip 을 고릅니다].
3. 압축을 사용자가 쓸 수 있는 폴더(예: `D:\TOOLS\pandoc`)에 풉니다. 설치 프로그램을 돌리지 않으므로 관리자 권한이 필요 없습니다.
4. 풀린 폴더 안의 `pandoc.exe` 를 경로째 불러 판을 확인합니다. 경로는 큰따옴표로 감쌉니다.

   ```text
   "D:\TOOLS\pandoc\pandoc.exe" --version
   ```

   PATH 에 넣지 않아도 되고, 이 문서의 `pandoc` 자리에 위 전체 경로를 쓰면 됩니다.
5. msi 설치 프로그램은 공식 안내에 "pandoc 을 설치하고 이전 판을 바꾸고 PATH 를 고친다" 고만 있습니다 [문헌]. 사용자 단위로 설치되는지 관리자 권한을 묻는지는 확인하지 못했습니다 [미확인]. **관리자 권한이 필요하다고 나오면 msi 는 쓰지 않습니다.** zip 길만 씁니다.
6. 회사 정책상 새 프로그램에 승인이 필요하면 받고 나서 합니다. 승인을 받으려고 이 저장소의 내용을 사내에 올릴 필요는 없습니다.

## 2 바꾸기 (기본 양식)

1. `deck.md` 와 그림이 있는 **자료 폴더** 로 갑니다. 그림은 `deck.md` 가 가리키는 상대 경로로 찾기 때문에 다른 폴더에서 돌리면 안 됩니다.

   ```text
   cd /d "D:\자료\보고1"
   ```

   - 다른 드라이브로 옮길 때 cmd 의 `cd` 는 드라이브를 바꾸지 못하고 `cd /d` 가 필요하다고 알려져 있습니다. PowerShell 은 `cd` 만 쓰면 됩니다 [추정 — Windows 에서 이 저장소가 돌려 보지 못함].
   - 경로에 공백이 있으면 큰따옴표로 감쌉니다.
2. 기본 양식으로 먼저 만듭니다. 회사 양식은 그다음입니다.

   ```text
   pandoc deck.md -o deck.pptx
   ```

   합성 예시로 돌린 결과: 종료 0 · 10장 (표지 1 · 본문 9) · 그림 3개가 모두 들어감 · 발표자 노트 3장 [실험: pandoc 3.1.3].
3. 같은 이름의 `deck.pptx` 가 있으면 pandoc 은 **묻지 않고 덮어씁니다** [추정 — 일반 동작이고 이번에 따로 시험하지 않음]. 예전 결과를 남기려면 `-o deck-2.pptx` 처럼 다른 이름을 씁니다.
4. `deck.pptx` 를 PowerPoint 로 열어 3절의 확인을 합니다.

### 그림이 빠질 때

- 자료 폴더가 아닌 곳에서 돌리면 `File … not found in resource path` 가 나옵니다. 이 판에서는 **종료 99 로 멈추고 PPTX 가 만들어지지 않았습니다** [실험: pandoc 3.1.3 · 합성 예시 · T18 에서 두 번 다시 잼]. 새 판에서는 [미확인].
- 그림이 있는 폴더가 따로면 찾는 경로를 줍니다 [문헌: `--resource-path=SEARCHPATH` · 주지 않으면 지금 폴더].

  ```text
  pandoc deck.md --resource-path="D:\자료\보고1" -o deck.pptx
  ```

  [실험: pandoc 3.1.3 · 다른 폴더에서 돌려 성공]
- 그림이 안 들어갔는지는 `deck.md` 의 그림 줄 (`![img2 · …](경로)`) 개수와 PPTX 안 그림 개수를 대 보면 압니다.

### 발표자 노트

`deck.md` 의 `::: notes` 안 글은 PowerPoint 의 발표자 노트로 들어갑니다 [문헌: 매뉴얼의 speaker notes · 실험: 합성 예시 3장 모두]. 노트에는 '해석 근거' 가 있으므로 PPTX 를 밖으로 보낼 때 노트를 지울지 정합니다.

## 3 바꾼 뒤 확인

`deck.md` 가 원본이고 PPTX 는 사본입니다. pandoc 은 글을 다시 쓰지 않지만 눈으로 한 번 봅니다.

1. 장 수가 `deck.md` 의 `##` 제목 수 + 표지 1 인지 봅니다 (합성 예시: 9 + 1).
2. 꼬리표 (`[f003]` · `[추정 · img2]` · `[미확인]`) 와 숫자가 그대로인지 몇 장 봅니다. pandoc 은 작은따옴표를 둥근 따옴표로 바꾸는 정도만 합니다 [실험: pandoc 3.1.3].
3. 글이 장 밖으로 넘치는 곳이 없는지 봅니다. 기본 양식에서 근거 목록은 장마다 7줄이 한계였습니다 [실험: LibreOffice 렌더 — PowerPoint 렌더는 미확인].
4. 한계 장이 남아 있는지 봅니다. 지울 수 없는 장입니다.

## 4 회사 양식으로 바꾸기 (`--reference-doc`)

1. pandoc 이 꺼내 주는 기본 양식을 내 양식의 바탕으로 씁니다 [문헌: 매뉴얼의 예시 명령].

   ```text
   pandoc -o custom-reference.pptx --print-default-data-file reference.pptx
   ```

   [실험: pandoc 3.1.3 · 종료 0 · 레이아웃 11개 `Title Slide` · `Title and Content` · `Section Header` · `Two Content` · `Comparison` · `Title Only` · `Blank` · `Content with Caption` · `Picture with Caption` 등]
2. 양식을 주고 바꿉니다.

   ```text
   pandoc deck.md --reference-doc="custom-reference.pptx" -o deck.pptx
   ```

   양식 파일이 없으면 종료 99 입니다 [실험: pandoc 3.1.3].
3. 매뉴얼은 PowerPoint 2013 의 양식 (`.pptx` · `.potx`) 이 "된다고 알려져 있다" 고 합니다 [문헌]. pandoc 은 레이아웃을 **이름** 으로 찾습니다 (`Title Slide` · `Title and Content` · `Section Header` · `Two Content` · `Comparison` · `Content with Caption` · `Blank`; 같은 이름이 여럿이면 처음 것) [문헌]. 이름이 없으면 경고를 냅니다 [문헌].
4. 합성 양식 시험 결과 ([SPEC-deck-md.md](SPEC-deck-md.md) 11) [실험: pandoc 3.1.3 · 합성 양식에서만]:

   | 양식 | 결과 |
   |---|---|
   | 레이아웃 이름이 표준 이름과 모두 다름 | 종료 0 · 경고 7. pandoc 기본 레이아웃이 양식의 마스터 밑에 들어가고 배경 · 색 · 글꼴은 양식 것이 남음 |
   | 표준 이름은 있고 본문 자리표시자가 없음 | **실패** · 종료 63 · PPTX 가 나오지 않음 |

   기본 양식의 레이아웃 이름만 바꿔 다시 시험했을 때도 종료 0 · 경고 7 이었습니다 [실험: pandoc 3.1.3 · 이번 재현].
5. 그래서 회사 양식에서 할 수 있는 것 [추정]:
   - 먼저 4절 1단계의 기본 양식을 `--reference-doc` 으로 줘 보고 정상인지 확인합니다 (양식 문제와 `deck.md` 문제를 가르는 일).
   - 회사 양식으로 종료 63 이 나면 **양식 사본** 의 레이아웃 이름을 PowerPoint 의 슬라이드 마스터 보기에서 표준 이름과 다르게 바꿉니다. 원본 양식은 건드리지 않습니다.
   - 얻는 것은 양식의 배경 · 색 · 글꼴이고, 자리 배치는 pandoc 기본입니다. 양식 고유의 레이아웃은 쓰이지 않습니다.
6. 실제 회사 양식의 레이아웃 이름 · pandoc 이 받아들이는지는 [미확인] 입니다. 양식 파일은 저장소에 복사하지 않습니다.

## 5 회사 양식 위로 손으로 옮기기 [미확인 — T22 에서 시간을 잰다]

pandoc 이 회사 양식을 받지 못할 때의 후보일 뿐이고 이 저장소는 해 보지 않았습니다 ([PLAN.md](PLAN.md) 리스크 23).

- 후보 1: 회사 양식 파일을 열고 기본 양식으로 만든 `deck.pptx` 의 장을 붙여 넣은 뒤 붙여넣기 옵션의 '대상 테마 사용' 을 고릅니다.
- 후보 2: 회사 양식 파일에서 '슬라이드 다시 사용' 으로 `deck.pptx` 의 장을 가져옵니다.
- 두 길 모두 그림 · 두 단 배치 · 노트가 어떻게 되는지, 몇 분 드는지 [미확인] 입니다.

## 6 지우기 (되돌리기)

1. zip 으로 푼 폴더를 지웁니다. 설치 프로그램을 돌리지 않았으므로 이것이 전부입니다. PATH 를 직접 고쳤다면 그 항목도 지웁니다.
2. 만든 `deck.pptx` 와 양식 사본은 자료 폴더에서 지웁니다. `deck.md` 는 원본이므로 지우지 않습니다.
3. pandoc 의 사용자 자료 폴더 (`pandoc --version` 에 'User data directory' 로 나옵니다) 에 `reference.pptx` 를 직접 두지 않았다면 지울 것이 없습니다 [문헌: 사용자 자료 폴더의 파일은 기본값을 덮어쓴다].

## 7 자료가 밖으로 나가는가

- pandoc 은 `deck.md` 와 그림을 읽어 PPTX 를 쓸 뿐이고, 이 저장소의 사용에서 네트워크를 쓰는 곳은 없습니다. 다만 pandoc 이 어떤 경우에도 네트워크를 쓰지 않는지는 공식 자료로 확인하지 못했습니다 [미확인]. `deck.md` 에 `http://` 로 시작하는 그림 주소를 넣지 않으면 (스킬은 상대 경로만 씁니다) 내려받을 것이 없습니다 [추정].
- 키는 이 도구에 필요 없습니다. 명령줄에도 설정에도 키를 넣지 않습니다.

## 확인한 자료

확인한 날짜: 2026-11-03. pandoc.org 는 이 세션의 네트워크가 막혀 열지 못했고, 같은 내용의 GitHub 원문을 읽었습니다.

- 설치 안내 (Windows 절): https://github.com/jgm/pandoc/blob/main/INSTALL.md — msi · zip 설명. zip 이름 · msi 의 관리자 권한은 없음
- 매뉴얼: https://raw.githubusercontent.com/jgm/pandoc/refs/heads/main/MANUAL.txt — 판 헤더의 날짜 2026-10-25. `--reference-doc` · `--print-default-data-file` · `--resource-path` · 레이아웃 이름 · speaker notes · columns
- 릴리스: https://github.com/jgm/pandoc/releases/latest — 최신 3.13 (페이지에 26 Oct 로 표시). 파일 목록은 열리지 않음
- 직접 돌린 판: pandoc 3.1.3 (이 저장소의 개발 컨테이너 · Linux). Windows 에서의 실행은 [미확인]
