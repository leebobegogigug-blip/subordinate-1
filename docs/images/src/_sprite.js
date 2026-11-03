/* README 그림의 공용 그리기 조각 — 작은 차트 그림 (합성 · 값은 모두 지어낸 것).
   모두 정수 칸에 그린다 (DESIGN 원칙 6: 사각 격자). 색은 _base.css 의 변수에서 온다 (팔레트 안).
   쓰는 법: <span data-chart="box" data-w="128" data-h="64" data-pad="2"></span>
   box  PRD_B 두께 설비별 상자 그림 — EQ-03 만 높다 (docs/images/examples/k2_ctx_3.png 의 img3 를 줄여 그린 것) */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }

  function chart(kind, w, h, opt) {
    opt = opt || {};
    var s = el("svg", { "class": "chart", width: w, height: h, viewBox: "0 0 " + w + " " + h, "shape-rendering": "crispEdges" });
    var ink = "var(--ink-2)", dim = "var(--line-2)", acc = "var(--accent-ink)";
    function R(x, y, ww, hh, fill) { s.appendChild(el("rect", { x: x, y: y, width: ww, height: hh, fill: fill })); }
    var pad = opt.pad == null ? 4 : opt.pad;
    var iw = w - pad * 2, ih = h - pad * 2, x0 = pad, y0 = pad, i;
    if (kind === "box") {
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
