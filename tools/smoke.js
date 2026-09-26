// Smoke test: stub the DOM and canvas, then play the game from the plane to the finale.
// Run: node tools/smoke.js
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const any = () => new Proxy(function () {}, { get: (t, k) => k === Symbol.toPrimitive ? () => 0 : (t[k] ??= any()), set: (t, k, v) => (t[k] = v, true), apply: () => any() });
const ctx = new Proxy({}, { get: (t, k) => k === 'measureText' ? () => ({ width: 10 }) : (k in t ? t[k] : () => {}), set: (t, k, v) => (t[k] = v, true) });
const els = {};
Object.assign(global, {
  window: global, innerWidth: 1200, innerHeight: 700, devicePixelRatio: 1,
  document: { getElementById: id => els[id] ??= Object.assign(any(), { getContext: () => ctx, classList: { toggle() {} }, style: {}, offsetHeight: 68 }) },
  addEventListener() {}, location: { hash: '' }, history: { replaceState() {} }, performance: { now: () => 0 }, setTimeout: fn => fn(),
});
let raf; global.requestAnimationFrame = fn => (raf = fn);
eval(fs.readFileSync(path.join(root, 'data/posts.js'), 'utf8'));
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
eval(html.split('<script>')[1].split('</script>')[0] +
  ';globalThis.g = { get state() { return state }, P, M, keys, blocks, MAZE, start, jump, goToLevel, LEVELS, get found() { return found } };');

// shortest walk through the maze that visits every page, then the exit
const key = (c, r) => c + ',' + r;
function bfs(a, b) {
  const prev = new Map([[key(a.c, a.r), null]]), q = [a];
  while (q.length) {
    const p = q.shift(); if (p.c === b.c && p.r === b.r) break;
    for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const n = { c: p.c + dc, r: p.r + dr };
      if (n.c < 0 || n.c >= g.MAZE[0].length || g.MAZE[n.r][n.c] === '#' || prev.has(key(n.c, n.r))) continue;
      prev.set(key(n.c, n.r), p); q.push(n);
    }
  }
  const out = []; for (let p = b; p; p = prev.get(key(p.c, p.r))) out.unshift(p); return out;
}
let route = null, now = 0, frames = 0;
g.start();
while (g.state !== 'end' && frames++ < 60000) {
  if (g.state === 'maze') {
    if (!route) {
      route = []; let cur = { c: 0, r: 1 };
      for (const b of g.blocks.filter(b => b.maze).sort((x, y) => x.c - y.c)) { route.push(...bfs(cur, b).slice(1)); cur = b; }
      route.push(...bfs(cur, { c: 16, r: 9 }).slice(1), { c: 17, r: 9 });
    }
    if (route[0] && Math.abs(g.M.x - route[0].c) < 0.08 && Math.abs(g.M.y - route[0].r) < 0.08) route.shift();
    const t = route[0] || { c: 17, r: 9 };
    Object.assign(g.keys, { right: t.c > g.M.x + 0.04, left: t.c < g.M.x - 0.04, down: t.r > g.M.y + 0.04, up: t.r < g.M.y - 0.04 });
  } else {
    Object.assign(g.keys, { right: true, left: false, up: false, down: false });
    if (frames % 25 === 0) g.jump();
  }
  raf(now += 16);
}
for (let i = 0; i < 300; i++) raf(now += 16);   // let the finale run
const finished = g.state === 'end';
// jump to every level from the menu and make sure the game keeps running
Object.assign(g.keys, { right: false, left: false, up: false, down: false });
for (const lv of g.LEVELS) { g.goToLevel(lv.id); for (let i = 0; i < 30; i++) raf(now += 16); if (g.state !== 'play') { console.log('stuck after jumping to', lv.id, g.state); process.exit(1); } }
const by = k => g.blocks.filter(b => b[k] && b.hit).length;
console.log({ finished, found: g.found, plane: by('fly'), parade: by('marcher'), truck: by('car'), maze: by('maze'), frames });
if (!finished) process.exit(1);
