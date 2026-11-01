"""Create synthetic, non-private data for browser QA. Does not read Codex files."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codex_usage.report import render_html, sum_tokens


def demo_report():
    now=datetime.now(timezone.utc)
    source={'path':'C:\\Demo\\Codex\\sessions\\demo.jsonl','uri':'file:///C:/Demo/Codex/sessions/demo.jsonl','kind':'session','description':'合成测试日志，无真实账号数据','exists':True,'line':18}
    turns=[]
    for i in range(36):
        start=now-timedelta(days=i%12,hours=i)
        item={'id':f'turn-{i}','session_id':f'demo-{i%3}','title':['离线用量报告','文档与数据整理','界面交互验证'][i%3],'project':['C:\\Demo\\Usage','C:\\Demo\\Docs'][i%2],
              'started_at':start.isoformat(),'ended_at':(start+timedelta(minutes=3)).isoformat(),'model':['gpt-6-astra','gpt-6.1-sol'][i%2],'reasoning_effort':['ultra','high','medium'][i%3],
              'input_tokens':15000+i*1333,'cached_input_tokens':6000+i*600,'output_tokens':2300+i*77,'reasoning_output_tokens':1200+i*40,
              'total_tokens':17300+i*1410,'source':dict(source,line=i*20+5),'usage_sources':[dict(source,line=i*20+8)],'attribution':['matched','unknown','other'][i%3],
              'status':'completed','thread_source':'cli','root_session_id':f'demo-{i%3}','root_turn_id':f'turn-{i}','request_count':3,'accounting_method':'response_usage'}
        item['model_segments']=[{k:item[k] for k in ('model','reasoning_effort','input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')}]
        turns.append(item)
    sessions=[]
    for i in range(3):
        rows=[t for t in turns if t['session_id']==f'demo-{i}']
        sessions.append({'id':f'demo-{i}','title':rows[0]['title'],'project':rows[0]['project'],'model':'mixed','reasoning_effort':'mixed','created_at':rows[-1]['started_at'],'updated_at':rows[0]['ended_at'],'turn_count':len(rows),'attribution':rows[0]['attribution'],'source':source,**sum_tokens(rows)})
    return {'generated_at':now.isoformat(),'schema_version':1,'account':{'email':'demo@example.invalid','name':'演示用户','account_id':'demo-account','plan_type':'pro','login_method':'OpenAI / ChatGPT 账号登录','provider_name':'OpenAI','api_key_masked':None,'verification':'合成数据，仅用于界面测试'},
        'configuration':{'codex_home':'C:\\Demo\\Codex','model':'gpt-6-astra','reasoning_effort':'ultra','model_provider':'openai','base_url':None},
        'versions':{'desktop_version':'26.1021.3705.0','cache_client_version':'0.164.0','cache_fetched_at':now.isoformat()},
        'official_usage':{'status':'ok','usage_status':'ok','limits_status':'ok','usage_fetched_at':now.isoformat(),'limits_fetched_at':now.isoformat(),'summary':{'lifetimeTokens':12345678,'peakDailyTokens':1234567,'longestRunningTurnSec':540,'currentStreakDays':8,'longestStreakDays':14},'daily':[{'date':(now-timedelta(days=i)).date().isoformat(),'tokens':(30-i)*12345} for i in range(29,-1,-1)],'rate_limits':[{'label':'Codex 共享额度','primary':{'usedPercent':20,'windowDurationMins':300,'resetsAt':int((now+timedelta(hours=2)).timestamp())},'secondary':{'usedPercent':41,'windowDurationMins':10080,'resetsAt':int((now+timedelta(days=3)).timestamp())},'credits':{'balance':0}}]},
        'totals':sum_tokens(turns),'turns':turns,'sessions':sessions,'sources':[source],
        'rate_limits':[{'limit_id':'codex','limit_name':'Codex 共享额度','timestamp':now.isoformat(),'attribution':'matched','account_id':'demo-account','primary':{'used_percent':38,'window_minutes':300,'resets_at':int((now+timedelta(hours=2)).timestamp())},'secondary':{'used_percent':71,'window_minutes':10080,'resets_at':int((now+timedelta(days=3)).timestamp())},'credits':{'has_credits':False,'unlimited':False,'balance':'0'},'source':source}],
        'coverage':{'files_read':3,'files_discovered':3,'modern_response_count':108,'database_sessions':4,'parsed_sessions':3,'database_only_sessions':1,'database_only_tokens_used':12000},
        'database_only_sessions':[{'id':'missing-log','title':'仅有索引的历史会话','tokens_used':12000,'model':'gpt-6-astra'}],
        'model_catalog':[{'slug':'gpt-6-astra','display_name':'GPT-6 Astra','description':'演示模型资料','default_reasoning_level':'medium','supported_reasoning_levels':[{'effort':'high','description':'High'},{'effort':'ultra','description':'Ultra'}],'context_window':272000}],
        'warnings':['本页全部为合成数据，用于验证布局和交互。','本地日志总量不等于当前账号的官方账单；创建者归属不等于每轮实际计费账号。'],'models':[],'projects':[],'daily':[]}


if __name__=='__main__':
    output=Path(__file__).resolve().parents[1]/'.qa'/'demo.html'
    output.parent.mkdir(exist_ok=True)
    output.write_text(render_html(demo_report()),encoding='utf-8')
    print(output)
