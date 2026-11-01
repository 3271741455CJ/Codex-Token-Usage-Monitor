'use strict';

// Exercises the actual embedded application script with synthetic data only.
// This deliberately tests DOM behavior, not browser layout or visual rendering.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const template = fs.readFileSync(path.join(__dirname, '..', 'codex_usage', 'dashboard.html'), 'utf8');
const script = [...template.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1];

class Element {
  constructor(tag = '#text', text = '') {
    this.tagName = tag.toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = {};
    this.dataset = {};
    this.style = {};
    this.listeners = {};
    this.hidden = false;
    this.disabled = false;
    this.open = false;
    this._text = text;
    this._value = undefined;
    this.className = '';
    this.classList = {
      contains: name => this.className.split(/\s+/).includes(name),
      toggle: (name, force) => {
        const names = new Set(this.className.split(/\s+/).filter(Boolean));
        const active = force === undefined ? !names.has(name) : force;
        if (active) names.add(name); else names.delete(name);
        this.className = [...names].join(' ');
        return active;
      },
    };
  }
  get children() { return this.childNodes.filter(node => node.tagName !== '#TEXT'); }
  get textContent() { return this._text + this.childNodes.map(node => node.textContent).join(''); }
  set textContent(value) {
    this.childNodes.forEach(node => { node.parentNode = null; });
    this.childNodes = [];
    this._text = String(value ?? '');
  }
  get options() { return this.children.filter(node => node.tagName === 'OPTION'); }
  get value() {
    if (this._value !== undefined) return this._value;
    if (this.tagName === 'SELECT') return this.options[0]?.value || '';
    if (this.tagName === 'OPTION') return this.attributes.value ?? this.textContent;
    return '';
  }
  set value(value) {
    const string = String(value);
    this._value = this.tagName === 'SELECT' && !this.options.some(option => option.value === string) ? '' : string;
  }
  setAttribute(name, value) {
    this.attributes[name] = String(value);
    if (name === 'class') this.className = String(value);
    if (name === 'id') this.id = String(value);
    if (name === 'hidden') this.hidden = true;
    if (name === 'value') this._value = String(value);
    if (name.startsWith('data-')) {
      this.dataset[name.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = String(value);
    }
  }
  getAttribute(name) { return this.attributes[name] ?? null; }
  removeAttribute(name) { delete this.attributes[name]; }
  append(...nodes) {
    for (let node of nodes) {
      if (!(node instanceof Element)) node = new Element('#text', String(node));
      node.remove();
      node.parentNode = this;
      this.childNodes.push(node);
    }
  }
  prepend(...nodes) {
    const tail = [...this.childNodes];
    this.replaceChildren(...nodes, ...tail);
  }
  replaceChildren(...nodes) {
    this.childNodes.forEach(node => { node.parentNode = null; });
    this.childNodes = [];
    this._text = '';
    this.append(...nodes);
  }
  remove() {
    if (!this.parentNode) return;
    this.parentNode.childNodes = this.parentNode.childNodes.filter(node => node !== this);
    this.parentNode = null;
  }
  addEventListener(name, callback) { (this.listeners[name] ||= []).push(callback); }
  dispatch(name) {
    if (name === 'click' && this.disabled) return;
    for (const callback of this.listeners[name] || []) callback({ target: this, type: name });
  }
  click() { this.dispatch('click'); }
  showModal() { this.open = true; }
  close() { this.open = false; }
  select() {}
}

function all(root, predicate = () => true) {
  const result = [];
  for (const child of root.childNodes) {
    if (predicate(child)) result.push(child);
    result.push(...all(child, predicate));
  }
  return result;
}
function simpleMatch(node, selector) {
  if (selector.startsWith('.')) return node.classList.contains(selector.slice(1));
  return node.tagName.toLowerCase() === selector.toLowerCase();
}
function select(root, selector) {
  const parts = selector.split(' ');
  return all(root, node => {
    if (!simpleMatch(node, parts[parts.length - 1])) return false;
    let ancestor = node.parentNode;
    for (let i = parts.length - 2; i >= 0; i--) {
      while (ancestor && !simpleMatch(ancestor, parts[i])) ancestor = ancestor.parentNode;
      if (!ancestor) return false;
      ancestor = ancestor.parentNode;
    }
    return true;
  });
}
function createDocument() {
  const root = new Element('document');
  const stack = [root];
  const markup = template.replace(/<(script|style)\b([^>]*)>[\s\S]*?<\/\1>/g, '<$1$2></$1>');
  const voids = new Set(['meta', 'input', 'br', 'link', 'hr', 'img']);
  for (const token of markup.match(/<[^>]+>|[^<]+/g)) {
    if (/^<!/.test(token)) continue;
    if (/^<\//.test(token)) { stack.pop(); continue; }
    if (token.startsWith('<')) {
      const [, tag, attributes] = token.match(/^<([\w-]+)([\s\S]*?)\/?\s*>$/);
      const node = new Element(tag);
      for (const match of attributes.matchAll(/([^\s=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+)))?/g)) {
        node.setAttribute(match[1], match[2] ?? match[3] ?? match[4] ?? '');
      }
      stack[stack.length - 1].append(node);
      if (!voids.has(tag)) stack.push(node);
    } else stack[stack.length - 1].append(new Element('#text', token));
  }
  const body = all(root, node => node.tagName === 'BODY')[0];
  return {
    root, body,
    createElement: tag => new Element(tag),
    createTextNode: text => new Element('#text', String(text)),
    getElementById: id => all(root, node => node.id === id)[0] || null,
    querySelectorAll: selector => select(root, selector),
    execCommand: () => true,
  };
}
function boot(report = {}) {
  const document = createDocument();
  document.getElementById('report-data').textContent = JSON.stringify({ generated_at: '2026-10-25T12:00:00Z', ...report });
  let download = null;
  const timers = new Map();
  let nextTimer = 0;
  const context = {
    document, Node: Element, Intl, Date, Blob, console,
    navigator: { clipboard: { writeText: async () => {} } },
    URL: { createObjectURL: blob => { download = blob; return 'blob:synthetic-download'; }, revokeObjectURL: () => {} },
    setTimeout: (callback, delay) => { const id = ++nextTimer; timers.set(id, { callback, delay }); return id; },
    clearTimeout: id => timers.delete(id),
  };
  vm.runInNewContext(script, context, { filename: 'dashboard-inline.js', timeout: 3000 });
  return {
    document,
    get: id => document.getElementById(id),
    text: id => document.getElementById(id).textContent,
    change: (id, value) => { const element = document.getElementById(id); element.value = value; element.dispatch('change'); },
    click: id => document.getElementById(id).click(),
    buttons: id => all(document.getElementById(id), node => node.tagName === 'BUTTON'),
    rows: id => select(document.getElementById(id), 'tbody tr'),
    metrics: () => select(document.getElementById('metric-cards'), '.metric-value').map(node => node.textContent),
    flush: delay => { for (const [id, timer] of [...timers]) if (timer.delay <= delay) { timers.delete(id); timer.callback(); } },
    download: () => download,
  };
}
const source = { path: 'C:\\Synthetic\\session.jsonl', line: 8, uri: 'file:///C:/Synthetic/session.jsonl' };
function turn(id, input = 100, output = 20, extra = {}) {
  return {
    id, session_id: 's-' + id, title: 'Synthetic ' + id, project_id: 'project-one', project_name: '示例项目', project: 'C:\\Synthetic\\worktree-one',
    started_at: '2026-10-20T12:00:00Z', ended_at: '2026-10-20T12:01:00Z', model: 'model-a', reasoning_effort: 'high',
    input_tokens: input, cached_input_tokens: 10, cache_write_input_tokens: 5, output_tokens: output, reasoning_output_tokens: 7,
    total_tokens: input + output, usage_record_count: 1, request_count: 1, accounting_method: 'response_usage', attribution: 'matched',
    source, usage_sources: [{ ...source, line: 19 }], ...extra,
  };
}
function reportFor(rows, extra = {}) {
  const sessions = [...new Map(rows.map(row => [row.session_id, { ...row, id: row.session_id, created_at: row.started_at, updated_at: row.ended_at, turn_count: 1 }])).values()];
  return { turns: rows, sessions, sources: [source], ...extra };
}

test('empty data loads every section and reports missing usage rather than confirmed zero', () => {
  const app = boot();
  assert.deepEqual(app.metrics().slice(0, 3), ['未记录', '未记录', '未记录']);
  assert.match(app.text('history-table'), /没有符合/);
  assert.match(app.text('limits'), /没有可用/);
  assert.equal(app.get('page-prev').disabled, true);
  assert.equal(app.get('page-next').disabled, true);
  for (const nav of app.document.querySelectorAll('.nav button')) nav.click();
  assert.equal(app.get('filters-panel').hidden, true);
  app.click('refresh-help');
  assert.equal(app.get('detail-dialog').open, true);
  assert.match(app.text('dialog-content'), /双击项目目录/);
  app.click('close-dialog');
  assert.equal(app.get('detail-dialog').open, false);
});

test('model segments are summed once and filters select matching segment usage', () => {
  const mixed = turn('mixed', 300, 30, { model: 'mixed', model_segments: [
    { model: 'model-a', reasoning_effort: 'high', input_tokens: 100, output_tokens: 10, total_tokens: 110, cached_input_tokens: 50, reasoning_output_tokens: 5 },
    { model: 'model-b', reasoning_effort: 'medium', input_tokens: 200, output_tokens: 20, total_tokens: 220, cached_input_tokens: 150, reasoning_output_tokens: 10 },
  ] });
  const app = boot(reportFor([mixed, turn('simple', 50, 5)]));
  assert.equal(app.metrics()[0], '385');
  assert.equal(app.rows('model-detail-table').length, 2);
  app.change('model-filter', 'model-b');
  assert.deepEqual(app.metrics().slice(0, 3), ['220', '200', '20']);
  assert.equal(app.rows('model-detail-table').length, 1);
  app.change('reasoning-filter', 'high');
  assert.equal(app.metrics()[0], '未记录');
  app.click('reset-filters');
  assert.equal(app.metrics()[0], '385');
});

test('creator filtering is distinct from billing and unknown creator records remain visible', () => {
  const app = boot(reportFor([turn('current'), turn('other', 200, 20, { attribution: 'other' }), turn('unknown', 300, 20, { attribution: 'unknown' })]));
  assert.equal(app.metrics()[0], '660');
  app.change('attribution-filter', 'unknown');
  assert.equal(app.metrics()[0], '320');
  assert.match(app.text('history-table'), /创建者未知/);
  app.change('attribution-filter', 'matched');
  assert.equal(app.metrics()[0], '120');
  assert.match(app.text('history-table'), /当前账号创建/);
});

test('one project ID groups different worktrees and project selection includes both', () => {
  const app = boot(reportFor([turn('one'), turn('two', 200, 20, { project: 'C:\\Synthetic\\worktree-two' }), turn('three', 40, 4, { project_id: 'project-two', project_name: '第二项目' })]));
  assert.equal(app.rows('projects-table').length, 2);
  assert.equal(app.get('project-filter').options.length, 3);
  assert.match(app.rows('projects-table')[0].textContent, /worktree-one.*worktree-two/);
  app.buttons('projects-table')[0].click();
  assert.equal(app.metrics()[0], '340');
  assert.match(app.text('filter-count'), /2 轮/);
  assert.equal(app.get('section-history').classList.contains('active'), true);
});

test('history sorting, pagination, date filtering and search operate on synthetic rows', () => {
  const rows = Array.from({ length: 31 }, (_, i) => turn('t' + String(i).padStart(2, '0'), (i + 1) * 10, 0, { started_at: `2026-10-${String(i + 1).padStart(2, '0')}T10:00:00Z`, ended_at: `2026-10-${String(i + 1).padStart(2, '0')}T10:01:00Z` }));
  const app = boot(reportFor(rows));
  app.click('mode-turns');
  app.change('history-sort', 'tokens_desc');
  assert.match(app.rows('history-table')[0].textContent, /Synthetic t30/);
  assert.equal(app.rows('history-table').length, 25);
  app.click('page-next');
  assert.equal(app.rows('history-table').length, 6);
  assert.equal(app.text('page-info'), '2 / 2');
  app.click('page-prev');
  app.change('history-sort', 'tokens_asc');
  assert.match(app.rows('history-table')[0].textContent, /Synthetic t00/);
  app.change('date-from', '2026-10-30');
  assert.equal(app.rows('history-table').length, 2);
  app.click('reset-filters');
  app.get('search').value = 't05';
  app.get('search').dispatch('input');
  app.flush(180);
  assert.equal(app.rows('history-table').length, 1);
  assert.match(app.rows('history-table')[0].textContent, /Synthetic t05/);
});

test('session drilldown and individual turn show actual usage provenance and child totals', () => {
  const row = turn('root', 100, 20, { inclusive_tokens: { input_tokens: 200, output_tokens: 40, total_tokens: 240 }, child_turn_count: 1, root_session_id: 's-root', root_turn_id: 'root', usage_sources: Array.from({ length: 25 }, (_, i) => ({ ...source, line: 100 + i })) });
  const app = boot(reportFor([row]));
  app.buttons('history-table')[0].click();
  assert.match(app.text('dialog-title'), /Synthetic root/);
  const focus = app.buttons('dialog-content').find(button => button.textContent === '在历史明细中筛选此会话');
  focus.click();
  assert.equal(app.get('detail-dialog').open, false);
  assert.equal(app.get('session-focus').hidden, false);
  app.buttons('history-table')[0].click();
  assert.equal(app.text('dialog-title'), '单轮记录');
  assert.match(app.text('dialog-content'), /240 Tokens/);
  assert.match(app.text('dialog-content'), /响应请求数1/);
  assert.match(app.text('dialog-content'), /缓存写入（输入子项）5/);
  assert.match(app.text('dialog-content'), /第 119 行/);
  assert.doesNotMatch(app.text('dialog-content'), /第 124 行/);
  app.buttons('dialog-content').find(button => button.textContent === '加载更多用量来源').click();
  assert.match(app.text('dialog-content'), /第 124 行/);
  assert.equal(app.metrics()[0], '120');
  app.click('clear-session');
  assert.equal(app.get('session-focus').hidden, true);
});

test('missing usage remains unknown in cards, tables, session and single-turn dialogs', () => {
  const app = boot(reportFor([turn('missing', 0, 0, { usage_record_count: 0, request_count: 0, accounting_method: null, usage_sources: [] })]));
  assert.equal(app.metrics()[0], '未记录');
  assert.match(app.text('history-table'), /未记录/);
  app.buttons('history-table')[0].click();
  assert.match(app.text('dialog-content'), /输入 Token未记录/);
  app.click('close-dialog');
  app.click('mode-turns');
  app.buttons('history-table')[0].click();
  assert.match(app.text('dialog-content'), /响应请求数未确定/);
  assert.match(app.text('dialog-content'), /总 Token未记录/);
  assert.match(app.text('dialog-content'), /没有可核验的 Token 事件来源/);
});

test('limit history retains snapshots, past resets and credit flags', () => {
  const rate_limits = [1, 2].map(index => ({ limit_id: 'pool-one', timestamp: `2026-01-0${index}T00:00:00Z`, attribution: 'matched', primary: { used_percent: index * 10, window_minutes: 300, resets_at: 1735689600 }, credits: { has_credits: false, balance: '3.50', unlimited: false }, spend_control_reached: false, source }));
  const app = boot({ rate_limits });
  assert.match(app.text('limits'), /80.0% 剩余/);
  assert.doesNotMatch(app.text('limits'), /90.0% 剩余/);
  assert.match(app.text('limits'), /已超过记录的重置时间/);
  assert.match(app.text('limits'), /credits 可用声明：否/);
  assert.match(app.text('limits'), /是否触达支出限制：否/);
  app.click('limits-history');
  assert.match(app.text('dialog-content'), /10.0% 已用/);
  assert.match(app.text('dialog-content'), /20.0% 已用/);
});

test('database-only indexed counts are visible but never added to totals', () => {
  const app = boot(reportFor([turn('one')], { database_only_sessions: [
    { id: 'db-1', title: '索引记录一', tokens_used: 999999, project_name: '仅索引项目', source: { ...source, path: 'C:\\Synthetic\\state.sqlite', table: 'threads', key: 'db-1' } },
    { id: 'db-2', title: '索引记录二', tokens_used: null },
  ] }));
  assert.equal(app.metrics()[0], '120');
  assert.match(app.text('database-only-table'), /999,999/);
  assert.match(app.text('database-only-table'), /未知/);
  app.buttons('database-only-table')[0].click();
  assert.match(app.text('dialog-content'), /数据表：threads/);
  assert.match(app.text('dialog-content'), /索引键：db-1/);
});

test('CSV export preserves selection and neutralizes formulas after whitespace or newline', async () => {
  const dangerous = ['=SUM(1,1)', ' +cmd', '\n@bad', '-1+1', '\tfoo', '"quoted", value'];
  const app = boot(reportFor(dangerous.map((title, index) => turn('csv' + index, 10, 2, { title }))));
  app.click('export-csv');
  const csv = await app.download().text();
  for (const title of dangerous.slice(0, 5)) assert.ok(csv.includes('"\'' + title.replace(/"/g, '""') + '"'));
  assert.ok(csv.includes('"""quoted"", value"'));
  app.get('search').value = 'csv0';
  app.get('search').dispatch('input');
  app.flush(180);
  app.click('export-csv');
  const filtered = await app.download().text();
  assert.equal(filtered.split('\r\n').length, 2);
  assert.match(filtered, /csv0/);
  assert.doesNotMatch(filtered, /csv1/);
});

test('untrusted titles are text, secret fields remain masked and external source links are rejected', () => {
  const injection = '<img src="https://invalid.example/x" onerror="bad()">';
  const app = boot(reportFor([turn('injection', 1, 1, { title: injection, source: { path: 'synthetic', uri: 'https://invalid.example/' } })], { account: { email: 'synthetic@example.invalid', access_token: 'DO-NOT-SHOW', api_key_masked: '••••1234' } }));
  assert.ok(app.text('history-table').includes(injection));
  assert.equal(select(app.get('history-table'), 'img').length, 0);
  assert.doesNotMatch(app.text('account-details'), /DO-NOT-SHOW/);
  app.click('mode-turns');
  app.buttons('history-table').find(button => button.textContent === '查看来源').click();
  assert.equal(select(app.get('dialog-content'), 'a').length, 0);
});

test('source pagination and filter expansion are usable without network or persistence APIs', () => {
  const app = boot({ sources: Array.from({ length: 34 }, (_, i) => ({ path: 'C:\\Synthetic\\' + i, kind: 'synthetic' })) });
  assert.equal(select(app.get('source-list'), '.source-row').length, 30);
  app.click('show-more-sources');
  assert.equal(select(app.get('source-list'), '.source-row').length, 34);
  assert.equal(app.get('show-more-sources').hidden, true);
  app.click('more-filters');
  assert.equal(app.get('more-filter-fields').hidden, false);
  app.click('more-filters');
  assert.equal(app.get('more-filter-fields').hidden, true);
  assert.doesNotMatch(script, /\b(fetch|XMLHttpRequest|WebSocket|EventSource|localStorage|sessionStorage|indexedDB)\s*[.(]/);
});

test('model cache details and new metadata labels preserve their offline meaning', () => {
  const app = boot({
    configuration: { provider_kind: '自定义代理', authentication_note: '仅为合成说明', openai_base_url_env: 'https://synthetic.invalid/api' },
    coverage: { database_only_unknown_tokens: 2 },
    model_catalog: [{ slug: 'model-test', display_name: '示例模型', default_reasoning_level: 'high', supported_reasoning_levels: [{ effort: 'high', description: '合成能力说明' }], context_window: 200000, max_context_window: null, supported_in_api: true, visibility: 'list' }],
  });
  assert.match(app.text('configuration-details'), /认证与计费身份说明/);
  assert.match(app.text('configuration-details'), /生效情况未验证/);
  assert.match(app.text('coverage-details'), /索引计数未知的会话数2/);
  app.buttons('model-catalog-table')[0].click();
  assert.match(app.text('dialog-content'), /合成能力说明/);
  assert.match(app.text('dialog-content'), /可见性声明list/);
  assert.equal(app.text('dialog-title'), '本地模型缓存详情');
});

test('network-style file source paths cannot become clickable links', () => {
  for (const uri of ['file://server/share', 'file:////server/share', 'file:///\\server/share', 'file:///%5c%5cserver/share']) {
    const app = boot(reportFor([turn('bad-uri', 1, 1, { source: { path: 'synthetic', uri } })]));
    app.click('mode-turns');
    app.buttons('history-table').find(button => button.textContent === '查看来源').click();
    assert.equal(select(app.get('dialog-content'), 'a').length, 0, uri);
  }
});

test('official account totals stay independent of local filters and missing metrics remain unknown', () => {
  const official_usage={status:'partial',usage_status:'ok',limits_status:'unsupported',usage_fetched_at:'2026-10-20T00:00:00Z',summary:{lifetimeTokens:900,peakDailyTokens:null},daily:[{date:'2026-10-20',tokens:90},{date:'2026-10-21',tokens:null}]};
  const app=boot(reportFor([turn('local')],{official_usage}));
  assert.equal(app.metrics()[0],'120');
  assert.match(app.text('official-metrics'),/900/);
  assert.match(app.text('official-metrics'),/未提供/);
  assert.match(app.text('official-message'),/不支持该接口/);
  assert.match(app.text('official-daily'),/2026-10-21未提供/);
  app.change('attribution-filter','other');
  assert.equal(app.metrics()[0],'未记录');
  assert.match(app.text('official-metrics'),/900/);
});

test('official quota snapshots distinguish expired windows, unknown usage and actual zero credits', () => {
  const app=boot({official_usage:{status:'ok',rate_limits:[{label:'Codex 共享额度',primary:{usedPercent:20,windowDurationMins:300,resetsAt:1},secondary:{usedPercent:null,windowDurationMins:10080,resetsAt:null},credits:{balance:0}}]}});
  assert.match(app.text('official-limits'),/80.0% 剩余（采样时）/);
  assert.match(app.text('official-limits'),/每周 · 未提供/);
  assert.match(app.text('official-limits'),/当前剩余量未知/);
  assert.match(app.text('official-limits'),/Credits 余额：0/);
  assert.match(boot().text('official-status'),/默认离线/);
  assert.match(boot().text('official-metrics'),/未提供/);
});


test('serialized privacy output keeps drilldowns and CSV useful without private originals', async () => {
  const { spawnSync } = require('node:child_process');
  const raw = reportFor([turn('PRIVATE-TURN', 100, 20, {
    title: 'PRIVATE-TITLE', project: 'C:/PRIVATE-PATH', project_id: 'PRIVATE-PROJECT',
    project_name: 'PRIVATE-PROJECT-NAME', session_id: 'PRIVATE-SESSION',
    source: {path:'C:/PRIVATE-SOURCE.jsonl',line:8,uri:'file:///C:/PRIVATE-SOURCE.jsonl'},
    usage_sources: [{path:'C:/PRIVATE-SOURCE.jsonl',line:19}],
  })], {account:{email:'PRIVATE-EMAIL@example.invalid',api_key_masked:'PRIVATE-KEY'}});
  const result = spawnSync('python', ['-B', '-c', 'import json,sys; from codex_usage.privacy import protect_report; print(json.dumps(protect_report(json.load(sys.stdin))))'], {
    cwd: path.join(__dirname, '..'), input: JSON.stringify(raw), encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  assert.doesNotMatch(result.stdout, /PRIVATE/);
  const safe = JSON.parse(result.stdout);
  const app = boot(safe);
  assert.equal(app.metrics()[0], '120');
  assert.match(app.text('account-name'), /本地查看/);
  assert.match(app.text('account-details'), /auth.json/);
  app.buttons('projects-table')[0].click();
  assert.equal(app.metrics()[0], '120');
  app.click('mode-turns');
  app.buttons('history-table').find(button => button.textContent === '查看来源').click();
  assert.match(app.text('dialog-content'), /source-.*第 8 行/);
  assert.match(app.text('dialog-content'), /sessions/);
  assert.equal(select(app.get('dialog-content'), 'a').length, 0);
  assert.equal(app.buttons('dialog-content').length, 0);
  app.buttons('source-list')[0].click();
  assert.match(app.text('dialog-content'), /自行/);
  app.click('export-csv');
  const csv = await app.download().text();
  assert.doesNotMatch(csv, /PRIVATE|C:|file:/);
  assert.match(csv, /来源编号/);
  assert.ok(csv.includes(safe.turns[0].id));
  assert.ok(csv.includes(safe.turns[0].source.path));
  assert.match(csv, /100.*20.*120/);
});


test('format selector offers all requested reports and guides old snapshots', () => {
  const app=boot();
  assert.equal(app.get('export-format').options.length,8);
  app.change('export-format','report.docx'); app.click('export-csv');
  assert.match(app.text('dialog-content'),/启动交互报告/);
});

test('live refresh waits for generation, reloads on success and permits retry after failure', async () => {
  const live=fs.readFileSync(path.join(__dirname,'..','codex_usage','live.js'),'utf8');
  for (const ok of [true,false]) {
    let callback,reloads=0,request;
    const button={addEventListener:(name,fn)=>{callback=fn;}};
    const old={cloneNode:()=>button,replaceWith:()=>{}};
    vm.runInNewContext(live,{document:{getElementById:()=>old},location:{reload:()=>reloads++},
      fetch:async(url,options)=>{request={url,options};return{ok};}});
    await callback();
    assert.equal(request.url,'refresh'); assert.equal(request.options.method,'POST');
    assert.equal(request.options.headers['X-Codex-Refresh'],'1');
    assert.equal(reloads,ok?1:0);
    if(!ok){assert.equal(button.disabled,false);assert.match(button.textContent,/重试/);}
  }
});
