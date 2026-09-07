/* Per-site performance ratio: overlay up to three sites on one chart, and fall
   back to one small panel per site beyond that.

   Three is not arbitrary. It is the number of hues from this palette that stay
   apart in every possible pairing, in light and dark, for normal and
   colour-deficient vision. A fourth would look fine to some readers and be
   unreadable to others, so past three the chart facets instead. */
(function () {
  "use strict";
  var DATA = window.__SITEPR__;
  if (!DATA || !DATA.sites || !DATA.sites.length) return;

  var root = document.getElementById("siteplot");
  var picker = document.querySelector("#line-chart .picker");
  if (!root || !picker) return;

  var MAX_OVERLAY = 3;
  var W = 960, ML = 44, MR = 92, MT = 12, MB = 24;
  var tip = root.querySelector(".tip");
  var boxes = [].slice.call(picker.querySelectorAll("input[type=checkbox]"));
  var slots = [null, null, null];   // slot -> site index, held until unticked

  function selected() {
    return boxes.filter(function (b) { return b.checked; })
                .map(function (b) { return +b.getAttribute("data-site"); });
  }

  function slotOf(idx) {
    var at = slots.indexOf(idx);
    return at === -1 ? null : at + 1;
  }

  /* A site keeps its colour for as long as it is on screen: unticking a
     different site must never repaint the ones that remain. */
  function reassign() {
    var sel = selected();
    slots = slots.map(function (i) { return sel.indexOf(i) === -1 ? null : i; });
    if (sel.length <= MAX_OVERLAY) {
      sel.forEach(function (i) {
        if (slots.indexOf(i) === -1) {
          var free = slots.indexOf(null);
          if (free !== -1) slots[free] = i;
        }
      });
    } else {
      slots = [null, null, null];
    }
  }

  function niceTicks(max) {
    if (!(max > 0)) return { top: 1, step: 0.25, count: 4 };
    var best = null;
    [4, 5, 6].forEach(function (count) {
      var raw = max / count, exp = Math.floor(Math.log10(raw)), base = Math.pow(10, exp);
      [1, 2, 2.5, 5, 10].some(function (m) {
        var step = m * base;
        if (step * count >= max - 1e-9) {
          if (!best || step * count < best.top) best = { top: step * count, step: step, count: count };
          return true;
        }
        return false;
      });
    });
    return best;
  }

  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function pathFor(values, x, y) {
    // break the line across days with no report rather than bridging them
    var segs = [], cur = [];
    values.forEach(function (v, i) {
      if (v === null || v === undefined) { if (cur.length) segs.push(cur); cur = []; }
      else cur.push([x(i), y(v)]);
    });
    if (cur.length) segs.push(cur);
    return segs;
  }

  function drawChart(indices, opt) {
    // A small panel needs its own viewBox: squeezing the 960-wide one into a
    // 320px card shrinks the axis text to a few pixels.
    var w = opt.width || W, height = opt.height;
    var ml = opt.ml || ML, mr = opt.mr || MR, mb = opt.mb || MB;
    var innerW = w - ml - mr, innerH = height - MT - mb;
    var n = DATA.days.length;
    var max = opt.sharedMax || 0;
    if (!opt.sharedMax) {
      indices.forEach(function (i) {
        DATA.sites[i].values.forEach(function (v) { if (v !== null && v > max) max = v; });
      });
    }
    var t = niceTicks(max || 1);
    var showLabels = opt.showLabels;
    var x = function (i) { return ml + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW); };
    var y = function (v) { return MT + innerH - (v / t.top) * innerH; };
    var out = ['<svg viewBox="0 0 ' + w + " " + height + '" role="img" aria-label="' +
               esc(indices.map(function (i) { return DATA.sites[i].name; }).join(", ")) +
               ' performance ratio">'];

    for (var k = 0; k <= t.count; k++) {
      var gv = t.step * k, gy = y(gv);
      out.push('<line class="grid" x1="' + ml + '" y1="' + gy.toFixed(1) +
               '" x2="' + (ml + innerW) + '" y2="' + gy.toFixed(1) + '"/>');
      out.push('<text class="axis" x="' + (ml - 6) + '" y="' + (gy + 3.5).toFixed(1) +
               '" text-anchor="end">' + (t.step >= 1 ? gv.toFixed(0) : gv.toFixed(1)) + "</text>");
    }

    var tickStep = Math.max(1, Math.round(n / (opt.xticks || 6))), lastI = n - 1, ticks = [];
    for (var i2 = 0; i2 < n; i2 += tickStep) {
      if (lastI - i2 >= tickStep * 0.6) ticks.push(i2);
    }
    ticks.push(lastI);
    ticks.forEach(function (i) {
      out.push('<text class="axis" x="' + x(i).toFixed(1) + '" y="' + (MT + innerH + 14) +
               '" text-anchor="' + (i === lastI ? "end" : (i === 0 ? "start" : "middle")) +
               '">' + esc(DATA.labels[i]) + "</text>");
    });

    var ends = [];
    indices.forEach(function (idx) {
      var site = DATA.sites[idx];
      var slot = slotOf(idx);
      var colour = slot ? "var(--series-" + slot + ")" : "var(--gen)";
      pathFor(site.values, x, y).forEach(function (seg) {
        if (seg.length > 1) {
          out.push('<path d="M' + seg.map(function (p) {
            return p[0].toFixed(1) + "," + p[1].toFixed(1);
          }).join(" L") + '" fill="none" stroke="' + colour +
            '" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>');
        } else if (seg.length === 1) {
          out.push('<circle cx="' + seg[0][0].toFixed(1) + '" cy="' + seg[0][1].toFixed(1) +
                   '" r="3.5" fill="' + colour + '"/>');
        }
      });
      var lastIdx = -1;
      site.values.forEach(function (v, i) { if (v !== null) lastIdx = i; });
      if (lastIdx >= 0) {
        var lx = x(lastIdx), ly = y(site.values[lastIdx]);
        out.push('<circle cx="' + lx.toFixed(1) + '" cy="' + ly.toFixed(1) +
                 '" r="4.5" fill="' + colour + '" stroke="var(--panel)" stroke-width="2"/>');
        if (showLabels) {
          ends.push({ x: lx, y: ly, trueY: ly, text: site.values[lastIdx].toFixed(1) + " %" });
        }
      }
    });

    // Converging lines would print their end labels on top of each other, so
    // push them apart and run a thin leader back to the dot they belong to.
    ends.sort(function (a, b) { return a.y - b.y; });
    for (var e = 1; e < ends.length; e++) {
      var gap = ends[e].y - ends[e - 1].y;
      if (gap < 14) ends[e].y += 14 - gap;
    }
    ends.forEach(function (p) {
      if (Math.abs(p.y - p.trueY) > 1.5) {
        out.push('<line x1="' + (p.x + 5).toFixed(1) + '" y1="' + p.trueY.toFixed(1) +
                 '" x2="' + (p.x + 9).toFixed(1) + '" y2="' + p.y.toFixed(1) +
                 '" stroke="var(--rule-strong)" stroke-width="1"/>');
      }
      out.push('<text class="dlabel" x="' + (p.x + 11).toFixed(1) + '" y="' +
               (p.y + 3.5).toFixed(1) + '">' + p.text + "</text>");
    });

    if (showLabels) {
      out.push('<line class="crosshair" x1="0" y1="' + MT + '" x2="0" y2="' + (MT + innerH) + '"/>');
      indices.forEach(function (idx) {
        var slot = slotOf(idx);
        out.push('<circle class="hover-dot" cx="0" cy="0" r="4.5" fill="' +
                 (slot ? "var(--series-" + slot + ")" : "var(--gen)") +
                 '" stroke="var(--panel)" stroke-width="2" style="opacity:0"/>');
      });
    }
    out.push("</svg>");
    return { svg: out.join(""), x: x, y: y, top: t.top };
  }

  function hover(indices, geom) {
    var svg = root.querySelector("svg");
    if (!svg) return;
    var hair = svg.querySelector(".crosshair");
    var dots = [].slice.call(svg.querySelectorAll(".hover-dot"));
    if (!hair) return;

    function hide() {
      tip.style.opacity = 0; hair.style.opacity = 0;
      dots.forEach(function (d) { d.style.opacity = 0; });
    }
    function show(evt) {
      var r = svg.getBoundingClientRect(), scale = r.width / W;
      var mx = (evt.clientX - r.left) / scale;
      var n = DATA.days.length, best = 0, bd = Infinity;
      for (var i = 0; i < n; i++) {
        var d = Math.abs(geom.x(i) - mx);
        if (d < bd) { bd = d; best = i; }
      }
      hair.setAttribute("x1", geom.x(best)); hair.setAttribute("x2", geom.x(best));
      hair.style.opacity = 1;
      var rows = "", anchorY = null;
      indices.forEach(function (idx, k) {
        var site = DATA.sites[idx], v = site.values[best], slot = slotOf(idx);
        var colour = slot ? "var(--series-" + slot + ")" : "var(--gen)";
        var dot = dots[k];
        if (dot) {
          if (v === null) dot.style.opacity = 0;
          else {
            dot.setAttribute("cx", geom.x(best)); dot.setAttribute("cy", geom.y(v));
            dot.style.opacity = 1;
            if (anchorY === null || geom.y(v) < anchorY) anchorY = geom.y(v);
          }
        }
        rows += '<div class="t-r"><i style="background:' + colour + '"></i>' +
                esc(site.name) + " <b>" +
                (v === null ? "no report" : v.toFixed(1) + " %") + "</b></div>";
      });
      tip.innerHTML = '<div class="t-d">' + esc(DATA.full[best]) + "</div>" + rows;
      tip.style.opacity = 1;
      tip.style.left = Math.min(Math.max(geom.x(best) * scale, 90), r.width - 90) + "px";
      tip.style.top = (Math.max(anchorY === null ? MT : anchorY, MT + 46) * scale) + "px";
    }
    svg.addEventListener("mousemove", show);
    svg.addEventListener("mouseleave", hide);
    svg.addEventListener("touchmove", function (e) {
      if (e.touches[0]) show(e.touches[0]);
    }, { passive: true });
    svg.addEventListener("touchend", hide);
  }

  function render() {
    reassign();
    var sel = selected();

    boxes.forEach(function (b) {
      var idx = +b.getAttribute("data-site");
      var slot = slotOf(idx);
      var sw = b.parentNode.querySelector(".sw");
      sw.setAttribute("data-slot", slot || "");
      sw.style.background = b.checked
        ? (slot ? "var(--series-" + slot + ")" : "var(--gen)")
        : "transparent";
      b.parentNode.classList.toggle("on", b.checked);
    });

    var count = document.getElementById("pick-count");
    if (count) {
      count.textContent = sel.length === 0 ? "nothing selected"
        : sel.length + (sel.length === 1 ? " site" : " sites")
          + (sel.length > MAX_OVERLAY ? " · shown as separate panels" : "");
    }

    if (!sel.length) {
      root.innerHTML = '<div class="empty">Tick a site above to plot it.</div>' +
                       '<div class="tip"></div>';
      tip = root.querySelector(".tip");
      return;
    }

    if (sel.length <= MAX_OVERLAY) {
      var legend = '<div class="legend">' + sel.map(function (idx) {
        var slot = slotOf(idx);
        return '<span><i style="background:' +
          (slot ? "var(--series-" + slot + ")" : "var(--gen)") + '"></i>' +
          esc(DATA.sites[idx].name) +
          (DATA.sites[idx].frozen ? " (fixed value)" : "") + "</span>";
      }).join("") + "</div>";
      var g = drawChart(sel, { height: 260, showLabels: true });
      root.innerHTML = legend + g.svg + '<div class="tip"></div>';
      tip = root.querySelector(".tip");
      hover(sel, g);
    } else {
      // one panel per site, all on the same scale so heights are comparable
      var sharedMax = 0;
      sel.forEach(function (i) {
        DATA.sites[i].values.forEach(function (v) {
          if (v !== null && v > sharedMax) sharedMax = v;
        });
      });
      var panels = sel.map(function (idx) {
        var g = drawChart([idx], { width: 430, height: 150, ml: 30, mr: 14, mb: 20,
                                   xticks: 4, sharedMax: sharedMax, showLabels: false });
        var site = DATA.sites[idx];
        var vals = site.values.filter(function (v) { return v !== null; });
        var mean = vals.length ? vals.reduce(function (a, b) { return a + b; }, 0) / vals.length : null;
        return '<div class="mini"><div class="mini-h"><b>' + esc(site.name) + "</b>" +
               (site.frozen ? ' <span class="flag">fixed value</span>' : "") +
               "<span>" + (mean === null ? "—" : "mean " + mean.toFixed(1) + " %") +
               "</span></div>" + g.svg + "</div>";
      }).join("");
      root.innerHTML = '<div class="minis">' + panels + '</div><div class="tip"></div>';
      tip = root.querySelector(".tip");
    }
  }

  boxes.forEach(function (b) { b.addEventListener("change", render); });

  function pick(indices) {
    boxes.forEach(function (b) {
      b.checked = indices.indexOf(+b.getAttribute("data-site")) !== -1;
    });
    slots = [null, null, null];
    render();
  }
  var ids = DATA.sites.map(function (_, i) { return i; });
  var byName = document.getElementById("pick-best");
  if (byName) byName.addEventListener("click", function () { pick(ids.slice(0, 3)); });
  var worst = document.getElementById("pick-worst");
  if (worst) worst.addEventListener("click", function () { pick(ids.slice(-3)); });
  var none = document.getElementById("pick-none");
  if (none) none.addEventListener("click", function () { pick([]); });

  render();
})();
