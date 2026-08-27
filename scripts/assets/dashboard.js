/* Hover layer for the board: crosshair + tooltip on the time panels,
   per-bar tooltip on the site chart, and the chart/table toggle. */
(function () {
  "use strict";
  var BOARD = window.__BOARD__ || { panels: [] };

  function fmt(v, digits, unit) {
    if (v === null || v === undefined || v === "") return "—";
    var n = Number(v);
    if (!isFinite(n)) return "—";
    return n.toLocaleString("en-IN", {
      minimumFractionDigits: digits, maximumFractionDigits: digits
    }) + (unit ? " " + unit : "");
  }

  function timePanel(panel) {
    var root = document.getElementById(panel.id);
    if (!root) return;
    var svg = root.querySelector("svg");
    var tip = root.querySelector(".tip");
    var hair = svg.querySelector(".crosshair");
    var dots = Array.prototype.slice.call(svg.querySelectorAll(".hover-dot"));
    var pts = panel.points;
    if (!pts.length) return;

    function hide() {
      tip.style.opacity = 0;
      hair.style.opacity = 0;
      dots.forEach(function (d) { d.style.opacity = 0; });
    }

    function show(evt) {
      var rect = svg.getBoundingClientRect();
      var scale = rect.width / panel.viewWidth;
      var mx = (evt.clientX - rect.left) / scale;
      var best = 0, bestD = Infinity;
      for (var i = 0; i < pts.length; i++) {
        var d = Math.abs(pts[i].x - mx);
        if (d < bestD) { bestD = d; best = i; }
      }
      var p = pts[best];
      hair.setAttribute("x1", p.x); hair.setAttribute("x2", p.x);
      hair.style.opacity = 1;

      var rows = "";
      panel.fields.forEach(function (f, idx) {
        var val = p[f.key];
        var dot = dots[idx];
        if (dot) {
          if (val === null || val === undefined) { dot.style.opacity = 0; }
          else {
            dot.setAttribute("cx", p.x);
            dot.setAttribute("cy", p[f.key + "_y"]);
            dot.style.opacity = 1;
          }
        }
        rows += '<div class="t-r"><i style="background:' + f.color + '"></i>' +
                f.label + ' <b>' + fmt(val, f.digits, f.unit) + '</b></div>';
      });
      tip.innerHTML = '<div class="t-d">' + p.label + "</div>" + rows;
      tip.style.opacity = 1;
      var left = Math.min(Math.max(p.x * scale, 78), rect.width - 78);
      tip.style.left = left + "px";
      // sit just above the hovered point, but never ride up over the panel heading
      var anchorY = p[panel.fields[0].key + "_y"];
      if (anchorY === null || anchorY === undefined) anchorY = panel.tipY;
      tip.style.top = (Math.max(anchorY, panel.tipY + 46) * scale) + "px";
    }

    svg.addEventListener("mousemove", show);
    svg.addEventListener("mouseleave", hide);
    svg.addEventListener("touchmove", function (e) {
      if (e.touches[0]) show(e.touches[0]);
    }, { passive: true });
    svg.addEventListener("touchend", hide);
  }

  function barPanel(panel) {
    var root = document.getElementById(panel.id);
    if (!root) return;
    var tip = root.querySelector(".tip");
    var bars = root.querySelectorAll("[data-tip]");
    Array.prototype.forEach.call(bars, function (bar) {
      bar.addEventListener("mouseenter", function () {
        tip.innerHTML = bar.getAttribute("data-tip");
        tip.style.opacity = 1;
        var r = bar.getBoundingClientRect();
        var pr = root.getBoundingClientRect();
        tip.style.left = (r.left - pr.left + r.width / 2) + "px";
        tip.style.top = (r.top - pr.top) + "px";
      });
      bar.addEventListener("mouseleave", function () { tip.style.opacity = 0; });
    });
  }

  BOARD.panels.forEach(function (p) {
    if (p.kind === "time") timePanel(p);
    else if (p.kind === "bars") barPanel(p);
  });

  Array.prototype.forEach.call(document.querySelectorAll("[data-tabs]"), function (group) {
    var tabs = group.querySelectorAll(".tab");
    Array.prototype.forEach.call(tabs, function (tab) {
      tab.addEventListener("click", function () {
        Array.prototype.forEach.call(tabs, function (t) {
          var on = t === tab;
          t.setAttribute("aria-selected", on ? "true" : "false");
          var target = document.getElementById(t.getAttribute("data-target"));
          if (target) target.classList.toggle("hidden", !on);
        });
      });
    });
  });
})();
