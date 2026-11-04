"""Five mutation strategies, shared software oracle and equal DUT-call budgets."""
import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import time

from .__main__ import ROOT, inputs, dump, serializable
from .model import Domain, PARAMETERS, fitness

METHODS=('1d','nd','ga','binary','random')
LABELS={'1d':'1-D mutation','nd':'n-D mutation','ga':'Genetic algorithm',
        'binary':'Binary search','random':'Random mutation'}

@dataclass(frozen=True)
class Oracle:
    rapid: float=4.0
    deviation: float=5.0

    def bad(self, status, scores):
        return status!='complete' or scores['rapid']>self.rapid or scores['deviation']>self.deviation

    def rank(self, trial):
        scores=trial['scores']
        severity=max(scores['rapid']/self.rapid,scores['deviation']/self.deviation)
        return (self.bad(trial['status'],scores),severity)

class BinaryTrack:
    def __init__(self, domain, default):
        ticks=domain.ticks()
        if len(ticks)!=1:
            raise ValueError('binary baseline requires one contiguous input interval')
        self.domain=domain
        self.low,self.high=ticks[0]
        self.anchor=max(self.low,min(self.high,round(default/domain.step)))
        self.safe_low=self.safe_high=self.anchor
        self.bad_low=self.bad_high=None
        self.anchor_bad=False
        self.stage=0
        self.turn=0
        self.exhausted=0

    def propose(self):
        if self.stage<3:
            return (self.anchor,self.low,self.high)[self.stage]
        for _ in range(2):
            self.turn=1-self.turn
            if self.turn and self.bad_low is not None and self.safe_low-self.bad_low>1:
                return (self.safe_low+self.bad_low)//2
            if not self.turn and self.bad_high is not None and self.bad_high-self.safe_high>1:
                return (self.safe_high+self.bad_high)//2
        self.exhausted+=1
        return self.anchor

    def observe(self, tick, bad):
        if self.stage==0:
            self.anchor_bad=bad
        elif tick<self.anchor:
            if bad: self.bad_low=tick
            else: self.safe_low=tick
        elif tick>self.anchor:
            if bad: self.bad_high=tick
            else: self.safe_high=tick
        self.stage+=1

    def result(self):
        if self.anchor_bad:
            return Domain((),self.domain.step)
        return Domain(((self.domain.value(self.safe_low),self.domain.value(self.safe_high)),),self.domain.step)

class Experiment:
    def __init__(self, backend, spec, domains, mission, oracle, seed, n, k, out):
        self.backend,self.spec,self.domains,self.mission=backend,spec,domains,mission
        self.oracle,self.rng,self.n,self.k=oracle,random.Random(seed),n,k
        self.defaults=spec['defaults']
        self.out=out
        self.count=0
        self.bad_count=0
        self.excluded={key:set() for key in domains}
        self.history={key:[] for key in domains}
        self.seeds={key:[] for key in domains}
        self.unique=set()
        self.log=None

    def evaluate(self, config, involved, stage):
        sequence=self.backend.run(config,self.mission)
        scores=fitness(sequence,self.mission)
        self.count+=1
        record={'evaluation':self.count,'stage':stage,'involved':involved,
                'config':config,'status':sequence.status,'scores':scores,
                'anomalous':self.oracle.bad(sequence.status,scores)}
        self.unique.add(tuple(config[key] for key in PARAMETERS))
        if record['anomalous']:
            self.bad_count+=1
            for key in involved:
                self.excluded[key].add(config[key])
        self.log.write(json.dumps(serializable(record),allow_nan=False)+'\n')
        return record

    def single(self, calls, domains=None, stage='1d'):
        domains=self.domains if domains is None else domains
        names=[key for key,d in domains.items() if d.intervals]
        if not names:
            raise ValueError('no nonempty search domain remains')
        for i in range(calls):
            key=names[i%len(names)]
            history=self.history[key]
            domain=domains[key]
            seeds=self.seeds[key]
            if seeds:
                domain=domain.local(self.rng.choice(seeds)['config'][key])
            config=self.defaults.copy()
            config[key]=domain.sample(self.rng)
            record=self.evaluate(config,[key],stage)
            # Freeze the Top K seeds throughout each N-candidate generation.
            history.append(record)
            if len(history)==self.n:
                self.seeds[key]=sorted(seeds+history,key=self.oracle.rank,reverse=True)[:self.k]
                history.clear()

    def nd(self, budget):
        # A separate warmup belongs to n-D's own budget, never borrowed free
        # from the independently compared 1-D strategy.
        warmup=budget//2
        self.single(warmup,stage='nd_1d_warmup')
        refined={key:d.exclude(self.excluded[key]) for key,d in self.domains.items()}
        pairs=[(a,b) for a,b in self.spec['correlations'] if refined[a].intervals and refined[b].intervals]
        history={pair:[] for pair in pairs}
        seed_pools={pair:[] for pair in pairs}
        for i in range(budget-warmup):
            if not pairs:
                self.single(1,stage='nd_no_remaining_pair_fallback_1d')
                continue
            pair=pairs[(i//3)%len(pairs)]
            target,related=pair
            if i%3==0:
                domain=refined[target]
                seeds=seed_pools[pair]
                if seeds:
                    domain=domain.local(self.rng.choice(seeds)['config'][target])
                target_value=domain.sample(self.rng)
            ticks=refined[related].ticks()
            critical=[refined[related].value(ticks[0][0]),refined[related].value(ticks[-1][1]),self.defaults[related]]
            config={**self.defaults,target:target_value,related:critical[i%3]}
            record=self.evaluate(config,[target,related],'nd_correlated')
            history[pair].append(record)
            if len(history[pair])==3*self.n:
                seed_pools[pair]=sorted(seed_pools[pair]+history[pair],key=self.oracle.rank,reverse=True)[:self.k]
                history[pair].clear()
        return {'warmup_evaluations':warmup,'correlated_budget':budget-warmup,
                'eligible_pairs':pairs,'last_triplet_may_be_truncated_to_budget':True}

    def random_config(self):
        return {**self.defaults,**{key:d.sample(self.rng) for key,d in self.domains.items()}}

    def random_single(self,budget):
        names=[key for key,domain in self.domains.items() if domain.intervals]
        if not names:
            raise ValueError('no nonempty search domain remains')
        for _ in range(budget):
            key=self.rng.choice(names)
            config=self.defaults.copy()
            config[key]=self.domains[key].sample(self.rng)
            self.evaluate(config,[key],'random_single_parameter')

    def ga(self,budget):
        population=[]
        next_population=[]
        for i in range(budget):
            if not population:
                config=self.random_config()
            else:
                def parent():
                    return max(self.rng.choices(population,k=3),key=self.oracle.rank)['config']
                a,b=parent(),parent()
                config=self.defaults.copy()
                for key,domain in self.domains.items():
                    config[key]=a[key] if self.rng.random()<.5 else b[key]
                    if self.rng.random()<.2:
                        config[key]=domain.sample(self.rng)
            record=self.evaluate(config,list(self.domains),'ga')
            next_population.append(record)
            if len(next_population)==self.n:
                population=sorted(population+next_population,key=self.oracle.rank,reverse=True)[:self.n]
                next_population=[]

    def run(self,method,budget):
        started=time.perf_counter()
        extra={}
        with self.out.open('w',encoding='utf-8') as self.log:
            if method=='1d': self.single(budget)
            elif method=='nd': extra=self.nd(budget)
            elif method=='random':
                self.random_single(budget)
                extra={'mutation_scope':'one uniformly selected parameter; all others default',
                       'feedback_guided':False}
            elif method=='ga': self.ga(budget)
            elif method=='binary':
                tracks={key:BinaryTrack(d,self.defaults[key]) for key,d in self.domains.items()}
                names=list(tracks)
                for i in range(budget):
                    key=names[i%len(names)]
                    track=tracks[key]
                    tick=track.propose()
                    config={**self.defaults,key:track.domain.value(tick)}
                    record=self.evaluate(config,[key],'binary')
                    track.observe(tick,record['anomalous'])
                extra={'exhausted_bracket_rechecks':sum(t.exhausted for t in tracks.values()),
                       'continuous_safe_component_assumption':True}
            else: raise ValueError(method)
        bounds={key:(tracks[key].result() if method=='binary' else domain.exclude(self.excluded[key]))
                for key,domain in self.domains.items()}
        assert self.count==budget
        return {'label':LABELS[method],'evaluations':self.count,'unique_configurations':len(self.unique),
                'anomalous_evaluations':self.bad_count,'elapsed_s':time.perf_counter()-started,
                'domains':{key:{'intervals':d.intervals,'step':d.step} for key,d in bounds.items()},
                'observed_rejected_values':{key:sorted(values) for key,values in self.excluded.items()},**extra}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=ROOT/'examples/config.json')
    p.add_argument('--mission',type=Path,default=ROOT/'examples/mission.json')
    p.add_argument('--library',type=Path,default=ROOT/'build/setpoint.dll')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--budget',type=int,default=600,help='actual native evaluations per method and seed, including n-D warmup')
    p.add_argument('--n',type=int,default=20,help='initial samples per parameter / GA population size')
    p.add_argument('--k',type=int,default=5)
    p.add_argument('--seeds',type=int,nargs='+',default=[42])
    p.add_argument('--rapid-threshold',type=float,default=4)
    p.add_argument('--deviation-threshold',type=float,default=5)
    args=p.parse_args()
    if args.budget<6 or not 1<=args.k<=args.n or args.n<2:
        p.error('require budget >= 6, N >= max(K,2), K >= 1')
    if len(set(args.seeds))!=len(args.seeds): p.error('seeds must be distinct')
    if not all(math.isfinite(v) and v>0 for v in (args.rapid_threshold,args.deviation_threshold)):
        p.error('thresholds must be finite and positive')
    spec,domains,mission,backend=inputs(args)
    if any(len(d.intervals)!=1 for d in domains.values()):
        p.error('this binary baseline requires contiguous original intervals; refined output may be discontinuous')
    oracle=Oracle(args.rapid_threshold,args.deviation_threshold)
    baseline=backend.run(spec['defaults'],mission)
    base_scores=fitness(baseline,mission)
    if oracle.bad(baseline.status,base_scores):
        p.error('baseline itself violates the chosen oracle; use a nominal mission/config before inferring bounds')
    args.out.mkdir(parents=True,exist_ok=False)
    result={'schema':'fig5_ablation_v1','kind':'software_pilot','config':spec,'mission_ned':mission,
            'mission_context':backend.mission_context,'budget_per_method_seed':args.budget,
            'N':args.n,'K':args.k,'seeds':args.seeds,'parameter_order':PARAMETERS,
            'thresholds':{'rapid_m_s2':oracle.rapid,'deviation_m':oracle.deviation,
                          'interruption':'status != complete; includes time limit'},
            'baseline':{'status':baseline.status,'scores':base_scores,'shared_calibration_evaluations':1},
            'library_sha256':hashlib.sha256(args.library.read_bytes()).hexdigest(),
            'random_strategy':'Uniformly select one parameter, sample its original grid, keep all others default; no feedback guidance.',
            'projection':'1-D and Random exclude only the selected target value. Anomalous n-D/GA configurations exclude every involved sampled value; conservative marginal projection, not causal attribution.',
            'range_semantics':'Unexcluded grid values are software-estimated, not verified safe. Binary assumes a connected safe component.',
            'normalization':'Common original configured domain per parameter, never per-method inferred range.',
            'unsupported_parameters':[key for key in PARAMETERS if key not in domains],
            'runs':{}}
    provenance=ROOT/'build/provenance.json'
    result['native_build']=json.loads(provenance.read_text(encoding='utf-8')) if provenance.exists() else None
    for seed in args.seeds:
        result['runs'][str(seed)]={}
        for method in METHODS:
            experiment=Experiment(backend,spec,domains,mission,oracle,seed,args.n,args.k,
                                  args.out/f'{method}_seed{seed}.jsonl')
            report=experiment.run(method,args.budget)
            result['runs'][str(seed)][method]=report
            dump(args.out/'results.json',result)
            print(f'seed={seed} method={method}: {report["evaluations"]} calls, '
                  f'{report["anomalous_evaluations"]} anomalous, {report["elapsed_s"]:.2f}s',flush=True)
    print(args.out/'results.json',flush=True)

if __name__=='__main__': main()
