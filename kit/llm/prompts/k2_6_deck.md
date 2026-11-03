보고 장표의 중간 형식 deck-lite 를 JSON 파일 하나로 쓰십시오. 그림은 보지 않아도 됩니다.

읽을 파일 (읽기 도구로 여십시오. 이 두 파일 말고 다른 파일은 열지 마십시오):
- inputs/facts_lite.json · 사실 (f001 – f012) 과 그림 (img1 – img5) 목록
- inputs/interview_lite.json · 사용자 인터뷰 답 (a01 – a04)

쓸 파일: results/deck_1.json
파일에는 JSON 만 씁니다. 코드 울타리 (```) 나 설명 글을 넣지 않습니다.

형식 (아래에 없는 칸은 쓰지 않습니다. 값은 모양을 보이려는 자리표시이니 그대로 옮기지 마십시오):
{
  "format": 1,
  "meta": {"type": "anomaly", "audience": "...", "title": "...", "date": "YYYY-MM-DD", "host": "opencode", "data_class": "synthetic"},
  "slides": [
    {
      "id": "s1",
      "section": "요약",
      "title": {"text": "...", "kind": "사실", "refs": ["f0??"]},
      "bullets": [{"text": "...", "kind": "해석", "refs": ["f0??", "img?"], "reasoning": "..."}],
      "notes": ""
    }
  ],
  "open_items": [{"slot": "s?.title", "why": "..."}]
}

규칙:
1. meta.type 은 "anomaly" · "experiment" · "periodic" 중 하나입니다. date 는 YYYY-MM-DD 이고 data_class 는 늘 "synthetic" 입니다.
2. slides 는 4 – 8장입니다. section 은 "요약", "현상", "현상 범위", "분석", "의견", "한계 · 다음", "부록" 중 하나이고 이 순서를 지킵니다. "현상" 과 "한계 · 다음" 은 꼭 넣습니다.
3. 문장 (title 과 bullets 의 각 항목) 마다 kind 와 refs 를 답니다.
   - 사실: 사실 id (f…) 나 그림 id (img…) 를 하나 이상.
   - 해석: 사실 · 그림 id 를 둘 이상, 그리고 reasoning 에 추론 한 줄.
   - 의견: 인터뷰 답 id (a…) 를 하나 이상. 의견은 사용자 답에서만 나옵니다. 당신의 의견을 쓰지 않습니다.
   - 미확인: 필요한데 자료도 답도 없는 것. refs 는 [] 입니다.
4. refs 에는 두 파일에 있는 id 만 씁니다. id 를 지어내지 않습니다.
5. 제목 (title.text) 은 완결된 한 문장 주장입니다. 40자 안 · 숫자 하나 이상을 권합니다.
6. open_items 는 남은 질문 목록입니다. 없으면 [] 입니다.

다 쓰면 "썼음" 한 줄만 답하십시오.
