/* README 그림의 공용 그리기 조각 — 막내 (픽셀 캐릭터) · 7세그 · 작은 차트 그림.
   모두 정수 칸에 그린다 (DESIGN 원칙 6: 사각 격자). 색은 _base.css 의 클래스에서 온다 (팔레트 안).
   쓰는 법: <span data-mak="idle" data-scale="3"></span> · <span data-seg="09" data-u="3"></span>
           <span data-chart="trend" data-w="64" data-h="40"></span> */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  // ── 막내: 16 × 16 칸. 글자 하나 = 한 칸 ('.' 은 비움). 글자의 색은 _base.css 의 .mak 클래스.
  //   W 흰 선 (머리 테두리 · 눈 · 입 · 와이셔츠 · 손) · N 얼굴 화면 · J 저고리 · T 넥타이
  //   G 결재판 · P 종이 · Q 글줄 · K 클립 · L 켜진 불 · l 꺼진 불
  //   얼굴은 works 캐릭터들처럼 '화면' 이다 (네이비 바탕에 흰 눈). 몸에 넥타이와 결재판이 붙어 막내가 된다.
  var UP = [                             // r0–r2 — 머리 위쪽 (모든 서 있는 자세가 같다)
    "......WW........",
    "...WWWWWWWWWW...",
    "...WNNNNNNNNW..."
  ];
  var FACE = {                           // r3–r8 — 눈 · 입
    idle: ["...WNWWNNWWNW...", "...WNWWNNWWNW...", "...WNNNNNNNNW...", "...WNNNWWNNNW...", "...WNNNNNNNNW...", "...WNNNNNNNNW..."],
    ask:  ["...WNWWNNWWNW...", "...WNWWNNWWNW...", "...WNNNNNNNNW...", "...WNNNWWNNNW...", "...WNNNWWNNNW...", "...WNNNNNNNNW..."],
    work: ["...WNNNNNNNNW...", "...WNWWNNWWNW...", "...WNWWNNWWNW...", "...WNNNNNNNNW...", "...WNNNWWNNNW...", "...WNNNNNNNNW..."],
    err:  ["...WNWNNNNWNW...", "...WNNWNNWNNW...", "...WNWNNNNWNW...", "...WNNNNNNNNW...", "...WNNWWWWNNW...", "...WNNNNNNNNW..."]
  };
  var CHIN = "...WWWWWWWWWW...";          // r9 — 턱
  function body(led) {                   // r10–r15 — 결재판을 오른쪽에 든 몸
    return [
      "..JJJJWTTWJK" + led + "K..",
      "..JJJJWTTWGGGGG.",
      "..JJJJJTTJGPPPG.",
      "..JJJJJTTWGQQQG.",
      "..JJJJJTTWGPPPG.",
      "..JJJJJTTJGGGGG."
    ];
  }
  function stand(face, led) {
    return UP.concat(FACE[face]).concat([CHIN]).concat(body(led));
  }
  function stamp(rows, pts, ch) {        // [x, y] 칸에 ch 를 덮어쓴다
    var out = rows.map(function (r) { return r.split(""); });
    pts.forEach(function (p) { out[p[1]][p[0]] = ch; });
    return out.map(function (r) { return r.join(""); });
  }
  var BANG = [[13, 0], [13, 1], [13, 2], [13, 3], [13, 5], [15, 0], [15, 1], [15, 2], [15, 3], [15, 5]];   // ‼
  var TICK = [[11, 3], [12, 4], [13, 3], [14, 2], [15, 1]];                                                // √
  var DOTS = [[11, 0], [13, 0], [15, 0]];                                                                  // …

  var FRAMES = {
    // 대기 — 결재판을 내리고 기다린다 · 불 꺼짐
    idle: stand("idle", "l"),
    // 질문 — 손을 들고 ‼ · 불 켜짐 (사용자 응답 대기)
    ask: (function () {
      var r = stand("ask", "L");
      r = stamp(r, [[0, 5], [1, 5], [0, 6], [1, 6]], "W");                       // 든 손
      r = stamp(r, [[0, 7], [1, 7], [0, 8], [1, 8], [0, 9], [1, 9], [0, 10], [1, 10]], "J");   // 팔
      return stamp(r, BANG, "L");
    })(),
    // 작성 · 검사 — 결재판을 들여다본다 · 점 셋 · 불 켜짐
    work: stamp(stand("work", "L"), DOTS, "L"),
    // 막힘 — 눈을 꼭 감고 (> <) 입을 다문다 · 불 꺼짐 (ERR 칩은 HTML 이 옆에 붙인다)
    err: stand("err", "l"),
    // 완료 — 고개를 숙여 인사 · √ · 불 켜짐
    done: stamp([
      "................", "................", "................", "................", "................", "................",
      "......WW........",
      "...WWWWWWWWWW...",
      "...WNNNNNNNNW...",
      "...WNWWNNWWNW...",
      "...WNNNNNNNNW...",
      "...WWWWWWWWWW...",
      "..JJJJJTTJJJJJ..",
      "..JJJJJTTJGGGGG.",
      "..JJJJJTTJGPPPG.",
      "..JJJJJTTJGGGGG."
    ], TICK, "L")
  };

  function check(name, rows) {
    if (rows.length !== 16) throw new Error("막내 " + name + ": 줄 수 " + rows.length);
    rows.forEach(function (r, i) {
      if (r.length !== 16) throw new Error("막내 " + name + " r" + i + ": 칸 수 " + r.length + " · " + r);
    });
  }
  Object.keys(FRAMES).forEach(function (k) { check(k, FRAMES[k]); });

  function el(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }

  function mak(state, scale) {
    var rows = FRAMES[state];
    var s = el("svg", { "class": "mak", width: 16 * scale, height: 16 * scale, viewBox: "0 0 16 16" });
    rows.forEach(function (row, y) {
      var x = 0;
      while (x < 16) {
        var c = row[x];
        if (c === ".") { x++; continue; }
        var x2 = x;
        while (x2 < 16 && row[x2] === c) x2++;
        s.appendChild(el("rect", { "class": c, x: x, y: y, width: x2 - x, height: 1 }));
        x = x2;
      }
    });
    return s;
  }

  // ── 7세그: 숫자 한 칸 = 5 × 9 단위, 획 사이는 한 칸씩 띄운다. 꺼진 획도 흐리게 보인다 (켜진 것 = .on · 꺼진 것 = .off)
  var SEG = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg",
    "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg"
  };
  var PART = {   // 획 → [x, y, 가로, 세로] (단위)
    a: [1, 0, 3, 1], b: [4, 1, 1, 3], c: [4, 5, 1, 3], d: [1, 8, 3, 1],
    e: [0, 5, 1, 3], f: [0, 1, 1, 3], g: [1, 4, 3, 1]
  };
  function seg(text, u) {
    var n = text.length, gap = 2;
    var w = 0, i, ch;
    for (i = 0; i < n; i++) w += (text[i] === ":" ? 1 : 5) + (i < n - 1 ? gap : 0);
    var s = el("svg", { "class": "seg", width: w * u, height: 9 * u, viewBox: "0 0 " + w + " 9" });
    var x = 0;
    for (i = 0; i < n; i++) {
      ch = text[i];
      if (ch === ":") {
        s.appendChild(el("rect", { "class": "on", x: x, y: 2, width: 1, height: 1 }));
        s.appendChild(el("rect", { "class": "on", x: x, y: 6, width: 1, height: 1 }));
        x += 1 + gap;
        continue;
      }
      var lit = SEG[ch] || "";
      Object.keys(PART).forEach(function (k) {
        var p = PART[k];
        s.appendChild(el("rect", { "class": lit.indexOf(k) >= 0 ? "on" : "off", x: x + p[0], y: p[1], width: p[2], height: p[3] }));
      });
      x += 5 + gap;
    }
    return s;
  }

  // ── 작은 차트 그림 (합성 · 값은 모두 지어낸 것). 선 = 1 단위 · 색은 CSS 변수.
  //   trend  선 추세 (PRD_B 두께 lot 추세 · 9/16 부터 한 칸 올라감) · flat  같은 기간 PRD_A (변화 없음)
  //   box    설비별 상자 그림 (EQ-03 만 높다) · wafer 웨이퍼 맵 (오른쪽 위 가장자리에 불량) · pareto 불량 유형 파레토
  function chart(kind, w, h, opt) {
    opt = opt || {};
    var s = el("svg", { "class": "chart", width: w, height: h, viewBox: "0 0 " + w + " " + h, "shape-rendering": "crispEdges" });
    var ink = "var(--ink-2)", dim = "var(--line-2)", acc = "var(--accent-ink)", nav = "var(--prime-2)";
    function R(x, y, ww, hh, fill) { s.appendChild(el("rect", { x: x, y: y, width: ww, height: hh, fill: fill })); }
    function line(pts, stroke, sw) {
      s.appendChild(el("polyline", { points: pts.join(" "), fill: "none", stroke: stroke, "stroke-width": sw || 1, "stroke-linejoin": "miter" }));
    }
    var pad = opt.pad == null ? 4 : opt.pad;
    var iw = w - pad * 2, ih = h - pad * 2, x0 = pad, y0 = pad, i;
    if (kind === "trend" || kind === "flat") {
      R(x0, y0 + ih - 1, iw, 1, dim);                                    // 가로 축
      var n = 30, pts = [], step = Math.round(iw / (n - 1));
      for (i = 0; i < n; i++) {
        var wob = [0, 1, 0, -1, 1, 0, -1, 0, 1, -1][i % 10];
        var lvl = kind === "trend" && i >= 15 ? 0.34 : 0.62;               // 9/16 (= 15번째 칸) 부터 올라간다
        var y = y0 + Math.round(ih * (1 - lvl)) + wob * (opt.noise || 1);
        pts.push((x0 + i * step) + "," + y);
      }
      if (kind === "trend") {
        var usl = y0 + Math.round(ih * 0.18);
        s.appendChild(el("line", { x1: x0, x2: x0 + iw, y1: usl + 0.5, y2: usl + 0.5, stroke: ink, "stroke-width": 1, "stroke-dasharray": "4 3" }));
        var cx = x0 + 15 * step;
        s.appendChild(el("line", { x1: cx + 0.5, x2: cx + 0.5, y1: y0, y2: y0 + ih, stroke: acc, "stroke-width": 1 }));
      }
      line(pts, "var(--ink)", 1);
    } else if (kind === "box") {
      R(x0, y0 + ih - 1, iw, 1, dim);
      var cols = 4, cw = Math.floor(iw / cols);
      for (i = 0; i < cols; i++) {
        var hi = i === 2;                                                  // 세 번째 = EQ-03
        var top = y0 + Math.round(ih * (hi ? 0.18 : 0.42)), hgt = Math.round(ih * 0.3);
        var bx = x0 + i * cw + Math.round(cw * 0.22), bw = Math.round(cw * 0.56);
        s.appendChild(el("rect", { x: bx + 0.5, y: top + 0.5, width: bw, height: hgt, fill: "none", stroke: hi ? acc : ink, "stroke-width": 1 }));
        R(bx, top + Math.round(hgt * 0.45), bw + 1, 1, hi ? acc : ink);     // 중앙값
        R(bx + Math.round(bw / 2), top - 3, 1, 3, hi ? acc : ink);
        R(bx + Math.round(bw / 2), top + hgt + 1, 1, 3, hi ? acc : ink);
      }
    } else if (kind === "wafer") {
      var r = Math.floor(Math.min(iw, ih) / 2), cx2 = x0 + iw / 2, cy2 = y0 + ih / 2;
      s.appendChild(el("circle", { cx: cx2, cy: cy2, r: r - 0.5, fill: "none", stroke: ink, "stroke-width": 1, "shape-rendering": "geometricPrecision" }));
      var seed = 7, dots = [], gx, gy;
      for (gy = -r + 3; gy < r - 2; gy += 4) {
        for (gx = -r + 3; gx < r - 2; gx += 4) {
          if (gx * gx + gy * gy > (r - 3) * (r - 3)) continue;
          var edge = gx > r * 0.25 && gy < -r * 0.15 && (gx * gx + gy * gy) > (r * 0.55) * (r * 0.55);   // 오른쪽 위 가장자리
          seed = (seed * 31 + 11) % 97;
          if (edge && seed % 3 !== 0) dots.push([gx, gy, 1]);
          else if (seed % 29 === 0) dots.push([gx, gy, 0]);
        }
      }
      dots.forEach(function (d) { R(Math.round(cx2 + d[0]), Math.round(cy2 + d[1]), 2, 2, d[2] ? acc : dim); });
    } else if (kind === "pareto") {
      R(x0, y0 + ih - 1, iw, 1, dim);
      var hs = [0.9, 0.5, 0.34, 0.2, 0.14, 0.1], bw2 = Math.floor(iw / hs.length) - 2, pts2 = [], acum = 0, tot = hs.reduce(function (a, b) { return a + b; }, 0);
      hs.forEach(function (v, k) {
        var bh = Math.round((ih - 2) * v);
        R(x0 + k * (bw2 + 2), y0 + ih - 1 - bh, bw2, bh, k === 0 ? acc : nav);
        acum += v / tot;
        pts2.push((x0 + k * (bw2 + 2) + Math.round(bw2 / 2)) + "," + (y0 + Math.round((ih - 2) * (1 - acum))));
      });
      line(pts2, "var(--ink-2)", 1);
    }
    return s;
  }

  window.addEventListener("DOMContentLoaded", function () {
    [].forEach.call(document.querySelectorAll("[data-mak]"), function (n) {
      n.appendChild(mak(n.getAttribute("data-mak"), +(n.getAttribute("data-scale") || 3)));
    });
    [].forEach.call(document.querySelectorAll("[data-seg]"), function (n) {
      n.appendChild(seg(n.getAttribute("data-seg"), +(n.getAttribute("data-u") || 3)));
    });
    [].forEach.call(document.querySelectorAll("[data-chart]"), function (n) {
      n.appendChild(chart(n.getAttribute("data-chart"), +n.getAttribute("data-w"), +n.getAttribute("data-h"),
        { pad: n.hasAttribute("data-pad") ? +n.getAttribute("data-pad") : undefined }));
    });
  });
})();
