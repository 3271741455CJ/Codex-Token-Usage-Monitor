"""Anonymous evidence reports: no verdict certifies model identity."""
from fractions import Fraction
import math

from .storage import safe_snapshot


def wilson(successes,total):
    if not total: return None
    z=1.959963984540054; p=successes/total; d=1+z*z/total
    center=(p+z*z/(2*total))/d
    radius=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return [max(0,center-radius),min(1,center+radius)]


def upgrade(record):
    value=safe_snapshot(record)
    legacy=value.get('schema_version',1)<2 or value.get('evidence_level')=='legacy_unverified'
    value.update(schema_version=2,validation_state='experimental')
    value['evidence_level']='legacy_unverified' if legacy else (
        'matched_official_comparison' if value.get('provenance_level')=='same_time_official_reference' else
        'historical_reference' if value.get('baseline_id') else 'basic_observation')
    completed=value.get('capability_completed')
    correct=value.get('capability_correct',0)
    scored = value.get('capability_valid') if value.get('mode') == 'assessment' else completed
    accuracy=correct/scored if scored else None
    response_count=value.get('response_count',0)
    counts = value.get('assessment_counts')
    attempted = sum(row['attempted'] for row in counts) if counts else value.get('sample_count', response_count + value.get('network_failures', 0))
    stability=value.get('dimensions',{}).get('stability',{'status':'not_comparable'})
    value['dimensions']={
        'quality':{'accuracy':accuracy,'interval':wilson(correct,scored) if scored else None,
                   'valid_responses':value.get('capability_valid'),'sample_count':scored},
        'behavior':{'identity_state':value.get('identity_state','no_reference'),
                    'p_value':value.get('p_value'),'baseline_id':value.get('baseline_id')},
        'reliability':{'response_count':response_count,'sample_count':attempted,
                       'network_failures':value.get('network_failures',0),'invalid_responses':value.get('invalid_responses',0),
                       'latency_mean':value.get('latency_mean'),'latency_p95':value.get('latency_p95')},
        'stability':stability if not legacy else {'status':'not_comparable'}}
    value['recommendation']='review_reference' if value.get('detected_anomaly') else 'collect_more_evidence'
    return safe_snapshot(value)


ISSUES = {
    'output_limit': '输出达到上限', 'stream_interrupted': '响应中途断开',
    'empty_answer': '没有最终答案', 'response_filtered': '输出被过滤',
    'incomplete_output': '回答未完整结束', 'answer_format': '回答格式不符',
    'authentication_failed': 'Key 未通过认证', 'network_error': '网络连接失败',
    'unsupported_parameters': '接口不接受当前参数', 'rate_limited': '供应商限流',
    'reference_model_unavailable': '官方 API 不提供此型号或当前 Key 无权限',
    'reference_model_retired': '官方原版本已停用，旧型号 ID 已指向其他版本',
    'invalid_response': '接口返回格式无法解析', 'redirect_blocked': '请求发生跳转',
    'http_error': '供应商请求失败', 'remote_error': '供应商返回错误',
}
TASK_LABELS = {
    'constraints': '多步推理', 'code': '代码追踪', 'repair': '代码纠错',
    'structured': '结构化输出', 'tool_args': '工具参数', 'document': '文档规则',
}


def explain(record):
    """Derive ordinary-language copy exclusively from anonymous aggregate fields."""
    record = safe_snapshot(record)
    n = record.get('capability_valid') or 0
    correct = record.get('capability_correct') or 0
    pair = record.get('paired_result') or {}
    paired_n = pair.get('valid_pairs') or 0
    headline = '证据不足，暂无法判断是否降配'
    comparison = '没有匹配的同型号官方参考。'
    if record.get('source_kind') == 'official_api':
        headline = '官方直连能力报告'
        comparison = '这轮测的是官方 API 本身。'
    elif record.get('reference_state') == 'reference_mismatch':
        comparison = '已配置参考，但型号或请求设置不一致。本轮只测中转能力。'
    elif record.get('reference_state') in ('reference_key_required', 'reference_unavailable'):
        reason = ISSUES.get(record.get('reference_error'), '官方参考当前不可用')
        comparison = f'{reason}。本轮只测中转能力。'
    elif record.get('reference_state') in ('reference_matched', 'reference_pending') or (record.get('reference_preset') and pair):
        comparison = '已选中官方参考。本轮尚未取得可评分的同题对照。'
        if paired_n and pair.get('reference_correct') is not None and pair.get('target_correct') is not None:
            delta = 100 * pair['accuracy_loss']
            comparison = (f'官方 {pair["reference_correct"]}/{paired_n}，中转 {pair["target_correct"]}/{paired_n}。'
                          + (f'本轮中转低 {delta:g} 个百分点。' if delta > 0 else
                             f'本轮中转高 {-delta:g} 个百分点。' if delta < 0 else '本轮两边答对数相同。'))
            if pair['status'] == 'degraded':
                headline = '本轮表现明显低于官方，建议复测'
            elif (pair['status'] == 'no_detected_degradation' and
                  wilson(pair['regressions'], paired_n)[1] <= .10):
                headline = '本轮未发现明显能力差距'
        if pair:
            comparison += f'共有 {paired_n}/{pair["attempted_pairs"]} 对题可以比较。'
        if record.get('model') and record.get('reference_model'):
            comparison += f'请求型号为中转 {record["model"]}、官方 {record["reference_model"]}。'
        if record.get('reference_error'):
            comparison += f'官方对照中止：{ISSUES.get(record["reference_error"], "请求未完成")}。'
    elif pair:
        comparison = '这是旧版对照记录。匹配条件和统计结果可在专业详情中查看。'
    capability = f'本轮答对 {correct}/{n} 道可评分题。' if n else '本轮没有可评分的能力题。'
    counts = record.get('assessment_counts') or []
    for side in counts:
        attempted, valid, correct = side['attempted'], side['valid'], side['correct']
        label = '官方参考' if side['source_kind'] == 'reference' else '本轮'
        coverage = f'{label}已尝试 {attempted}/{side["sample_count"]} 题，答对 {correct}，答错 {valid - correct}，无法评分 {attempted - valid}。'
        if side['source_kind'] and side['source_kind'] == record.get('source_kind'):
            capability = coverage
        elif side['source_kind'] == 'reference' and (attempted != valid or attempted != side['sample_count']):
            comparison += coverage
    if not counts and 0 < n < 10:
        capability += '样本较少，只能说明这几道题的表现。'
    identity = '本轮暂无可用的型号对照结论。'
    if record.get('identity_state') == 'identity_uncalibrated':
        identity = '已采集短行为样本，型号判断仍待校准。'
    elif record.get('identity_state') == 'invalid_probe':
        identity = '未取得可用的行为样本。'
        if not record.get('response_issues'):
            identity += '旧记录未保留具体原因。'
    source_labels = {'reference': '官方参考', 'relay': '检测目标', 'official_api': '检测目标'}
    diagnostics = [
        f'{source_labels.get(row.get("source_kind"), "来源未记录")} {ISSUES.get(row["error_code"], "请求未完成")} {row["sample_count"]} 次'
        for row in record.get('response_issues', [])
    ]
    if not diagnostics and record.get('error_code'):
        diagnostics = [ISSUES.get(record['error_code'], '请求未完成')]
    elif not diagnostics and record.get('reference_error'):
        diagnostics = [f'官方参考 {ISSUES.get(record["reference_error"], "请求未完成")}']
    if record.get('status') == 'budget_exhausted':
        headline = '预算不足，检测未完成'
    elif record.get('status') == 'cancelled':
        headline = '检测已取消'
    elif record.get('status') != 'ok':
        headline = '检测未完成'
    return {'headline': headline, 'capability': capability, 'comparison': comparison,
            'identity': identity, 'diagnostics': diagnostics}


def trend(records):
    dated=sorted((r for r in records if r.get('target_id')),key=lambda r:r.get('evaluated_at',''))
    if not dated: return {'status':'insufficient_data','sample_count':0}
    latest=dated[-1]
    if (latest.get('status')!='ok' or not latest.get('capability_completed') or
        latest.get('capability_valid')!=latest.get('capability_completed') or latest.get('network_failures') or latest.get('invalid_responses')):
        return {'status':'not_comparable','sample_count':len(dated)}
    rows=[r for r in records if r.get('status')=='ok' and r.get('target_id') and r.get('capability_completed')
          and r.get('capability_valid')==r.get('capability_completed') and not r.get('network_failures') and not r.get('invalid_responses')]
    rows.sort(key=lambda r:r.get('evaluated_at',''))
    if len(rows)<2: return {'status':'insufficient_data','sample_count':len(rows)}
    newest=rows[-1]
    binding=('target_id','model','protocol_id','suite_version','mode','reference_model','reference_preset',
             'reference_protocol_id','sample_count')
    previous=[r for r in rows[:-1] if all(r.get(k)==newest.get(k) for k in binding)]
    if not previous: return {'status':'not_comparable','sample_count':len(rows)}
    if newest.get('suite_version') == 'assessment-v2':
        unique = {row['task_seed']: row for row in [*previous, newest] if type(row.get('task_seed')) is int}
        if len(unique) < 4:
            return {'status': 'insufficient_data', 'sample_count': len(unique)}
        window = sorted(unique.values(), key=lambda row: row['evaluated_at'])[-4:]
        scores = [Fraction(row.get('capability_correct', 0), row['capability_completed']) for row in window]
        earlier, recent = scores[:2], scores[2:]
        decline = min(earlier) - max(recent) >= Fraction(1, 10)
        return {'status': 'historical_decline_signal' if decline else 'no_detected_deviation',
                'accuracy_change': float((sum(recent) - sum(earlier)) / 2), 'sample_count': 4,
                'provenance_level': 'user_history'}
    before=previous[-1]
    difference=newest.get('capability_correct',0)/newest['capability_completed']-before.get('capability_correct',0)/before['capability_completed']
    return {'status':'historical_decline_signal' if difference<=-0.1 else 'no_detected_deviation',
            'accuracy_change':difference,'sample_count':len(previous)+1,'provenance_level':'user_history'}


def comparisons(records):
    groups={}
    for row in records:
        if row.get('target_id') and row.get('mode') in ('quality','quality_audit','context','assessment'):
            groups.setdefault(row['target_id'],[]).append(row)
    result=[]
    for target_id,rows in groups.items():
        latest=max(rows,key=lambda r:r.get('evaluated_at',''))
        result.append({'target_id':target_id,'source_alias':latest.get('source_alias'),'model':latest.get('model'),
                       'suite_version':latest.get('suite_version'),'protocol_id':latest.get('protocol_id'),
                       'mode':latest.get('mode'),'last_result':upgrade(latest),'trend':trend(rows)})
    return safe_snapshot(result)
