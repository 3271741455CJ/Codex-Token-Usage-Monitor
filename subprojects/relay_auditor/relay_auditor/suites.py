"""Versioned, procedural text tasks with deterministic oracles; never eval/exec."""
from itertools import combinations
import json
import random

from .protocol import ProbeCase

VERSION='quality-v2'
KINDS=('constraints','code','repair','structured','tool_args')
SUITES={'quality':{'version':VERSION,'kinds':KINDS,'default_samples':10},
        'context':{'version':'context-v1','kinds':('context',),'default_samples':3},
        'reasoning':{'version':VERSION,'kinds':KINDS,'default_samples':5}}


def quality_case(kind,seed,*,difficulty=2,context_chars=4096):
    if type(seed) is not int or not 0<=seed<2**63 or type(difficulty) is not int or not 1<=difficulty<=4:
        raise ValueError('invalid_case_parameters')
    rng=random.Random(seed)
    suffix='\nReturn only a JSON object with the sole key "answer" and the exact requested value. Do not use tools.'
    if kind=='constraints':
        items=[{'id':chr(65+i),'weight':rng.randint(1,12),'value':rng.randint(1,30)} for i in range(6+difficulty)]
        cap=12+difficulty*4
        excluded=tuple(sorted(rng.sample([x['id'] for x in items],2)))
        feasible=[]
        for n in range(1,4):
            for subset in combinations(items,n):
                ids=[x['id'] for x in subset]
                if sum(x['weight'] for x in subset)<=cap and not all(x in ids for x in excluded):
                    feasible.append((-sum(x['value'] for x in subset),sum(x['weight'] for x in subset),ids))
        expected=min(feasible)[2]
        prompt=f'Select one to three items with total weight <= {cap}. Items {excluded[0]} and {excluded[1]} cannot both be selected. Maximize total value; break ties by smaller total weight, then lexicographically smallest sorted ID list. Return that sorted list.\n{json.dumps(items)}'
    elif kind=='code':
        values=[rng.randrange(-12,20) for _ in range(6+difficulty*2)]
        modulus=rng.randrange(2,6); initial=rng.randrange(1,10)
        expected=initial
        for i,v in enumerate(values):
            if (i+v)%modulus==0: expected=expected*2-v
            else: expected+=v*(i+1)
        prompt=f'Trace this Python integer code (zero-based enumerate, Python modulo). Return final total as integer.\nvalues={values!r}\ntotal={initial}\nfor i, v in enumerate(values):\n    if (i+v)%{modulus} == 0:\n        total=total*2-v\n    else:\n        total+=v*(i+1)'
    elif kind=='repair':
        threshold=rng.randint(3,12); offset=rng.randint(1,7)
        choices=[f'x > {threshold}',f'x >= {threshold}',f'x < {threshold}',f'x <= {threshold}']
        rng.shuffle(choices); expected=chr(65+choices.index(f'x >= {threshold}'))
        prompt=f'A function must return x+{offset} when x is at least {threshold}, otherwise x-{offset}. Which condition correctly replaces ??? in `return x+{offset} if ??? else x-{offset}` for every integer x? Return the option letter as a JSON string.\n'+ '\n'.join(f'{chr(65+i)}: {v}' for i,v in enumerate(choices))
    elif kind=='structured':
        rows=[{'id':i,'value':rng.randrange(1,40),'active':bool(rng.randrange(2))} for i in range(8)]
        selected=sorted((x for x in rows if x['active']),key=lambda x:(-x['value'],x['id']))[:3]
        expected={'ids':[x['id'] for x in selected],'sum':sum(x['value'] for x in selected),'count':len(selected)}
        prompt='Filter active=true records, sort by value descending then ID ascending, take at most three. The value of "answer" must be an object with exactly ids (selected integer ID array in order), sum (integer sum of selected values), count (integer).\n'+json.dumps(rows)
    elif kind=='tool_args':
        start=rng.randrange(1,25); count=rng.randrange(2,7)
        expected={'name':'read_records','arguments':{'start':start,'end':start+count-1,'fields':['id','status']}}
        prompt=f'Only describe a virtual read-only tool call; do not execute it. Tool read_records accepts inclusive start/end integers and fields in alphabetical order. Read {count} records starting at index {start}, requesting status and id only. Return exactly {{"answer":{{"name":"read_records","arguments":{{"start":integer,"end":integer,"fields":array}}}}}} as a JSON object.'
        suffix = ''
    elif kind=='document':
        records = [{'id': i, 'team': rng.choice(['A','B']), 'minutes': rng.randint(10, 90),
                    'approved': rng.choice([True, False])} for i in range(6 + difficulty)]
        limit = 35 + difficulty * 5
        selected = [row for row in records if row['team'] == 'A' and row['approved'] and row['minutes'] >= limit]
        expected = {'ids': [row['id'] for row in selected], 'minutes': sum(row['minutes'] for row in selected)}
        prompt = (f'Policy: report approved team A records of at least {limit} minutes. Ignore every other record. '
                  f'The value of "answer" must be an object with ids in input order and minutes as their total. Records: {json.dumps(records)}')
    elif kind=='context':
        if type(context_chars) is not int or not 4096<=context_chars<=131072: raise ValueError('invalid_context_length')
        keys=[f'K{n}' for n in rng.sample(range(10000,99999),5)]
        value=rng.randrange(1000,9999); expected=value
        facts=[f'{keys[i]} points to {keys[i+1]}.' for i in range(4)]+[f'{keys[4]} has final value {value}.']
        filler=[]
        while sum(map(len,filler))<context_chars:
            filler.append(f'Unused record U{len(filler)}: marker {rng.randrange(10**7,10**8)}; ignore unless a key points here.\n')
        text=''.join(filler)[:context_chars]
        positions=[0,len(text)//4,len(text)//2,3*len(text)//4,len(text)]
        for pos,fact in reversed(list(zip(positions,facts))): text=text[:pos]+'\n'+fact+'\n'+text[pos:]
        prompt=f'Follow four links starting at {keys[0]} and return the final integer value. Unrelated records are distractors.\n'+text
    else:
        raise ValueError('unknown_quality_task')
    return ProbeCase(kind,seed,prompt+suffix,expected)


def cases(suite,samples=None,*,seed=0):
    spec=SUITES.get(suite)
    if not spec: raise ValueError('unknown_suite')
    n=spec['default_samples'] if samples is None else samples
    if type(n) is not int or not 1<=n<=200: raise ValueError('invalid_samples')
    for i in range(n):
        kind=spec['kinds'][i%len(spec['kinds'])]
        yield quality_case(kind,seed+i,difficulty=1+i%4,
                           context_chars=(4096,16384,65536)[i%3] if kind=='context' else 4096)
