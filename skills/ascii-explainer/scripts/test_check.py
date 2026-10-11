"""Run: python3 scripts/test_check.py. Known wrong claims must be rejected."""
from copy import deepcopy
import unittest
from check import check, Invalid


class Checks(unittest.TestCase):
    def reject(self, model, message):
        with self.assertRaisesRegex(Invalid, message):
            check(model)

    def test_recursive_fallback_and_alias(self):
        m={'kind':'ranges','start':'0x1000','end':'0x1020','backings':{'R':32,'F':4,'D':4},'regions':[
            {'id':'R','start':0,'end':32,'priority':1,'backing':'R'},
            {'id':'F','start':10,'end':14,'priority':5,'backing':'F'},
            {'id':'C','start':8,'end':24,'priority':8,'children':[
                {'id':'D','start':4,'end':8,'priority':-50,'backing':'D'},
                {'id':'E','start':12,'end':16,'priority':0,'backing':'R','offset':0}]}],
            'queries':['0x100B','0x100D','0x1015','0x1001','0x1020']}
        r=check(m)['models'][0]['facts']
        self.assertEqual([(s['start'],s['end'],s['region']) for s in r['segments']],
            [(4096,4106,'R'),(4106,4108,'F'),(4108,4112,'D'),(4112,4116,'R'),(4116,4120,'E'),(4120,4128,'R')])
        self.assertEqual([q['region'] for q in r['queries']],['F','D','E','R',None])
        self.assertEqual([(q['backing'],q['offset']) for q in r['queries'][2:4]],[('R',1),('R',1)])
        self.assertFalse(r['queries'][-1]['inside'])
        m['claims']=[{k:s[k] for k in ('start','end','region')} for s in r['segments']]
        check(m)
        m['claims'][3]['region']='F'
        self.reject(m,'wrong target')

    def test_empty_negative_and_terminal_results(self):
        m={'kind':'ranges','start':-3,'end':5,'regions':[
            {'id':'L','start':0,'end':4,'priority':0},
            {'id':'C','start':1,'end':7,'priority':5,'children':[
                {'id':'E','start':1,'end':2,'priority':-1,'result':'BLOCK'}]},
            {'id':'Z','start':4,'end':4,'priority':100}], 'queries':[-1,1,5]}
        r=check(m)['models'][0]['facts']
        self.assertEqual([q['result'] for q in r['queries']],['BLOCK',None,None])
        self.assertEqual([(s['start'],s['end'],s['region']) for s in r['segments']],
                         [(-3,-1,'L'),(-1,0,'E'),(0,1,'L'),(1,5,None)])
        self.assertEqual(check({'kind':'ranges','start':3,'end':3,'regions':[]})['models'][0]['facts']['segments'],[])
        m['regions'].append({'id':'tie','start':0,'end':1,'priority':0})
        self.reject(m,'ambiguous')

    def test_range_rejections(self):
        m={'kind':'ranges','start':0,'end':4,'regions':[{'id':'A','start':0,'end':4,'priority':0}]}
        for patch in ({'end':5},{'start':-1},{'priority':True},{'children':[], 'result':'X'}, {'offset':1}):
            bad=deepcopy(m);bad['regions'][0].update(patch)
            with self.subTest(patch=patch): self.reject(bad,'.')
        bad=deepcopy(m);bad['backings']={'B':3};bad['regions'][0]['backing']='B'
        self.reject(bad,'alias exceeds')

    def layout(self, bits, data=None):
        m={'kind':'fields','origin':'0x105','base':16,'fields':[
            {'id':'N','size':2,'endian':'little','value':bits},
            {'id':'payload','size':{'count':'N','unit_bits':1},'tail_bits_from':'N'},
            {'id':'pad','align':4,'zero':True},{'id':'CRC','size':1}],
            'checksums':[{'field':'CRC','covers':['N','payload']}]}
        if data is not None: m['data']=data
        return m

    def test_layout_alignment_empty_and_tail(self):
        for bits,expected,total in [(5,[(261,263),(263,264),(264,264),(264,265)],4),
                                    (0,[(261,263),(263,263),(263,264),(264,265)],4),
                                    (9,[(261,263),(263,265),(265,268),(268,269)],8)]:
            r=check(self.layout(bits))['models'][0]['facts']
            self.assertEqual([(f['start'],f['end']) for f in r['fields']],expected)
            self.assertEqual(r['total_bytes'],total)
            self.assertEqual(r['checksums'][0]['bytes'],2+(bits+7)//8)
        r=check(self.layout(5,'05 00 15 7E'))['models'][0]['facts']
        self.assertEqual(r['missing_bytes'],0)
        self.assertEqual(r['fields'][1]['valid_tail_bits'],5)
        self.assertEqual(r['fields'][0]['display'],'5 (dec)')
        self.assertEqual(r['fields'][-1]['display'],'7E (hex)')
        self.assertEqual(check(self.layout(0))['models'][0]['facts']['fields'][2]['display'],'zero required')
        self.assertEqual(check(self.layout(5,'05 00 15'))['models'][0]['facts']['missing_bytes'],1)
        partial={'kind':'fields','origin':0,'data':'C0','fields':[{'id':'CRC','size':2}]}
        self.assertEqual(check(partial)['models'][0]['facts']['fields'][0]['display'],'C0 ?? (hex)')
        self.reject(self.layout(5,'05 00 F5 7E'),'unused high bits')
        self.reject(self.layout(0,'00 00 FF 7E'),'nonzero')
        self.reject(self.layout(5,'06 00 15 7E'),'disagrees')
        self.reject(self.layout(5,'05 00 15 7E 00'),'exceeds')
        bad=self.layout(0);bad['claims']=[{'id':'pad','start':263,'end':266,'size':3}]
        self.reject(bad,'claim mismatch')

    def test_bits_and_bad_schemas(self):
        m={'kind':'fields','origin':0,'data':'A0','fields':[{'id':'flags','size':1,'endian':'big','bits':[
            {'id':'compressed','lsb':7,'width':1},{'id':'kind','lsb':5,'width':2},
            {'id':'reserved','lsb':0,'width':5,'equals':0}]}]}
        result=check(m)
        self.assertEqual([row[3] for row in result['models'][0]['facts']['fields'][0]['bits']],['1','01','00000'])
        bad=deepcopy(m);bad['fields'][0]['bits'][2]['width']=4
        self.reject(bad,'cover')
        bad=deepcopy(m);bad['fields'][0]['bits'][2]['width']=6
        self.reject(bad,'overlap')
        for invalid in ({'kind':'oops'}, {'kind':'fields','origin':True,'fields':[]},
                        {'kind':'fields','origin':0,'fields':[{'id':'x','size':2**40,'bits':[]}]},
                        {'kind':'ranges','start':0,'end':1,'regions':[],'typo':1}):
            with self.subTest(invalid=invalid): self.reject(invalid,'.')

    def sched(self):
        return {'kind':'schedule','resources':{'worker':['W1','W2'],'gpu':['G']},'tasks':[
            {'id':'A','duration':4,'after':[],'needs':{'worker':1,'gpu':1}},
            {'id':'B','duration':3,'after':[],'needs':{'worker':1,'gpu':1}},
            {'id':'C','duration':2,'after':['A'],'needs':{'worker':1}},
            {'id':'D','duration':1,'after':['B','C'],'needs':{'worker':1}}], 'plan':[
            {'id':'A','start':0,'end':4,'using':['W1','G']},
            {'id':'B','start':4,'end':7,'using':['W1','G']},
            {'id':'C','start':4,'end':6,'using':['W2']},
            {'id':'D','start':7,'end':8,'using':['W1']}]}

    def test_schedule_accounting_and_conflicts(self):
        m=self.sched();r=check(m)['models'][0]['facts']
        self.assertEqual(r['makespan'],8);self.assertEqual(r['work'],{'worker':10,'gpu':7})
        self.assertEqual(r['optimality'],'not_proven')
        bad=deepcopy(m);bad['plan'][1].update(start=0,end=3,using=['W2','G'])
        self.reject(bad,'G: A overlaps B')
        bad=deepcopy(m);bad['plan'][2]['using']=['W1'];self.reject(bad,'overlaps')
        bad=deepcopy(m);bad['plan'][2].update(start=3,end=5);self.reject(bad,'before A')
        bad=deepcopy(m);bad['plan'][0]['end']=3;self.reject(bad,'duration')
        bad=deepcopy(m);bad['plan'].append(bad['plan'][0]);self.reject(bad,'repeated')
        bad=deepcopy(m);bad['plan'].pop();self.reject(bad,'every task')
        bad=deepcopy(m);bad['plan'][0]['using']=['W1'];self.reject(bad,'needs')
        bad=deepcopy(m);bad['tasks'][0]['after']=['D'];self.reject(bad,'cycle')

    def test_bound_and_binding(self):
        m={'kind':'schedule','resources':{'worker':['W1']},'tasks':[
            {'id':'A','duration':2,'after':[],'needs':{'worker':1}}],
            'plan':[{'id':'A','start':0,'end':2,'using':['W1']}]}
        r=check(m);self.assertEqual(r['models'][0]['facts']['optimality'],'proven_by_bound')
        answer='\n\n'.join('```text\n'+t+'\n```' for t in r['models'][0]['tables'])
        self.assertTrue(check(m,answer,view='table')['answer_checked'])
        for bad in (answer.replace('W1','W2'),answer+'\n```text\nextra\n```',answer+answer,answer.replace('  ',' ',1),answer.replace('```text','```json'),answer.replace('```text','```'),answer+'\n```',answer.replace('```','````'),answer+'\n~~~text\nextra\n~~~'):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(Invalid,'answer code blocks'): check(m,bad,view='table')

    def test_diagram_geometry_and_binding(self):
        r=check(self.sched());block=r['models'][0]['blocks'][0]
        # Columns before the trailing boundary encode two cells per time unit.
        lanes={line.split()[0]:line.split()[1][:-1] for line in block.splitlines()
               if line.startswith(('W1 ', 'W2 ', 'G '))}
        self.assertEqual(lanes,{'W1':'AAAAAAAABBBBBBDD',
                                'W2':'........CCCC....','G':'AAAAAAAABBBBBB..'})
        answer='```text\n'+block+'\n```'
        self.assertTrue(check(self.sched(),answer)['answer_checked'])
        for bad in (answer.replace('AAAA','....',1),answer+'\n    A -> B',answer+'\n     A -> B',answer+answer):
            with self.assertRaises(Invalid):check(self.sched(),bad)
        self.assertEqual(r['models'][0]['facts'],check(self.sched(),view='table')['models'][0]['facts'])

    def test_field_and_range_diagrams(self):
        r=check(self.layout(0))['models'][0]['blocks'][0]
        self.assertIn('bytes  NNNNBBCC|',r)
        self.assertIn('payload [0x107,0x107): 0 byte(s); empty',r)
        partial={'kind':'fields','origin':27,'data':'50 09 00 A6 01 C0','fields':[
            {'id':'head','size':3},{'id':'payload','size':2},{'id':'CRC','size':2}]}
        block=check(partial)['models'][0]['blocks'][0]
        self.assertIn('received  ############..|',block)
        m={'kind':'ranges','start':-3,'end':4,'regions':[{'id':'X','start':1,'end':4,'priority':0}]}
        block=check(m)['models'][0]['blocks'][0]
        self.assertIn('visible  ..XXXXXX......|',block)
        m['end']=1000000
        self.assertIn('NOT TO SCALE',check(m)['models'][0]['blocks'][0])
        for model in (m,partial,self.layout(0),self.sched()):
            for block in check(model)['models'][0]['blocks']:
                self.assertTrue(block.isascii());self.assertLessEqual(max(map(len,block.splitlines())),80)


if __name__=='__main__':
    unittest.main()
