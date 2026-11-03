/* README 그림의 공용 그리기 조각 — 작은 차트 그림 (합성 · 값은 모두 지어낸 것).
   모두 정수 칸에 그린다 (DESIGN 원칙 6: 사각 격자). 색은 _base.css 의 변수에서 온다 (팔레트 안).
   쓰는 법: <span data-chart="trend" data-w="302" data-h="68" data-pad="2"></span>
   trend  PRD_B 두께 lot 추세 — 9/16 부터 한 칸 올라가고 2 lot 이 USL 을 넘는다 (grammar.html 의 그림 img2 와 같은 값)
   box    PRD_B 두께 설비별 상자 그림 — EQ-03 만 높다 (img3) */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }

  // 30 lot (2026-09-01 – 09-30) · 앞 15 lot 은 평균 100.3 nm, 뒤 15 lot 은 101.4 nm (+1.2 nm 안팎), 103 넘는 lot 둘
  var PRD_B = [100.1, 100.5, 100.2, 99.9, 100.4, 100.6, 100.0, 100.3, 100.5, 100.1, 99.8, 100.4, 100.7, 100.2, 100.3,
               101.2, 100.9, 101.6, 101.1, 103.2, 101.3, 100.8, 101.2, 101.5, 101.0, 103.1, 101.1, 101.4, 100.9, 101.2];

  function chart(kind, w, h, opt) {
    opt = opt || {};
    var s = el("svg", { "class": "chart", width: w, height: h, viewBox: "0 0 " + w + " " + h, "shape-rendering": "crispEdges" });
    var ink = "var(--ink-2)", dim = "var(--line-2)", acc = "var(--accent-ink)";
    function R(x, y, ww, hh, fill) { s.appendChild(el("rect", { x: x, y: y, width: ww, height: hh, fill: fill })); }
    var pad = opt.pad == null ? 4 : opt.pad;
    var iw = w - pad * 2, ih = h - pad * 2, x0 = pad, y0 = pad, i;
    if (kind === "trend") {
      var n = PRD_B.length, step = Math.floor(iw / (n - 1));
      var ox = x0 + Math.floor((iw - step * (n - 1)) / 2);
      var X = function (k) { return ox + k * step; };
      var Y = function (nm) { return y0 + Math.round((104 - nm) / 5 * (ih - 1)); };          // 99.0–104.0 nm
      R(x0, y0 + ih - 1, iw, 1, dim);                                                          // 가로 축
      s.appendChild(el("line", { x1: x0, x2: x0 + iw, y1: Y(103) + 0.5, y2: Y(103) + 0.5, stroke: ink, "stroke-width": 1, "stroke-dasharray": "4 3" }));   // USL 103.0
      R(X(15) - Math.floor(step / 2), y0, 1, ih, acc);                                         // 9/16 — 첫 변화 lot 바로 앞
      s.appendChild(el("polyline", {
        points: PRD_B.map(function (nm, k) { return (X(k) + 0.5) + "," + (Y(nm) + 0.5); }).join(" "),
        fill: "none", stroke: ink, "stroke-width": 1, "stroke-linejoin": "miter"
      }));
      PRD_B.forEach(function (nm, k) {
        if (nm > 103) s.appendChild(el("rect", { x: X(k) - 2, y: Y(nm) - 2, width: 5, height: 5, fill: "var(--panel)", stroke: "var(--ink)", "stroke-width": 1 }));
        else R(X(k) - 1, Y(nm) - 1, 3, 3, "var(--ink)");
      });
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
    }
    return s;
  }

  window.addEventListener("DOMContentLoaded", function () {
    [].forEach.call(document.querySelectorAll("[data-chart]"), function (n) {
      n.appendChild(chart(n.getAttribute("data-chart"), +n.getAttribute("data-w"), +n.getAttribute("data-h"),
        { pad: n.hasAttribute("data-pad") ? +n.getAttribute("data-pad") : undefined }));
    });
  });
})();
