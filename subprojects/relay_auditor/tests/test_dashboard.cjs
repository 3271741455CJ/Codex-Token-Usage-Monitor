const assert = require('node:assert/strict');
const test = require('node:test');
const ui = require('../relay_auditor/web/app.js');

test('unknown usage never renders as zero', () => {
  assert.equal(ui.formatCount(null), '未知');
  assert.equal(ui.formatCount(0), '0');
});
test('screening consistency never becomes certified model identity', () => {
  assert.equal(ui.identityLabel('baseline_missing'), '缺少匹配基线');
  assert.equal(ui.identityLabel('screening_consistent'), '筛查未见偏离（实验性）');
  assert.equal(ui.identityLabel('no_detected_deviation'), '本次未检出行为差异');
});
test('user interval preserves seconds and rejects invalid values', () => {
  assert.equal(ui.intervalSeconds('2.5', 'minutes'), 150);
  assert.equal(ui.intervalSeconds('30', 'seconds'), 30);
  assert.throws(() => ui.intervalSeconds('0', 'minutes'));
  assert.throws(() => ui.intervalSeconds('NaN', 'minutes'));
});
test('formal identity audit counts both channels', () => {
  assert.equal(ui.estimateRequests('identity_audit', 50), 500);
  assert.equal(ui.estimateRequests('capability_audit', 40), 80);
  assert.equal(ui.estimateRequests('baseline', 12), 12);
});
test('quality and reasoning estimates include all reference calls',()=>{
  assert.equal(ui.estimateRequests('quality_audit',40),80);
  assert.equal(ui.estimateRequests('reasoning',5),10);
  assert.equal(ui.estimateRequests('reasoning',5,true),20);
  assert.equal(ui.estimateRequests('screen',100),3);
  assert.equal(ui.qualityText({accuracy:null}),'未测 / 无有效证据');
});
test('custom names and UI-only model mappings never enter browser exports', () => {
  const result = ui.exportSnapshot({schema_version:1,history:[],display_names:{'relay-1':'PRIVATE-NAME'},
    model_choices:{'relay-1':['gpt-test']},catalog_models:{},catalog_reasoning:{},desktop:true,
    official_presets:[{id:'openai',label:'OpenAI'}]});
  assert.deepEqual(result,{schema_version:1,history:[]});
});
test('official reference summary shows the selected provider and exact model mapping', () => {
  const presets = [{id:'openai',label:'OpenAI'}];
  const target = {model:'gpt5.6sol',reference_preset:'openai',reference_model:'gpt-5.6-sol'};
  assert.equal(ui.referenceSummary({...target,assessment_plan:{reference_state:'reference_matched'}},presets),
    '已匹配 OpenAI · 中转 gpt5.6sol ↔ 官方 gpt-5.6-sol');
  assert.match(ui.referenceSummary({...target,assessment_plan:{reference_state:'reference_pending'}},presets),/Key 待首次检测验证/);
  assert.match(ui.referenceSummary({...target,assessment_plan:{reference_state:'reference_mismatch'}},presets),/本轮只测能力/);
  assert.match(ui.referenceSummary({...target,reference_preset:null,assessment_plan:{reference_state:'reference_matched'}},presets),/旧版同型号官方参考/);
});
test('new targets do not inherit labels from history or jobs for a different target ID', () => {
  const data = {targets:[{source_alias:'relay-1',target_id:'target-new'}],display_names:{'relay-1':'新检测目标'}};
  assert.equal(ui.targetLabel(data,{source_alias:'relay-1',target_id:'target-new'}),'新检测目标');
  assert.equal(ui.targetLabel(data,{source_alias:'relay-1',target_id:'target-old'}),'relay-1（已删除）');
  assert.equal(ui.targetLabel(data,{source_alias:'relay-1'}),'relay-1');
  assert.equal(ui.targetLabel(data,{source_alias:'relay-1',source_kind:'official_api'}),'官方直连');
});

test('follow-up reports show the original screen and new paired scores for the same target', () => {
  const screen = {job_id:'screen-1', target_id:'target-1', paired_result:{valid_pairs:10,target_correct:6,reference_correct:10}};
  const review = {review_of:'screen-1', target_id:'target-1', paired_result:{valid_pairs:40,target_correct:31,reference_correct:37}};
  assert.equal(ui.pairedReviewSummary(review, [screen]), '初筛 10 对，中转 6/10、官方 10/10。新题复核 40 对，中转 31/40、官方 37/40。');
  assert.equal(ui.pairedReviewSummary({...review,paired_result:{valid_pairs:0}}, [screen]),
    '初筛 10 对，中转 6/10、官方 10/10。新题复核暂未获得可比较的答题结果。');
  assert.equal(ui.pairedReviewSummary(review, [{...screen,target_id:'other'}]), '新题复核 40 对，中转 31/40、官方 37/40。');
  assert.equal(ui.pairedReviewSummary(screen, []), '');
});

test('target selection survives a reorder and falls back when the selected target is removed', () => {
  const first = {target_id:'first'};
  const second = {target_id:'second'};
  assert.equal(ui.selectedTarget([first, second], 'second'), second);
  assert.equal(ui.selectedTarget([second, first], 'first'), first);
  assert.equal(ui.selectedTarget([first], 'second'), first);
  assert.equal(ui.selectedTarget([], 'second'), null);
});

test('paired summary shows the observed quick-screen difference with a sample caveat', () => {
  const result = {mode:'assessment', status:'ok', paired_result:{attempted_pairs:10,valid_pairs:10,target_correct:7,reference_correct:9}};
  assert.deepEqual(ui.pairedReport(result), {
    headline:'初筛低于官方 20 个百分点', gap:'20 个百分点', caveat:'样本较少，建议复核', samples:'10 道可比较题', relay:'7/10', official:'9/10'
  });
  const missing = {...result,paired_result:{...result.paired_result,valid_pairs:9}};
  assert.match(ui.pairedReport(missing).caveat, /部分题目/);
  assert.equal(ui.pairedReport({...result,paired_result:{valid_pairs:10,target_correct:7}}), null);
  assert.equal(ui.pairedReport({...result,status:'cancelled'}), null);
  assert.equal(ui.pairedReport(null), null);
});
