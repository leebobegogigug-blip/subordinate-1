# Subordinate–1 설치 가이드 — opencode 에이전트용

> **사람용 한 줄:** opencode 에 아래 프롬프트를 붙여넣으면 이 문서대로 설치합니다.
> Subordinate–1 은 앱이 아니라 opencode 에 더하는 스킬 · 에이전트 · 명령 묶음입니다. 저장소는 `D:\OPENCODE\subordinate-1` 에 받아 둡니다.
>
> ```text
> Subordinate–1 을 설치해줘. 저장소는 D:\OPENCODE\subordinate-1 에 받아 줘.
> 1. 코드 받기: D:\OPENCODE\subordinate-1 이 없으면 git clone https://github.com/leebobegogigug-blip/subordinate-1.git "D:\OPENCODE\subordinate-1"
>    (이미 받아져 있으면 받지 말고, git 이 안 되면 zip 을 그 폴더에 풀어 달라고 나한테 물어)
> 2. 그다음 D:\OPENCODE\subordinate-1\INSTALL.md 를 끝까지 읽고 그 순서대로만 진행해.
>    API 키는 절대 출력하지 말고, [질문] 표시가 있는 곳에서는 멈추고 나한테 물어봐.
> ```

---

이 아래는 **opencode(에이전트)가 실행할 절차**입니다.

## 0. 목표와 규칙

**목표**: 파일 세 개를 opencode 전역 설정 폴더 `%USERPROFILE%\.config\opencode\` 에 복사하고, 사내 모델이 그림을 받도록 `modalities` 를 확인한 뒤, 시험으로 `/subordinate` 의 첫 메시지까지 본다.

| 저장소의 파일 | 복사해 둘 자리 (전역 설정 폴더 아래) |
|---|---|
| `skills\subordinate-1\SKILL.md` | `skills\subordinate-1\SKILL.md` |
| `opencode\agents\subordinate-1.md` | `agents\subordinate-1.md` |
| `opencode\commands\subordinate.md` | `commands\subordinate.md` |

심볼릭 링크는 쓰지 않습니다 (관리자 권한 · 개발자 모드가 필요할 수 있음). 복사만 합니다. 파이썬은 필요 없습니다.

**규칙 — 반드시 지킬 것**

1. **명령은 이 문서에 적힌 것만** 실행한다. 명령은 PowerShell 기준이고, cmd 가 다르면 함께 적었다. 경로는 항상 큰따옴표.
2. **비밀 금지 (W-04)**: `opencode.json` · `opencode.jsonc` · `auth.json` 을 통째로 읽거나 출력하지 않는다 (`cat` · `type` · `Get-Content` · 읽기 도구 모두). 필요한 칸만, 이 문서의 명령으로 본다. 키 값이 화면에 나왔으면 보고에 옮기지 말고 사용자에게 알린다. 사용자가 키를 채팅에 붙이려 하면 말린다.
3. **키를 고치지 않는다.** `apiKey` 가 값으로 적혀 있으면 3단계에서 멈추고 사용자에게 알린다. 옮기는 일은 사용자가 한다.
4. **덮어쓰지 않는다 (W-07 · W-08)**: 같은 이름의 파일이 있고 내용이 다르면 차이를 보이고 **[질문]**. 덮어쓰기 전에는 반드시 `.bak` 백업.
5. **관리자 권한 · 실행 정책 변경 · 시스템 PATH · 레지스트리 금지.** 명령은 사용자 폴더 안에서만.
6. **[질문]** 표시가 있는 곳에서는 멈추고 사용자에게 묻는다. 답을 기다린다.
7. 출력이 예상과 다르면 추측해서 우회하지 말고, 출력을 그대로 보여 주고 [문제 해결](#문제-해결)을 따른다. 표에 없으면 멈추고 보고한다.
8. 명령은 한 번에 하나씩 실행하고 결과를 확인한 뒤 다음으로 간다.
9. 보고 · 대화에 사내 주소 · 모델 이름을 적지 않는다 ('사내 모델 1개' 처럼).

## 1. 저장소 확인

```powershell
Test-Path "D:\OPENCODE\subordinate-1\skills\subordinate-1\SKILL.md"
```

cmd: `if exist "D:\OPENCODE\subordinate-1\skills\subordinate-1\SKILL.md" (echo True) else (echo False)`

- **확인**: `True` 면 2단계로.
- **실패하면**: 폴더가 없으면 `git clone https://github.com/leebobegogigug-blip/subordinate-1.git "D:\OPENCODE\subordinate-1"` 을 실행한다. 폴더가 있는데 위 파일이 없거나, git 이 없거나 막혔으면 **[질문]** 목록을 보여 주고 어떻게 할지 묻는다 (zip 을 풀어 달라고 부탁할 수 있다). 아무것도 지우거나 옮기지 않는다.

## 2. 설정 폴더 찾기

opencode 는 설정 폴더를 `~/.config/opencode` 로 읽는다. Windows 에서는 `%USERPROFILE%\.config\opencode` 다. 하위 폴더 이름은 **복수형** (`agents` · `commands` · `skills`) 이다.

```powershell
"OPENCODE_CONFIG_DIR=[$env:OPENCODE_CONFIG_DIR]"
"OPENCODE_CONFIG=[$env:OPENCODE_CONFIG]"
Test-Path "$env:USERPROFILE\.config\opencode"
```

- **확인**: `OPENCODE_CONFIG_DIR=[]` (비어 있음) 이면 전역 설정 폴더 `%USERPROFILE%\.config\opencode` 를 쓴다. 폴더가 없으면 (`False`) 3단계의 복사가 만든다.
- `OPENCODE_CONFIG_DIR` 가 비어 있지 않으면 **[질문]** "`OPENCODE_CONFIG_DIR` 가 설정돼 있습니다. 세 파일을 그 폴더에 둘까요, 전역 설정 폴더 `%USERPROFILE%\.config\opencode` 에 둘까요?" 답을 받은 곳을 이후 `<설정 폴더>` 로 쓴다.
- 옛 단수형 폴더 확인:

```powershell
Test-Path "$env:USERPROFILE\.config\opencode\agent\subordinate-1.md"
Test-Path "$env:USERPROFILE\.config\opencode\command\subordinate.md"
```

둘 다 `False` 여야 한다. 하나라도 `True` 면 **[질문]** "단수형 옛 폴더에 같은 이름의 파일이 있습니다. opencode 가 복수형과 단수형이 겹칠 때 어느 쪽을 쓰는지 문서에서 확인하지 못했습니다 **[미확인]**. 옛 파일을 `.bak` 으로 바꿔 둘까요, 그대로 두고 복수형에도 복사할까요?" 사용자 답대로 한다 (이름 바꾸기는 `Rename-Item` 으로 `.bak` 을 붙이고, 같은 이름의 `.bak` 이 이미 있으면 멈추고 묻는다).
- **실패하면**: 명령 출력이 위와 다르면 그대로 보여 주고 멈춘다.

## 3. 세 파일 복사

아래 명령을 파일마다 하나씩 실행한다. `$repo` · `$cfg` 는 명령마다 다시 적는다 (셸이 상태를 이어 주지 않을 수 있음). `$cfg` 는 2단계에서 정한 `<설정 폴더>` 다.

먼저 상태를 본다 (복사하지 않음). 아래는 스킬 파일 예시이고, 에이전트 · 명령 파일은 경로를 바꿔 같은 식으로 본다.

```powershell
$repo = "D:\OPENCODE\subordinate-1"; $cfg = "$env:USERPROFILE\.config\opencode"
$src = "$repo\skills\subordinate-1\SKILL.md"; $dst = "$cfg\skills\subordinate-1\SKILL.md"
if (-not (Test-Path $dst)) { "새로" }
elseif ((Get-FileHash $src).Hash -eq (Get-FileHash $dst).Hash) { "이미 설치됨" }
else { "다름" }
```

경로 바꾸기: 에이전트는 `$src = "$repo\opencode\agents\subordinate-1.md"` · `$dst = "$cfg\agents\subordinate-1.md"`, 명령은 `$src = "$repo\opencode\commands\subordinate.md"` · `$dst = "$cfg\commands\subordinate.md"`.

| 결과 | 할 일 |
|---|---|
| `새로` | 복사한다 (아래) |
| `이미 설치됨` | 내용이 같다. 건너뛰고 '이미 있음' 으로 기록한다 |
| `다름` | 차이를 보인다 (아래). **[질문]** "`<파일>` 이 이미 있고 저장소 것과 다릅니다. 백업(`.bak`) 해 두고 덮어쓸까요, 건너뛸까요?" 덮어쓴다고 하면 백업 뒤 복사. 건너뛴다고 하면 '건너뜀' 으로 기록한다 |

차이 보이기 (키가 들어 있는 파일이 아니므로 내용을 보여도 된다):

```powershell
Compare-Object (Get-Content $src) (Get-Content $dst) | Select-Object -First 20
```

백업 (이미 `.bak` 이 있으면 덮어쓰지 않고 시각을 붙인다):

```powershell
$bak = "$dst.bak"; if (Test-Path $bak) { $bak = "$dst." + (Get-Date -Format "yyyyMMdd-HHmmss") + ".bak" }
Copy-Item $dst $bak
```

복사 (폴더를 먼저 만든다):

```powershell
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
Copy-Item $src $dst
```

cmd 를 쓰면 `mkdir` 과 `copy "원본" "대상"` 으로 같은 일을 한다 (덮어쓸 때는 `copy /Y`, 사용자 동의 뒤에만).

- **확인**: 세 파일 모두 `Test-Path` 가 `True`, 해시가 저장소 것과 같음 (건너뛴 것은 제외).
- **실패하면**: 오류 문구를 그대로 보고하고 멈춘다. 권한 오류면 관리자 권한으로 바꾸려 하지 않는다. 사용자에게 알린다.
- 파일 이름은 그대로 둔다. `SKILL.md` 는 대문자이고, 스킬 폴더 이름은 머리말의 `name` (`subordinate-1`) 과 같아야 한다.

## 4. 사내 모델에 그림 입력 (modalities) — 필수

**까닭**: 이 도구는 자료 폴더의 차트 그림을 읽는다. M0 시험에서 사내 모델의 설정에 `modalities` 가 없을 때는 그림이 모델에 닿지 않았고, `"modalities": { "input": ["text", "image"], "output": ["text"] }` 를 더하자 닿았다. 이 키는 opencode 의 provider 설정 소스에는 있으나 사용자 문서에는 없다 **[미확인 — 없을 때의 동작 · opencode 판마다 같은지]**.

### 4-1. 사내 모델이 정의된 설정 파일 찾기

설정은 여러 곳에서 합쳐진다 (낮은 우선순위부터): 전역 `opencode.json` › `OPENCODE_CONFIG` 가 가리키는 파일 › 프로젝트의 `opencode.json`. 사내 모델이 어느 파일에 정의됐는지 찾는다. 키 값이 찍히지 않도록 **참 · 거짓만** 나오는 명령을 쓴다.

```powershell
$c = @("$env:USERPROFILE\.config\opencode\opencode.json", "$env:USERPROFILE\.config\opencode\opencode.jsonc", $env:OPENCODE_CONFIG, "D:\OPENCODE\opencode.json") | Where-Object { $_ -and (Test-Path $_) }
$c | ForEach-Object { "{0} : provider 있음={1}" -f $_, ((Get-Content -Raw -Encoding UTF8 $_) -match '"provider"\s*:') }
```

- **확인**: `provider 있음=True` 인 파일이 하나면 그 파일을 `<설정 파일>` 로 쓴다. 둘 이상이거나 하나도 없으면 **[질문]** "사내 모델이 정의된 설정 파일이 어느 것입니까?" (경로만 묻는다). 열려 있는 프로젝트 폴더가 다르면 그 폴더의 `opencode.json` 도 후보다.
- 위 명령은 목록 안의 흔한 자리만 본다. 사용자가 다른 자리를 말하면 그 경로로 같은 식으로 확인한다.

### 4-2. 키가 값으로 적혀 있지 않은지 확인 (W-04)

```powershell
(Get-Content -Raw -Encoding UTF8 "<설정 파일>") -match '"apiKey"\s*:\s*"(?!\{env:|\{file:)'
```

- `False` 면 통과 (`{env:…}` 또는 `{file:…}` 참조뿐이거나 apiKey 칸이 없음). 4-3 으로 간다.
- `True` 면 **여기서 멈춘다.** 파일을 더 읽거나 고치지 않는다. **[질문]** "설정 파일에 API 키가 값으로 적혀 있습니다. 환경 변수로 옮기시고 (예: 환경 변수 `INHOUSE_LLM_KEY` 를 만들고 파일에는 `\"apiKey\": \"{env:INHOUSE_LLM_KEY}\"` 로 적기) 알려 주십시오. 옮기는 일은 직접 해 주십시오. 키 값은 저에게 알려 주지 마십시오." 사용자가 옮겼다고 하면 이 단계를 다시 한다.

### 4-3. modalities 가 이미 있는지 보기

파일이 순수 JSON 이면 (주석 없음) 모델 이름과 `modalities` 유무만 뽑는다. 값은 찍지 않는다.

```powershell
$j = Get-Content -Raw -Encoding UTF8 "<설정 파일>" | ConvertFrom-Json
foreach ($p in $j.provider.PSObject.Properties) { foreach ($m in $p.Value.models.PSObject.Properties) { "{0} / {1} : modalities={2} image={3}" -f $p.Name, $m.Name, ($null -ne $m.Value.modalities), ($m.Value.modalities.input -contains "image") } }
```

- 사내 모델이 하나뿐이면 그것이다. 여럿이면 **[질문]** "그림을 읽을 모델이 어느 것입니까?" (대화에 이름이 보이는 것은 괜찮지만 보고에는 쓰지 않는다).
- **확인**: 그 모델이 `modalities=True image=True` 면 '있었음' 으로 기록하고 5단계로.
- `modalities=False` 거나 `image=False` 면 4-4 로. (`modalities` 는 있는데 `image` 만 없으면 4-4 에서 새 줄을 더하지 않고 그 줄의 `input` 에 `"image"` 만 더한다.)
- **실패하면**: `ConvertFrom-Json` 이 오류를 내면 (주석 · 끝 쉼표가 있는 `.jsonc` 일 수 있음) 4-4 에서 줄을 직접 보여 주고 사용자가 고치게 하거나, 모델 이름이 있는 줄 번호만 찾는다 — `Select-String -Path "<설정 파일>" -Pattern '"<모델 이름>"' | Select-Object LineNumber` (줄 번호만 나온다. 이름은 사용자에게 묻는다).

### 4-4. 한 줄 더하기

바꿀 곳은 **그 모델 칸 하나**, 더할 것은 **이 한 줄**이다. 다른 칸은 손대지 않는다.

```json
"modalities": { "input": ["text", "image"], "output": ["text"] }
```

모델 칸 안에서 앞 줄 끝에 쉼표를 붙이고 이 줄을 더한 모양이다 (주소 · 이름은 자리표시).

```json
"models": {
  "inhouse-model": {
    "name": "inhouse-model",
    "modalities": { "input": ["text", "image"], "output": ["text"] }
  }
}
```

**[질문]** "`<설정 파일>` 의 사내 모델 칸에 위 한 줄을 더하겠습니다. 더하기 전에 `opencode.json.bak` 으로 백업합니다. 이 줄이 없으면 차트 그림이 모델에 닿지 않습니다. 진행할까요?" 동의하면:

1. 백업 (이미 `.bak` 이 있으면 덮어쓰지 않고 시각을 붙인다. 파일 이름이 `opencode.jsonc` 면 그 이름에 `.bak`):

```powershell
$f = "<설정 파일>"; $bak = "$f.bak"; if (Test-Path $bak) { $bak = "$f." + (Get-Date -Format "yyyyMMdd-HHmmss") + ".bak" }
Copy-Item $f $bak; $bak
```

2. 편집 도구로 **그 모델 칸 안의 줄만** 바꾼다 (`name` 줄 뒤에 더하면 된다) (찾을 글에 `apiKey` · `baseURL` 줄을 넣지 않는다). 앞 줄에 쉼표가 필요한지 보고 맞춘다.
3. 고친 줄만 보인다: `Select-String -Path "$f" -Pattern 'modalities'`. 4-3 의 명령을 다시 돌려 `modalities=True` 이고 오류가 없는지 본다.

- **확인**: `modalities=True` · JSON 오류 없음.
- **실패하면**: JSON 오류가 나면 백업으로 되돌린다 (`Copy-Item "<백업>" "<설정 파일>" -Force` — 이 되돌리기는 방금 만든 백업으로만 한다). 되돌린 뒤 사용자에게 알리고 멈춘다.
- 사용자가 동의하지 않으면 '안 함' 으로 기록하고 계속 진행하되, 보고의 남은 일에 '그림이 닿지 않을 수 있음' 을 적는다.

## 5. 다시 시작하고 확인

**[질문]** "opencode 를 한 번 끝내고 다시 시작해 주십시오. 설정 · 스킬 · 명령은 시작할 때 읽는 것으로 보입니다 **[추정]**. 다시 시작하신 뒤 알려 주십시오." 사용자가 돌아오면 아래를 사용자가 직접 확인하도록 한다.

1. 입력 칸에 `/` 를 쳤을 때 명령 목록에 `/subordinate` 가 보이는가.
2. `Tab` 을 눌러 에이전트를 바꿀 때 `subordinate-1` 이 보이는가.

### 짧은 시험 (합성 자료)

시험 폴더는 저장소 **밖**에 만든다. 시험으로 `deck.md` 가 생겨도 저장소가 더러워지지 않게 하려는 것이다.

```powershell
$repo = "D:\OPENCODE\subordinate-1"; $try = "D:\OPENCODE\subordinate-1-try"
New-Item -ItemType Directory -Force -Path $try | Out-Null
Copy-Item "$repo\tests\fixtures\deck\facts_lite.json" $try
Copy-Item "$repo\docs\images\examples\k2_ctx_1.png", "$repo\docs\images\examples\k2_ctx_2.png", "$repo\docs\images\examples\k2_ctx_3.png" $try
Get-ChildItem $try | Select-Object Name
```

- **확인**: 파일 4개 (`facts_lite.json` · `k2_ctx_1.png` – `k2_ctx_3.png`). 폴더가 이미 있고 내용이 다르면 **[질문]** 덮어써도 되는지 묻는다.

**[질문]** "opencode 는 지금 연 폴더 그대로 두고 (시험 폴더에서 새로 열지 마십시오), `subordinate-1` 에이전트로 `/subordinate D:\OPENCODE\subordinate-1-try` 를 실행해 주십시오. 첫 메시지(미리 보기)까지만 보고 멈추시면 됩니다. 시험 폴더는 opencode 를 연 폴더 밖이라 폴더 밖 접근 허락 창이 뜰 수 있습니다. 허락해도 됩니다." 사용자가 결과를 알려 주면 기대와 맞추어 본다.

**기대한 것**: 사실 `f001` – `f012` 를 읽었다는 요약 · 그림 `img1` – `img3` 의 판독 메모 · '요약에는 있는데 폴더에 없는 그림' 으로 `img4` · `img5` 를 알림 (시험 자료가 일부러 그 두 장을 빼서 정상이다) · 첫 질문 `[질문 1/12 · 틀 1/3]` (번호 목록). 질문에 답하지 않고 멈추면 시험은 끝이다.

| 보인 것 | 할 일 |
|---|---|
| 기대와 같음 | 통과. 시험 폴더는 지워도 된다 (제거 절 참고) |
| 그림 판독이 '안 보임' | 4단계로 돌아가 `modalities` · 관리 설정을 다시 본다 ([문제 해결](#문제-해결)) |
| '스킬을 불러오지 못해 멈췄습니다' 문구 | 3단계의 스킬 파일 위치 · `name` 을 확인한다 ([문제 해결](#문제-해결)) |
| `/subordinate` 가 안 보임 · `subordinate-1` 이 안 보임 | [문제 해결](#문제-해결) |

## 6. 완료 보고

아래 형식으로 사용자에게 보고한다. **키 · 사내 주소 · 모델 이름은 쓰지 않는다.**

```text
Subordinate–1 설치 완료
- 설치한 곳   : (설정 폴더 — 전역 / OPENCODE_CONFIG_DIR) · 저장소 D:\OPENCODE\subordinate-1
- 파일 3개    : 스킬 (새로 / 이미 있음 / 덮어씀 / 건너뜀) · 에이전트 (…) · 명령 (…)
- modalities  : 있었음 / 더함 (사내 모델 1개) / 안 함 — 백업 파일이 생겼으면 그 이름
- 시험 결과   : 명령 보임 (예 / 아니오) · 에이전트 보임 (예 / 아니오) · 첫 메시지 (사실 f001–f012 · 그림 img1–img3 · 질문 1/12) 통과 / 실패 (어느 단계)
- 남은 일     : (없으면 없음. 시험 폴더 정리 · 키를 환경 변수로 옮기기 등)
- 다음        : 장표 만들기 — docs\USE-pandoc.md (회사 자료는 pandoc 쪽부터) · docs\USE-presenton.md (그 문서 2절 확인 뒤)
- 쓸 때 지킬 것: opencode 는 정해 둔 폴더에서 열고 자료 폴더는 명령 인자로 · 허락 창의 always · 자동 승인 쓰지 않기 · 인터뷰 중 Tab 으로 에이전트 바꾸지 않기 · 자료 폴더에 비밀 파일 두지 않기
```

---

## 문제 해결

고친 뒤에는 opencode 를 다시 시작하고 5단계의 확인을 한다.

| 보이는 것 | 조치 |
|---|---|
| `/subordinate` 가 명령 목록에 없음 | 명령 파일이 `<설정 폴더>\commands\subordinate.md` (복수형 `commands`) 에 있는지, opencode 를 다시 시작했는지 본다. 단수형 `command\` 에 옛 파일이 겹쳐 있지 않은지도 본다 (2단계 · **[미확인]**) |
| `Tab` 에 `subordinate-1` 이 없음 | `<설정 폴더>\agents\subordinate-1.md` (복수형) 를 본다. 파일 맨 위 머리말 `mode: primary` 가 그대로 있는지 확인한다 |
| '스킬을 불러오지 못해 멈췄습니다' | 에이전트 파일의 정해진 동작이다 (짐작으로 흉내 내지 않음). `<설정 폴더>\skills\subordinate-1\SKILL.md` 가 있는지 (파일 이름 `SKILL.md` 는 전부 대문자), 머리말의 `name` 이 `subordinate-1` 이고 폴더 이름과 같은지, 머리말에 `description` 이 있는지 본다. 스킬 권한을 `deny` 로 막는 설정이 없는지도 본다 (에이전트 파일은 `subordinate-1` 만 허용) |
| 그림이 '안 보임' · 엉뚱한 설명 | 4단계를 다시 본다. `modalities` 가 사내 모델 칸에 있는지. 다른 설정 파일이 같은 모델을 덮어쓰고 있을 수 있다 (프로젝트의 `opencode.json` 이 전역보다 우선). 회사 관리 설정 `%ProgramData%\opencode` 가 있으면 그 설정이 사용자 설정을 덮을 수 있다 (opencode 문서의 설정 우선순위). 그 폴더는 에이전트가 고치지 않고 사용자에게 알린다 |
| 모델 목록에 사내 모델이 없음 | 설정이 프로젝트 `opencode.json` 에만 있고 지금 다른 폴더에서 연 것일 수 있다. 그 파일을 가리키고 연다 (PowerShell `$env:OPENCODE_CONFIG = "D:\OPENCODE\opencode.json"` · cmd `set OPENCODE_CONFIG=D:\OPENCODE\opencode.json` — 그 창에서만 유효) |
| 자료 폴더를 읽을 때 허락 창 | 자료 폴더가 opencode 를 연 폴더 밖이면 정상이다 (`external_directory`). 허락하면 된다 |
| `deck.md` 를 쓸 때 허락 창 | 정상이다. 쓰기 전에 묻게 해 둔 것이다 (W-07). 거절하면 에이전트가 내용을 대화에 보여 준다 |
| 'question 도구를 쓸 수 없다' 는 말 | 정상이다. 일부러 막아 두었다. 질문은 번호 목록 글로 한다 |
| 다른 도구 (MCP · 사용자 도구 등) 가 막혔다는 말 · 미리 보기에 파일 목록이 없음 | 에이전트 파일은 맨 앞의 `"*": deny` 로 정해 둔 도구 (읽기 · `glob` · `grep` · `list` · 스킬 · `deck.md` 쓰기) 밖을 모두 막는다 (자료 속 지시가 다른 도구로 새지 않게 · docs/REDTEAM.md). 다른 도구가 막힌 것은 정상이다. 파일 목록을 못 보면 막힌 도구 이름만 보고하고 멈춘다 — 에이전트 파일은 고치지 않는다 **[미확인 — opencode 판마다 목록 도구 이름]** |
| 4단계 뒤 opencode 가 설정 오류를 냄 | 백업 (`.bak`) 으로 되돌리고 사용자에게 알린다. 되돌린 뒤에도 그림이 안 닿으면 '안 함' 으로 보고한다 |
| 4-2 에서 `True` | 키가 파일에 값으로 있다. 에이전트는 고치지 않고 사용자가 환경 변수로 옮기게 한다 |

## 업데이트

사용자가 업데이트를 요청했을 때.

1. **[질문]** "`D:\OPENCODE\subordinate-1` 에서 `git pull` 을 해도 될까요?" 동의하면:

```powershell
git -C "D:\OPENCODE\subordinate-1" pull --ff-only
```

- **확인**: 오류 없이 끝남. **실패하면**: 출력을 그대로 보여 주고 멈춘다. 저장소를 고치지 않았다면 `untracked` · `overwritten` 문구는 사용자가 만든 같은 이름 파일 때문일 수 있으니 **[질문]** 으로 처리 방법을 묻는다. zip 으로 받았다면 새 zip 을 풀어 달라고 부탁한다.

2. 3단계의 상태 명령으로 세 파일을 저장소 것과 견준다. `이미 설치됨` 이면 넘어간다.
3. `다름` 인 것만 차이를 보이고 **[질문]** 뒤, 백업하고 복사한다 (3단계와 같다).
4. 4단계의 modalities 는 이미 더했다면 다시 하지 않는다. 4-3 으로 `modalities=True` 만 확인한다.
5. opencode 를 다시 시작하라고 알리고, 5단계의 확인을 한다. 6단계 형식으로 보고한다.

## 제거

설치가 복사한 것만 지운다. 저장소 폴더는 지우지 않는다.

1. 세 파일마다 저장소 것과 견준다 (3단계의 상태 명령). `이미 설치됨` 이면 지운다. `다름` 이면 사용자가 고친 것일 수 있으니 차이를 보이고 **[질문]** "고친 흔적이 있습니다. 그래도 지울까요, 백업(`.bak`) 해 두고 지울까요, 남길까요?"
2. 지운다 (비어 있는 스킬 폴더도 함께):

```powershell
$cfg = "$env:USERPROFILE\.config\opencode"
Remove-Item "$cfg\skills\subordinate-1\SKILL.md"
if (-not (Get-ChildItem -Force "$cfg\skills\subordinate-1")) { Remove-Item "$cfg\skills\subordinate-1" } else { Get-ChildItem -Force "$cfg\skills\subordinate-1" | Select-Object Name }
Remove-Item "$cfg\agents\subordinate-1.md"
Remove-Item "$cfg\commands\subordinate.md"
```

`-Recurse` 는 쓰지 않는다. 스킬 폴더에 다른 파일 (예: 업데이트 때 만든 `.bak`) 이 남아 있으면 폴더는 지우지 않고 그 목록이 나온다 — 보여 준 뒤 **[질문]** 으로 묻는다. `OPENCODE_CONFIG_DIR` 에 설치했다면 `$cfg` 를 그 폴더로 바꾼다.

3. **[질문]** "사내 모델의 `modalities` 줄은 다른 일에도 쓰이므로 기본은 남겨 둡니다. 설치 전으로 되돌릴까요?" 되돌린다고 하면 `.bak` 과 견주어 그 한 줄만 뺀다 (편집 도구로 그 줄 하나만 지우고, 앞 줄의 쉼표를 맞춘다). 설정 파일을 `.bak` 으로 통째로 되돌리지 않는다 (그 사이에 사용자가 바꾼 다른 칸을 잃을 수 있다). 뺀 뒤 JSON 오류가 없는지 4-3 의 명령으로 본다.
4. **[질문]** "설치 때 만든 백업(`.bak`) 파일을 지울까요?" 목록을 보여 주고 답대로 한다.
5. **[질문]** "시험 폴더 `D:\OPENCODE\subordinate-1-try` 를 지울까요?" 지운다고 하면 `Remove-Item "D:\OPENCODE\subordinate-1-try" -Recurse` (이 폴더 하나만).
6. 저장소 `D:\OPENCODE\subordinate-1` 을 지울지는 사용자에게 맡긴다. 에이전트는 지우지 않는다.
7. opencode 를 다시 시작하라고 알린다.

**알아 둘 것 — 대화 기록.** 이 묶음은 인터뷰 답 원문을 파일로 남기지 않지만, opencode 는 세션 · 메시지를 자기 데이터 폴더 (`%USERPROFILE%\.local\share\opencode` 의 `opencode.db`) 에 남긴다 [문헌: opencode 문서 › troubleshooting › Storage]. 인터뷰에서 한 말도 거기 남는다. 이 제거는 그 데이터를 지우지 않는다. 지우려면 opencode 에서 그 세션을 지우거나 opencode 문서를 따른다 — 에이전트가 이 폴더를 지우지 않는다.

## 확인한 것

- **문서로 확인한 것** (opencode 문서): 전역 설정 폴더 `~/.config/opencode` 의 복수형 하위 폴더 · 스킬 자리 `skills/<name>/SKILL.md` · `name` 이 폴더 이름과 같아야 함 · `SKILL.md` 대문자 · `OPENCODE_CONFIG` · `OPENCODE_CONFIG_DIR` · `{env:…}` · 관리 설정 `%ProgramData%\opencode` · 설정 우선순위.
- **M0 에서 확인한 것**: `modalities` 를 넣어야 그림이 닿았다 (K2 결과 `G B O T 5`).
- **추정**: opencode 가 설정 · 스킬 · 명령을 시작할 때 읽는다 (다시 시작을 요청한 까닭). 단수형 폴더와 복수형 폴더가 겹칠 때 어느 쪽이 쓰이는지, `modalities` 가 판마다 같은지는 **[미확인]**.
- **[미확인 — Windows 에서 돌려 보지 못함]** 이 문서의 PowerShell · cmd 명령은 개발 쪽이 Windows 에서 돌려 보지 못했다. 문서와 문법 지식으로 썼다. 돌려 보고 다르면 그 출력을 보고하고 멈추라는 규칙 7 이 안전판이다.
