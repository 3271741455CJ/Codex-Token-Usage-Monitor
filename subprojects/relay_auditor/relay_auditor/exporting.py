"""Offline, anonymous, human-readable HTML report. No scripts or remote assets."""
from html import escape
from .storage import safe_snapshot
from .reports import upgrade,comparisons,explain

def html_report(snapshot):
    data=safe_snapshot(snapshot)
    history=[upgrade(row) for row in data.get('history',[])]
    cells=[]
    for item in comparisons(history):
        last=item['last_result']; dims=last['dimensions']; quality=dims['quality']; accuracy=quality.get('accuracy')
        brief = explain(last)
        percent='未知 / Unknown' if accuracy is None else f'{accuracy:.1%}'
        interval=quality.get('interval')
        if interval: percent+=f' (95%: {interval[0]:.1%} – {interval[1]:.1%})'
        bar=0 if accuracy is None else max(0,min(100,round(accuracy*100)))
        cells.append('<article><h2>'+escape(item.get('source_alias') or '历史目标')+' · '+escape(item['model'])+'</h2>'
                     '<h3>'+escape(brief['headline'])+'</h3>'
                     + ''.join('<p>'+escape(line)+'</p>' for line in
                               (brief['capability'], brief['comparison'], brief['identity'], *brief['diagnostics']))
                     + '<details><summary>专业详情 / Evidence details</summary>'
                     '<p>任务 / Suite: '+escape(item.get('suite_version') or 'legacy-v1')+'</p>'
                     '<p>状态 / Status: '+escape(last.get('status') or 'unavailable')+' · '+escape(item.get('protocol_id') or '')+'</p>'
                     '<p>复算 / Replay: seed '+str(last.get('task_seed'))+' · '+str(last.get('task_count'))+' tasks</p>'
                     '<p>能力 / Quality: '+percent+'</p><div class="bar"><i style="width:'+str(bar)+'%"></i></div>'
                     '<p>行为 / Behavior: '+escape(dims['behavior'].get('identity_state') or 'no_reference')+'</p>'
                     '<p>可靠性 / Reliability: '+str(dims['reliability'].get('response_count',0))+' responses · '
                     +str(dims['reliability'].get('network_failures',0))+' network failures</p>'
                     '<p>历史 / History: '+escape(item['trend']['status'])+'</p>'
                     '<p>证据 / Evidence: '+escape(last['evidence_level'])+' · experimental</p></details></article>')
    rows=[]
    for row in history:
        values=(row.get('evaluated_at',''),row.get('source_alias',''),row.get('model',''),row.get('mode',''),
                row.get('status',''),row.get('evidence_level',''),row.get('suite_version','legacy-v1'))
        rows.append('<tr>'+''.join('<td>'+escape(str(value))+'</td>' for value in values)+'</tr>')
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'+\
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'+\
        '<title>模型质量体检 / Model Quality Assessment</title><style>body{font:15px system-ui,sans-serif;max-width:1100px;margin:30px auto;padding:0 20px;color:#183541}article{border:1px solid #dce5e9;border-radius:12px;padding:18px;margin:18px 0}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border-bottom:1px solid #ddd;padding:9px;text-align:left}.bar{height:12px;background:#edf3f4}.bar i{display:block;height:100%;background:#007e78}@media print{article{break-inside:avoid}}</style>'+\
        '<h1>模型质量体检 / Model Quality Assessment</h1><p>实验性结果，不认证模型身份。Historical change is not proof of substitution. 不同任务/参数不可直接排名。</p>'+\
        ''.join(cells or ['<p>尚无质量体检记录 / No quality assessment records.</p>'])+\
        '<h2>记录 / History</h2><table><thead><tr><th>时间</th><th>匿名目标</th><th>模型</th><th>任务</th><th>状态</th><th>证据</th><th>版本</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></html>'
