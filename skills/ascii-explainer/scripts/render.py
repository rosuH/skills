"""ASCII views of validated facts. No independent semantic calculations."""
from math import gcd
from functools import reduce
from string import ascii_uppercase, ascii_lowercase, digits
from textwrap import wrap


def codes(names):
    names = list(dict.fromkeys(names))
    pool = ascii_uppercase + ascii_lowercase + digits
    if len(names) > len(pool):
        raise ValueError('more than 62 diagram identifiers')
    result = {n: n for n in names if len(n) == 1 and n in pool}
    available = iter(c for c in pool if c not in result.values())
    for name in names:
        if name not in result:
            result[name] = next(available)
    return result


def strip(points, lanes, fmt, unit):
    """Shared boundary columns; each lane contains disjoint (start,end,code)."""
    points = sorted(set(points))
    lo, hi = points[0], points[-1]
    if lo == hi:
        return [f'Empty [{fmt(lo)},{fmt(hi)}); no occupied cells.']
    step = reduce(gcd, (b-a for a,b in zip(points, points[1:])))
    cells = (hi-lo)//step
    if cells <= 50:
        scale = 2 if cells <= 25 else 1
        pos = {p: (p-lo)//step*scale for p in points}
        note = f'Scale: {scale} column(s) = {step} {unit}; [start,end).'
    else:
        # ponytail: compress only at exact boundaries; dense views use tables.
        if len(points) > 26:
            raise ValueError('too many boundaries for an 80-column diagram')
        pos = {p: i*2 for i,p in enumerate(points)}
        note = 'NOT TO SCALE: each span is 2 columns; bounds are listed below.'
    width = pos[hi]
    prefix = max(5, max(len(name) for name,_ in lanes)) + 2
    labels = [' '] * (width+len(fmt(hi)))
    occupied = set()
    # Endpoints take precedence; omit colliding interior labels, never move ticks.
    for p in [lo,hi]+points[1:-1]:
        start = pos[p]; label = fmt(p)
        slots = set(range(start-1,start+len(label)+1))
        if p == hi and slots & occupied:
            raise ValueError('endpoint labels collide at this scale')
        if not slots & occupied:
            labels[start:start+len(label)] = label
            occupied |= set(range(start,start+len(label)))
    ticks = ['-']*(width+1)
    for x in pos.values(): ticks[x] = '+'
    lines = [note, ' '*prefix+''.join(labels).rstrip(), ' '*prefix+''.join(ticks)]
    for name,spans in lanes:
        row = ['.']*width
        for a,b,token in spans:
            row[pos[a]:pos[b]] = token*(pos[b]-pos[a])
        lines.append(name.ljust(prefix)+''.join(row)+'|')
    return lines


def diagram(model, facts, tables):
    """Return one bound block, or explicit table fallback for a dense view."""
    fmt = hex if model.get('base') == 16 else str
    kind = model['kind']; lines = [model.get('id','model')+' / '+kind]
    def note(text):
        lines.extend(wrap(text, width=78, break_long_words=False, break_on_hyphens=False))
    try:
        if kind == 'ranges':
            rows = facts['segments']
            names = [r['region'] for r in rows if r['region'] is not None]
            token = codes(names)
            points = [r[k] for r in rows for k in ('start','end')]
            if not points:
                return [lines[0]+f'\nEmpty root [{model["start"]},{model["end"]}); no occupied cells.']+tables[1:]
            lanes = [('visible',[(r['start'],r['end'],token[r['region']]) for r in rows if r['region'] is not None])]
            lines += strip(points,lanes,fmt,'coordinate unit(s)')
            note('. = NONE (no target); a terminal result is not a gap.')
            for r in rows:
                target = 'NONE' if r['region'] is None else token[r['region']]+' = '+r['region']
                detail = f'{target}: [{fmt(r["start"])},{fmt(r["end"])})'
                if r['result'] and r['result'] != r['region']: detail += ' -> '+r['result']
                if r['backing']: detail += f' -> {r["backing"]}+{fmt(r["offset"])}'
                note(detail)
            for q in facts['queries']:
                result = q['result'] or ('NONE' if q['inside'] else 'OUTSIDE')
                detail = f'{fmt(q["point"])} -> {result}'
                if q['backing']: detail += f' -> {q["backing"]}+{fmt(q["offset"])}'
                note(detail)
        elif kind == 'fields':
            rows = facts['fields'];token = codes(r['id'] for r in rows)
            points = [r[k] for r in rows for k in ('start','end')]
            if facts['received_bytes'] is not None:
                received_end = rows[0]['start']+facts['received_bytes']
                points.append(received_end)
            lanes = [('bytes',[(r['start'],r['end'],token[r['id']]) for r in rows if r['size']])]
            if facts['received_bytes'] is not None:
                lanes.append(('received',[(rows[0]['start'],received_end,'#')]))
            lines += strip(points,lanes,fmt,'byte(s)')
            if facts['received_bytes'] is not None:
                note(f'Received: # present, . missing; {facts["received_bytes"]} received, {facts["missing_bytes"]} missing.')
            for r in rows:
                note(f'{token[r["id"]]} = {r["id"]} [{fmt(r["start"])},{fmt(r["end"])}): {r["size"]} byte(s); {r["display"]}')
            for r in rows:
                if not r.get('bits'): continue
                bits = sorted(r['bits'],key=lambda b:b[1],reverse=True)
                bt = codes(b[0] for b in bits)
                lines += [f'{r["id"]}: bits {r["size"]*8-1}..0 (MSB first)',
                          'field  '+''.join(bt[b[0]]*b[2] for b in bits),
                          'value  '+''.join(b[3] if b[3]!='?' else '?'*b[2] for b in bits)]
                for name,lsb,width,value in bits:
                    note(f'{bt[name]} = {name} bits {lsb+width-1}..{lsb}: {value}')
            for c in facts['checksums']:
                spans=', '.join(f'[{fmt(a)},{fmt(b)})' for a,b in c['coverage']) or 'empty'
                note(f'{c["field"]} covers {spans}: {c["bytes"]} byte(s); value NOT verified.')
            note(f'Total: {facts["total_bytes"]} byte(s); end {fmt(facts["end"])} exclusive.')
        else:
            plan = facts['plan']; token = codes(p['id'] for p in plan)
            points = [0]+[p[k] for p in plan for k in ('start','end')]
            lanes = [(unit,[(p['start'],p['end'],token[p['id']]) for p in plan if unit in p['using']])
                     for units in model['resources'].values() for unit in units]
            lines += strip(points,lanes,str,'time unit(s)')
            note('. = idle; same task code on several lanes = one task using those resources.')
            for p in sorted(plan,key=lambda p:(p['start'],p['id'])):
                note(f'{token[p["id"]]} = {p["id"]} [{p["start"]},{p["end"]}) on '+', '.join(p['using']))
            for t in model['tasks']:
                if t['after']: note(', '.join(t['after'])+' -> '+t['id']+' (waits for all)')
            note('Arrows are dependencies; lane order alone is not a dependency.')
            note(f'Makespan {facts["makespan"]}; lower bound {facts["lower_bound"]}; checker: {facts["optimality"]}.')
            note('Busy resource-time: '+', '.join(f'{k}={v}' for k,v in facts['work'].items())+'.')
        if any(len(line)>80 or not line.isascii() for line in lines):
            raise ValueError('labels or values exceed 80 ASCII columns')
        return ['\n'.join(lines)]
    except ValueError as exc:
        return [lines[0]+'\nTable fallback: '+str(exc)+'.']+tables
