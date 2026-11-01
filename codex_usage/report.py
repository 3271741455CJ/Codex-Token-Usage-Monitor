"""Assemble the local report and embed it into a network-disabled HTML file."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
import base64
import hashlib
import json
import math
from pathlib import Path
import re
from .metadata import scan_metadata, source
from .safety import checked_local_path
from .privacy import protect_report

TOKEN_FIELDS=('input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')


def number(value):
    return max(0,int(value)) if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) else 0


def sum_tokens(rows):
    return {key:sum(number(row.get(key)) for row in rows) for key in TOKEN_FIELDS}


def build_report(home: Path, output: Path, *, official_reader=None) -> dict:
    from .sessions import scan_sessions
    from .database import scan_database
    metadata=scan_metadata(home)
    from .official import unavailable
    official = official_reader(metadata['account']) if official_reader else unavailable()
    logs=scan_sessions(home,current_account_id=metadata['account'].get('account_id'))
    database=scan_database(home,output/'.scratch')
    threads=database.get('threads',{})
    if isinstance(threads,list): threads={row['id']:row for row in threads}
    projects_by_id={row['id']:row for row in database.get('projects',[]) if 'id' in row}
    account_id=metadata['account'].get('account_id')
    sessions=logs.get('sessions',[])
    turns=logs.get('turns',[])
    session_map={row['id']:row for row in sessions}
    for row in sessions:
        db=threads.get(row['id'],{})
        if isinstance(db.get('title'),str): row['title']=db['title'][:500]
        creator=row.get('creator_account_id') or db.get('creator_account_id')
        row['creator_account_id']=creator
        row['attribution']='matched' if creator and account_id and creator==account_id else 'other' if creator and account_id else 'unknown'
        row['attribution_basis']='会话创建者账号；不证明每轮实际计费账号' if creator else '没有可核实的账号字段'
        if db.get('project_id'):
            project=projects_by_id.get(db['project_id'],{})
            row['project_id']=db['project_id']
            row['project_name']=project.get('name') or row.get('project') or '未命名项目'
        row['database_tokens_used']=db.get('tokens_used')
    for row in turns:
        session=session_map.get(row.get('session_id'),{})
        for field in ('title','project_name','project_id','attribution','attribution_basis'):
            if field in session: row[field]=session[field]
    # Database-only records are coverage evidence, never token additions.
    missing=[]
    for sid,row in threads.items():
        if sid not in session_map:
            record={key:row.get(key) for key in ('id','title','project_id','tokens_used','model','reasoning_effort','rollout_path','created_at','updated_at','source')}
            if isinstance(record.get('title'),str): record['title']=record['title'][:500]
            creator=row.get('creator_account_id')
            record['attribution']='matched' if creator and account_id and creator==account_id else 'other' if creator and account_id else 'unknown'
            record['project_name']=projects_by_id.get(row.get('project_id'),{}).get('name')
            missing.append(record)
    coverage=dict(logs.get('coverage',{}))
    known_index_counts=[row['tokens_used'] for row in missing if isinstance(row.get('tokens_used'),(int,float)) and not isinstance(row.get('tokens_used'),bool) and math.isfinite(row['tokens_used']) and row['tokens_used']>=0]
    coverage.update(database_sessions=len(threads),parsed_sessions=len(sessions),database_only_sessions=len(missing),
                    database_only_tokens_used=sum(known_index_counts) if known_index_counts or not missing else None,
                    database_only_unknown_tokens=len(missing)-len(known_index_counts),
                    account_attribution='matched 只表示创建者匹配；离线无法验证每轮计费账号或覆盖其他设备。')
    grouped=defaultdict(list); daily=defaultdict(list); projects=defaultdict(list)
    for turn in turns:
        segments=turn.get('model_segments') or [turn]
        for segment in segments:
            grouped[(segment.get('model') or turn.get('model') or '未知',segment.get('reasoning_effort') or turn.get('reasoning_effort') or '未知')].append(segment)
        stamp=turn.get('started_at') or turn.get('ended_at') or ''
        # Dates are local calendar days, with the original timestamp preserved.
        try: day=datetime.fromisoformat(stamp.replace('Z','+00:00')).astimezone().date().isoformat()
        except (ValueError,TypeError,AttributeError): day='未知'
        daily[day].append(turn)
        projects[turn.get('project_id') or turn.get('project') or '未分类'].append(turn)
    totals=sum_tokens(turns)
    totals.update(turn_count=len(turns),session_count=len(sessions),project_count=len(projects),
                  recorded_response_count=sum(number(t.get('request_count')) for t in turns),
                  turns_without_usage=sum(t.get('usage_record_count')==0 for t in turns),
                  matched_creator=sum_tokens([t for t in turns if t.get('attribution')=='matched']),
                  unknown_creator=sum_tokens([t for t in turns if t.get('attribution')=='unknown']),
                  other_creator=sum_tokens([t for t in turns if t.get('attribution')=='other']))
    sources=[]; seen=set()
    for src in metadata.get('sources',[])+logs.get('sources',[])+database.get('sources',[]):
        if not isinstance(src,dict) or not src.get('path'): continue
        if src['path'] in seen: continue
        try:
            safe=checked_local_path(src['path'])
            src['uri']=safe.as_uri()
        except (ValueError,OSError): continue
        seen.add(src['path']); sources.append(src)
    # Generate source URLs only from validated local paths, never raw URI fields.
    for row in sessions+turns+logs.get('rate_limits',[]):
        src=row.get('source')
        if isinstance(src,dict) and src.get('path'):
            try: src['uri']=checked_local_path(src['path']).as_uri()
            except (ValueError,OSError): src.pop('uri',None)
    cli_versions=sorted({str(row.get('cli_version')) for row in sessions if row.get('cli_version')})
    metadata['versions']['observed_cli_versions']=cli_versions
    warnings=metadata.get('warnings',[])+logs.get('warnings',[])+database.get('warnings',[])
    if missing:
        warnings.append(f'另有 {len(missing)} 个会话只在本地数据库索引中存在，缺少可解析的用量日志；索引计数单独展示，不加入可核验的 Token 汇总。')
    warnings += [
        'Token 汇总仅覆盖本机可读取、去重后的日志，不是账号全生命周期账单，也不包含未同步设备或已删除日志。',
        '输入缓存 Token 是输入的子集；推理输出 Token 是输出的子集，均不重复加到总量。',
        '5 小时和每周限额是服务端用量窗口百分比，不是可换算的固定 Token 配额。本地快照过期后无法推断当前剩余量。',
        '离线无法获取实时 Usage & Billing、付款/发票、API 余额、账单费用、完整订阅与各模型额度；仅显示文件中实际存在的字段。',
    ]
    return {**metadata,'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),
        'official_usage':official,
        'local_timezone':str(datetime.now().astimezone().tzinfo),'totals':totals,'sessions':sessions,'turns':turns,
        'rate_limits':logs.get('rate_limits',[]),'sources':sources,'warnings':list(dict.fromkeys(warnings)),
        'coverage':coverage,'database_only_sessions':missing,
        'models':[{'model':key[0],'reasoning_effort':key[1],**sum_tokens(rows)} for key,rows in sorted(grouped.items())],
        'projects':[{'id':key,'name':rows[0].get('project_name') or key,'turn_count':len(rows),**sum_tokens(rows)} for key,rows in projects.items()],
        'daily':[{'date':key,**sum_tokens(rows)} for key,rows in sorted(daily.items())]}


def render_html(report: dict) -> str:
    return _render_html(protect_report(report))


def _render_html(report: dict) -> str:
    template=Path(__file__).with_name('dashboard.html').read_text(encoding='utf-8')
    serialized=json.dumps(report,ensure_ascii=False,separators=(',',':')).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    html=template.replace('__REPORT_DATA__',serialized)
    scripts=re.findall(r'<script\b[^>]*>(.*?)</script\s*>',html,re.S|re.I)
    hashes=['\'sha256-'+base64.b64encode(hashlib.sha256(script.encode('utf-8')).digest()).decode()+'\'' for script in scripts]
    policy="default-src 'none'; script-src "+' '.join(hashes)+"; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; object-src 'none'; frame-src 'none'; worker-src 'none'; manifest-src 'none'; base-uri 'none'; form-action 'none'"
    return html.replace('__CSP__',policy,1)


def write_report(report: dict, output: Path, *, export_json: bool=False) -> Path:
    report = protect_report(report)
    output.mkdir(exist_ok=True)
    target=output/'latest.html'
    temporary=output/'latest.html.tmp'
    temporary.write_text(_render_html(report),encoding='utf-8')
    temporary.replace(target)
    if export_json:
        (output/'usage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return target
