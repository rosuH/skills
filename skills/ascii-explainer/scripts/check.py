#!/usr/bin/env python3
"""Compute exact ranges/layouts; validate schedules; render and bind ASCII tables.

Stdlib only. Input JSON is data, never code. See references/checks.md for scope.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def obj(value, allowed, required=()):
    require(isinstance(value, dict), 'expected an object')
    require(not set(value) - set(allowed.split()), f'unknown keys: {set(value) - set(allowed.split())}')
    require(set(required) <= set(value), f'missing keys: {set(required) - set(value)}')
    return value


def num(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and re.fullmatch(r'-?(?:0x[0-9a-fA-F]+|[0-9]+)', value):
        sign = -1 if value.startswith('-') else 1
        raw = value.lstrip('-')
        return sign * int(raw, 16 if raw.startswith('0x') else 10)
    raise Invalid(f'expected integer or decimal/hex integer string: {value!r}')


def ident(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,19}', value),
            f'use a short ASCII identifier (1-20 characters): {value!r}')
    require(value not in ('NONE', 'OUTSIDE'), 'NONE and OUTSIDE are reserved')
    return value


def array(value):
    require(isinstance(value, list), 'expected an array')
    return value


def number_format(model):
    base = model.get('base', 10)
    require(base in (10, 16) and type(base) is int, 'base must be 10 or 16')
    return (lambda n: hex(n)) if base == 16 else str


def table(headers, rows):
    cells = [list(headers)] + [[str(x) for x in row] for row in rows]
    require(all(all(c.isascii() and '\n' not in c and '\t' not in c for c in row) for row in cells),
            'table cells must be single-line ASCII')
    widths = [max(len(row[i]) for row in cells) for i in range(len(headers))]
    lines = ['  '.join(c.ljust(w) for c, w in zip(row, widths)).rstrip() for row in cells]
    require(max(map(len, lines)) <= 80, 'table exceeds 80 columns; shorten identifiers or values')
    return '\n'.join(lines)


def ranges(m):
    obj(m, 'kind id base start end regions backings queries claims', ('start', 'end', 'regions'))
    lo, hi = num(m['start']), num(m['end'])
    require(lo <= hi, 'root end precedes start')
    fmt = number_format(m)
    backings = m.get('backings', {})
    require(isinstance(backings, dict), 'backings must be an object')
    backings = {ident(k): num(v) for k, v in backings.items()}
    require(all(v >= 0 for v in backings.values()), 'negative backing size')
    seen = set(); boundaries = {lo, hi}

    def nodes(items, origin, limit, depth=0):
        require(depth <= 16, 'nesting exceeds 16 levels')
        result = []
        for raw in array(items):
            obj(raw, 'id start end priority children result backing offset', ('id', 'start', 'end', 'priority'))
            name = ident(raw['id'])
            require(name not in seen, f'duplicate region {name}')
            seen.add(name)
            require(len(seen) <= 200, 'at most 200 regions')
            a, b = origin + num(raw['start']), origin + num(raw['end'])
            require(origin <= a <= b <= limit, f'{name}: outside parent or reversed range')
            node = dict(id=name, start=a, end=b, priority=num(raw['priority']))
            if 'children' in raw:
                require(not {'result', 'backing', 'offset'} & raw.keys(), f'{name}: container cannot have a result/backing')
                node['children'] = nodes(raw['children'], a, b, depth+1)
            else:
                node['result'] = ident(raw.get('result', name))
                node['backing'] = raw.get('backing')
                node['offset'] = num(raw.get('offset', 0))
                if node['backing'] is not None:
                    require(node['backing'] in backings, f'{name}: unknown backing')
                    require(0 <= node['offset'] <= node['offset'] + b-a <= backings[node['backing']],
                            f'{name}: alias exceeds backing')
                else:
                    require('offset' not in raw, f'{name}: offset needs a backing')
            for other in result:
                require(not (node['priority'] == other['priority'] and max(a, other['start']) < min(b, other['end'])),
                        f'{name}/{other["id"]}: overlapping equal-priority siblings are ambiguous')
            result.append(node); boundaries.update((a, b))
        return sorted(result, key=lambda n: n['priority'], reverse=True)

    # All child starts/ends are relative to their parent, including root children.
    tree = nodes(m['regions'], lo, hi)

    def resolve(items, x):
        for n in items:
            if n['start'] <= x < n['end']:
                hit = resolve(n['children'], x) if 'children' in n else n
                if hit is not None:
                    return hit
        return None

    def record(a, b, hit):
        return dict(start=a, end=b, region=hit['id'] if hit else None,
                    result=hit['result'] if hit else None,
                    backing=hit['backing'] if hit else None,
                    offset=hit['offset']+a-hit['start'] if hit and hit['backing'] is not None else None)

    segments = []
    points = sorted(boundaries)
    for a, b in zip(points, points[1:]):
        hit = resolve(tree, a)
        row = record(a, b, hit)
        if segments and segments[-1]['region'] == row['region']:
            segments[-1]['end'] = b
        else:
            segments.append(row)
    if 'claims' in m:
        cursor = lo
        for claim in array(m['claims']):
            obj(claim, 'start end region', ('start', 'end', 'region'))
            a, b = num(claim['start']), num(claim['end'])
            require(a == cursor and a < b <= hi, 'claims must partition root without gaps/overlaps')
            for row in segments:
                if max(a,row['start']) < min(b,row['end']):
                    require(claim['region'] == row['region'],
                            f'wrong target on [{fmt(max(a,row["start"]))},{fmt(min(b,row["end"]))}): expected {row["region"]}, got {claim["region"]}')
            cursor = b
        require(cursor == hi, 'claims omit the end of the root')
    rows = [[f'[{fmt(r["start"])},{fmt(r["end"])})', r['region'] or 'NONE', r['result'] or '-',
             r['backing'] or '-', fmt(r['offset']) if r['offset'] is not None else '-'] for r in segments]
    tables = [table(['range [start,end)', 'region', 'result', 'backing', 'offset'], rows)]
    queries = []
    for raw in array(m.get('queries', [])):
        x = num(raw); inside = lo <= x < hi
        hit = resolve(tree, x) if inside else None
        q = record(x,x,hit); q['point'] = x; q['inside'] = inside
        queries.append(q)
    if queries:
        tables.append(table(['point','region','result','backing','offset'],
            [[fmt(q['point']), q['region'] or ('NONE' if q['inside'] else 'OUTSIDE'), q['result'] or '-',
              q['backing'] or '-', fmt(q['offset']) if q['offset'] is not None else '-'] for q in queries]))
    return dict(segments=segments, queries=queries, normalized_regions=tree), tables


def fields(m):
    obj(m, 'kind id base origin data fields checksums claims', ('origin', 'fields'))
    origin = num(m['origin']); require(origin >= 0, 'negative byte origin')
    fmt = number_format(m)
    data = None
    if 'data' in m:
        require(isinstance(m['data'], str) and re.fullmatch(r'(?:[0-9a-fA-F]{2}\s*)*',m['data']), 'data must be hex bytes')
        data = bytes.fromhex(m['data'])
    cursor = origin; seen = {}; values = {}; rows = []; bit_tables = []
    for f in array(m['fields']):
        obj(f, 'id size align endian value bits zero tail_bits_from', ('id',))
        name = ident(f['id']); require(name not in seen, f'duplicate field {name}')
        require(('size' in f) != ('align' in f), f'{name}: specify size OR align')
        if 'align' in f:
            align = num(f['align']); require(align > 0, f'{name}: nonpositive alignment')
            size = (-cursor) % align
            require(not {'endian','value','bits','tail_bits_from'} & f.keys(), f'{name}: alignment field cannot be decoded')
        else:
            raw_size = f['size']
            if isinstance(raw_size,dict):
                obj(raw_size, 'count unit_bits', ('count','unit_bits'))
                require(raw_size['count'] in values, f'{name}: count must refer to a known earlier integer field')
                unit = num(raw_size['unit_bits']); require(unit > 0, 'nonpositive unit_bits')
                size = (values[raw_size['count']] * unit + 7)//8
            else:
                size = num(raw_size)
        require(0 <= size <= 2**40, f'{name}: invalid size')
        if 'zero' in f: require(type(f['zero']) is bool, 'zero must be Boolean')
        a,b = cursor,cursor+size
        chunk = data[a-origin:b-origin] if data is not None else None
        complete = chunk is not None and len(chunk)==size
        if f.get('zero') and chunk is not None:
            require(not any(chunk), f'{name}: nonzero reserved/padding bytes')
        value = None
        if 'endian' in f:
            require(f['endian'] in ('little','big') and 1 <= size <= 8, f'{name}: integer needs endian and size 1..8')
            if complete: value = int.from_bytes(chunk, f['endian'])
        if 'value' in f:
            require('endian' in f, f'{name}: integer value requires endian')
            declared = num(f['value']); require(0 <= declared < 2**(8*size), f'{name}: value does not fit')
            if value is not None: require(value == declared, f'{name}: declared value disagrees with data')
            # Even partial input must agree with supplied value.
            if chunk is not None: require(declared.to_bytes(size,f['endian'])[:len(chunk)] == chunk, f'{name}: supplied prefix disagrees with value')
            value = declared
        if value is not None: values[name] = value
        row = dict(id=name,start=a,end=b,size=size,value=value)
        if 'tail_bits_from' in f:
            key=f['tail_bits_from']; require(key in values, f'{name}: unknown bit count')
            count=values[key]; require(size==(count+7)//8, f'{name}: size disagrees with bit count')
            tail=count%8 or (8 if count else 0); row['valid_tail_bits']=tail
            if complete and size and tail<8: require(chunk[-1] >> tail == 0, f'{name}: nonzero unused high bits')
        if 'bits' in f:
            require('endian' in f and 1 <= size <= 8, f'{name}: bit fields need a decoded integer of size 1..8')
        bit_rows=[]; occupied=set()
        for bit in array(f.get('bits', [])):
            obj(bit, 'id lsb width equals', ('id','lsb','width'))
            bit_id=ident(bit['id']); lsb,width=num(bit['lsb']),num(bit['width'])
            require(width>0 and 0<=lsb<lsb+width<=size*8, f'{name}.{bit_id}: bit range outside field')
            positions=set(range(lsb,lsb+width)); require(not occupied & positions, f'{name}: overlapping bit fields')
            occupied |= positions
            require(bit_id not in [r[0] for r in bit_rows], f'{name}: duplicate bit id')
            v=(value>>lsb)&((1<<width)-1) if value is not None else None
            if 'equals' in bit:
                wanted=num(bit['equals']);require(0<=wanted<2**width, f'{name}: expected bit value does not fit')
                require(v is not None and v==wanted, f'{name}.{bit_id}: expected {wanted}, got {v}')
            bit_rows.append([bit_id,lsb,width,format(v,f'0{width}b') if v is not None else '?'])
        if 'bits' in f:
            require('endian' in f and occupied==set(range(size*8)), f'{name}: bit fields must cover decoded integer exactly')
            row['bits']=bit_rows
            bit_tables.append(table([name+' bits','lsb','width','binary'], bit_rows))
        if value is not None: display=f'{value} (dec)'
        elif chunk is not None and size<=8:
            display=' '.join(f'{chunk[i]:02X}' if i<len(chunk) else '??' for i in range(size))+' (hex)'
        elif complete: display=f'{size} bytes'
        else: display='?'
        if size and f.get('zero') and not complete: display='zero required'
        if size==0: display='empty'
        if 'tail_bits_from' in f: display += f'; tail={row["valid_tail_bits"]} bits'
        row['display']=display;seen[name]=row;rows.append(row);cursor=b
    require(rows, 'fields must not be empty')
    if data is not None: require(len(data)<=cursor-origin, 'data exceeds the declared record')
    for c in array(m.get('claims',[])):
        obj(c,'id start end size',('id','start','end','size'))
        require(c['id'] in seen, 'claim refers to unknown field')
        require(all(num(c[k])==seen[c['id']][k] for k in ('start','end','size')), f'{c["id"]}: layout claim mismatch')
    checksums=[]
    for c in array(m.get('checksums',[])):
        obj(c,'field covers',('field','covers'))
        require(c['field'] in seen, 'unknown checksum field')
        covers=array(c['covers']); require(len(covers)==len(set(covers)), 'duplicate checksum coverage')
        require(all(n in seen and n!=c['field'] for n in covers), 'invalid checksum coverage')
        spans=sorted((seen[n]['start'],seen[n]['end']) for n in covers if seen[n]['size'])
        merged=[]
        for a,b in spans:
            if merged and merged[-1][1]==a: merged[-1][1]=b
            else: merged.append([a,b])
        checksums.append(dict(field=c['field'],coverage=merged,bytes=sum(b-a for a,b in merged),value_verified=False))
    tables=[table(['field','start','end (excl)','bytes','value'],
                  [[r['id'],fmt(r['start']),fmt(r['end']),r['size'],r['display']] for r in rows])]+bit_tables
    if checksums:
        tables.append(table(['checksum','covered range','bytes','value checked'],
            [[c['field'],f'[{fmt(a)},{fmt(b)})',b-a,'NO'] for c in checksums for a,b in c['coverage']]))
    missing=None if data is None else cursor-origin-len(data)
    return dict(fields=rows,total_bytes=cursor-origin,end=cursor,received_bytes=None if data is None else len(data),missing_bytes=missing,checksums=checksums),tables


def schedule(m):
    obj(m,'kind id resources tasks plan',('resources','tasks','plan'))
    groups=m['resources'];require(isinstance(groups,dict) and groups, 'resources must be a nonempty object')
    units={}
    for group,names in groups.items():
        ident(group);require(array(names), 'resource group is empty')
        for name in names:
            ident(name);require(name not in units, f'duplicate resource {name}');units[name]=group
    tasks={}
    for t in array(m['tasks']):
        obj(t,'id duration after needs',('id','duration','after','needs'))
        name=ident(t['id']); require(name not in tasks, f'duplicate task {name}')
        duration=num(t['duration']); require(duration>0, f'{name}: duration must be positive')
        after=array(t['after']);require(len(after)==len(set(after)), f'{name}: duplicate predecessor')
        needs=t['needs'];require(isinstance(needs,dict) and needs, f'{name}: empty resource needs')
        needs={k:num(v) for k,v in needs.items()}
        require(all(k in groups and 0<v<=len(groups[k]) for k,v in needs.items()), f'{name}: invalid resource demand')
        tasks[name]=dict(id=name,duration=duration,after=after,needs=needs)
    require(tasks,'tasks must not be empty')
    for t in tasks.values(): require(all(p in tasks and p!=t['id'] for p in t['after']), f'{t["id"]}: invalid predecessor')
    critical={};pending=set(tasks)
    while pending:
        ready=[n for n in pending if all(p in critical for p in tasks[n]['after'])]
        require(ready,'dependency cycle')
        for n in ready:
            critical[n]=tasks[n]['duration']+max((critical[p] for p in tasks[n]['after']),default=0)
            pending.remove(n)
    plan={}
    for p in array(m['plan']):
        obj(p,'id start end using',('id','start','end','using'))
        name=p['id']; require(name in tasks and name not in plan,f'unknown or repeated task {name}')
        a,b=num(p['start']),num(p['end']);require(a>=0 and b-a==tasks[name]['duration'],f'{name}: wrong duration or negative start')
        using=array(p['using']);require(len(using)==len(set(using)) and all(u in units for u in using),f'{name}: unknown/duplicate resource')
        require(dict(Counter(units[u] for u in using))==tasks[name]['needs'],f'{name}: assigned resources do not meet needs')
        plan[name]=dict(id=name,start=a,end=b,using=using)
    require(set(plan)==set(tasks),f'plan must schedule every task exactly once; missing {set(tasks)-set(plan)}')
    for n,p in plan.items():
        for pred in tasks[n]['after']:
            require(plan[pred]['end']<=p['start'],f'{n}: starts before {pred} finishes')
    allocations=[]
    for unit,group in units.items():
        active=sorted((p for p in plan.values() if unit in p['using']),key=lambda p:(p['start'],p['id']))
        for a,b in zip(active,active[1:]):
            require(a['end']<=b['start'],f'{unit}: {a["id"]} overlaps {b["id"]}')
        allocations.extend([[unit,p['id'],p['start'],p['end'],p['end']-p['start']] for p in active])
    makespan=max(p['end'] for p in plan.values())
    work={g:sum(t['duration']*t['needs'].get(g,0) for t in tasks.values()) for g in groups}
    # Integer time/durations: round pooled-resource work bounds upward.
    bound=max([max(critical.values())]+[(work[g]+len(groups[g])-1)//len(groups[g]) for g in groups])
    result=dict(plan=list(plan.values()),makespan=makespan,work=work,lower_bound=bound,
                optimality='proven_by_bound' if makespan==bound else 'not_proven')
    tables=[table(['resource','task','start','end (excl)','duration'],allocations),
            table(['metric','value'],[['makespan',makespan],['lower_bound',bound],['optimality',result['optimality']]]),
            table(['resource group','busy resource-time'],[[g,v] for g,v in work.items()])]
    return result,tables


def check(document, answer=None, view='diagram'):
    from render import diagram
    require(view in ('diagram','table'), 'view must be diagram or table')
    if isinstance(document,dict) and 'models' in document:
        obj(document,'models',('models',));models=array(document['models'])
    else: models=[document]
    require(models,'no models')
    outputs=[];all_blocks=[];seen=set()
    for m in models:
        require(isinstance(m,dict),'model must be an object')
        name=ident(m.get('id','model'));require(name not in seen,'duplicate model id');seen.add(name)
        kind=m.get('kind');require(kind in ('ranges','fields','schedule'),'kind must be ranges, fields, or schedule')
        facts,tables={'ranges':ranges,'fields':fields,'schedule':schedule}[kind](m)
        blocks=diagram(m,facts,tables) if view=='diagram' else tables
        outputs.append(dict(id=name,kind=kind,facts=facts,tables=tables,blocks=blocks));all_blocks.extend(blocks)
    if answer is not None:
        fenced=re.findall(r'^```([^\n]*)\n(.*?)\n```$',answer,re.M|re.S)
        require(answer.count('```') == 2*len(fenced) and not re.search(r'(?m)^ *~{3,}',answer),
                'answer code blocks must use complete triple-backtick text fences')
        require(all(language == 'text' for language, _ in fenced), 'answer code blocks must use text fences')
        prose=re.sub(r'^```[^\n]*\n.*?\n```$', '', answer, flags=re.M|re.S)
        require(not re.search(r'(?m)^(?: {4}|\t)[ \t]*\S',prose),
                'answer code blocks must not use unchecked indented blocks')
        blocks=[body for _, body in fenced]
        require(Counter(blocks)==Counter(all_blocks),'answer code blocks differ from generated blocks (missing, changed, extra, or duplicate block)')
    return dict(ok=True,scope='structured inputs only; source transcription and prose need review',answer_checked=answer is not None,models=outputs)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',help='JSON model file; - reads stdin')
    parser.add_argument('--view',choices=['diagram','table'],default='diagram',help='bound output view (default: diagram)')
    parser.add_argument('--answer',help='verify all fenced answer blocks exactly match the selected view')
    args=parser.parse_args()
    try:
        raw=sys.stdin.read() if args.input=='-' else Path(args.input).read_text()
        document=json.loads(raw)
        answer=Path(args.answer).read_text() if args.answer else None
        result=check(document,answer,args.view)
    except (ValueError,TypeError,KeyError,OverflowError,OSError,RecursionError) as exc:
        print(json.dumps(dict(ok=False,error=str(exc)),ensure_ascii=True))
        return 2
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return 0


if __name__=='__main__':
    sys.exit(main())
