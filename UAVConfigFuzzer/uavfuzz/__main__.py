import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from .backend import NativeGenerator
from .model import ACTIVE, Domain, PARAMETERS, fitness, gps_to_ned
from .search import Search

ROOT = Path(__file__).resolve().parents[1]

def serializable(value):
    if isinstance(value, float) and not math.isfinite(value):
        return 'Infinity' if value == math.inf else '-Infinity' if value == -math.inf else 'NaN'
    if isinstance(value, dict):
        return {k:serializable(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(v) for v in value]
    return value

def dump(path, value):
    path.write_text(json.dumps(serializable(value), indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')

def read_json(path):
    def invalid(value):
        raise ValueError('non-standard JSON number: '+value)
    return json.loads(path.read_text(encoding='utf-8'), parse_constant=invalid)

def inputs(args):
    spec = read_json(args.config)
    if set(spec['defaults']) != set(PARAMETERS):
        raise ValueError('defaults must contain exactly the 19 named parameters')
    domains = {k:Domain(tuple(map(tuple, v['intervals'])), v['step']) for k,v in spec['domains'].items()}
    if not set(domains) <= ACTIVE:
        raise ValueError('search includes parameters not connected to this generator')
    pairs = spec['correlations']
    if any(a == b or a not in domains or b not in domains for a,b in pairs):
        raise ValueError('correlations must reference distinct searchable parameters')
    mission = read_json(args.mission)
    points = mission['waypoints']
    if mission['frame'] == 'gps':
        points = gps_to_ned(points)
    elif mission['frame'] != 'ned':
        raise ValueError('frame must be ned or gps')
    backend = NativeGenerator(args.library, spec['generator'], mission.get('types'))
    return spec, domains, points, backend

def run(args):
    spec, domains, mission, backend = inputs(args)
    # Refuse reuse so evidence from different runs cannot silently mix.
    args.out.mkdir(parents=True, exist_ok=False)
    baseline = backend.run(spec['defaults'], mission)
    scores = fitness(baseline, mission)
    with (args.out/'baseline.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['time','target_index','x','y','z','vx','vy','vz','ax','ay','az','yaw','yawrate'])
        writer.writerows(baseline.rows)
    provenance = ROOT/'build/provenance.json'
    native_info = read_json(provenance) if provenance.exists() else None
    dump(args.out/'manifest.json', {
        'scope':'setpoint_generator_and_fuzzing; software_only',
        'configuration_source':'explicit input; no constraint extraction', 'config':spec,
        'mission_ned':mission, 'mission_context':backend.mission_context,
        'seed':args.seed, 'N':args.n, 'K':args.k,
        'iterations':args.iterations, 'objective':args.objective, 'stage':args.command,
        'native_build':native_info, 'library_sha256':hashlib.sha256(args.library.read_bytes()).hexdigest(),
        'baseline':{'status':baseline.status, 'scores':scores},
        'limitations':['15 auto-mission parameters connected; 4 manual/controller parameters excluded; see README.',
                       'Literal interruption score includes startup/stopping samples; baseline can be infinite.',
                       'Remaining grid intervals are unexcluded, not proven safe.'],
    })
    if args.command == 'estimate':
        print(json.dumps(serializable({'status':baseline.status, 'scores':scores, 'samples':len(baseline.rows)})))
        return
    if args.command == 'nd':
        refined = read_json(args.single_bounds)
        if refined.get('kind') != 'software_estimated_1d_bounds' or refined.get('basis') != {
            'config':spec, 'mission_ned':serializable(mission), 'mission_context':backend.mission_context,
            'library_sha256':hashlib.sha256(args.library.read_bytes()).hexdigest()}:
            raise ValueError('n-D requires matching 1-D config, mission and native library provenance')
        domains = {key:Domain(tuple(map(tuple,value['intervals'])), value['step'])
                   for key,value in refined['domains'].items()}
        if set(domains) != set(spec['domains']):
            raise ValueError('refined bounds must contain exactly the original searchable parameters')
        for key, domain in domains.items():
            original = Domain(tuple(map(tuple,spec['domains'][key]['intervals'])),spec['domains'][key]['step'])
            if domain.step != original.step or any(
                not any(a <= low <= high <= b for a,b in original.intervals)
                for low,high in domain.intervals):
                raise ValueError('refined bounds must be a subset of original bounds on the same grid')
    excluded = {key:set() for key in domains}
    candidate_count, trial_count = 0, 0
    with (args.out/'trials.jsonl').open('w', encoding='utf-8') as log, \
         (args.out/'candidates.jsonl').open('w', encoding='utf-8') as candidates:
        def sink(record):
            nonlocal candidate_count, trial_count
            trial_count += 1
            log.write(json.dumps(serializable(record), allow_nan=False)+'\n')
            # A cutoff is an explicit experiment choice, not flight validation.
            failed = record['status'] != 'complete'
            value = record['scores'][args.objective]
            suspect = record['status'] == 'nonfinite' or (failed and args.objective == 'interruption')
            if args.threshold is not None:
                suspect = suspect or value > args.threshold
            if suspect:
                candidate_count += 1
                candidates.write(json.dumps(serializable({**record, 'validation':'software_only'}), allow_nan=False)+'\n')
                # n-D failures are retained as forbidden combinations, never
                # projected onto independent parameter ranges without proof.
                if record['correlated'] is None:
                    excluded[record['target']].add(record['config'][record['target']])
        started = time.perf_counter()
        search = Search(backend, spec['defaults'], mission, args.n, args.k, args.iterations, args.seed, sink)
        best = search.run(domains, args.objective, spec['correlations'] if args.command == 'nd' else None)
    dump(args.out/'best.json', [asdict(t) for t in best])
    dump(args.out/'bounds.json', {
        'kind':'software_estimated_1d_bounds' if args.command == '1d' else 'conditional_nd_results',
        'basis':{'config':spec, 'mission_ned':mission, 'mission_context':backend.mission_context,
                 'library_sha256':hashlib.sha256(args.library.read_bytes()).hexdigest()},
        'validation':'software_only; remaining values are not proven safe',
        'domains':{key:{'intervals':domain.exclude(excluded[key]).intervals, 'step':domain.step}
                   for key,domain in domains.items()},
        'note':'n-D constraints remain in candidates.jsonl as combinations; marginal domains are unchanged.'
    })
    summary = {'trials':trial_count, 'candidates':candidate_count, 'elapsed_s':time.perf_counter()-started}
    dump(args.out/'summary.json', summary)
    print(json.dumps(summary))

def main():
    parser = argparse.ArgumentParser(description='PX4 native setpoint-guided software fuzzer')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('estimate', '1d', 'nd'):
        p = sub.add_parser(name)
        p.add_argument('--config', type=Path, default=ROOT/'examples/config.json')
        p.add_argument('--mission', type=Path, default=ROOT/'examples/mission.json')
        p.add_argument('--library', type=Path, default=ROOT/'build'/('setpoint.dll' if sys.platform=='win32' else 'libsetpoint.so'))
        p.add_argument('--out', type=Path, required=True)
        p.add_argument('--objective', choices=['rapid','deviation','interruption'], default='interruption')
        p.add_argument('--n', type=int, default=100)
        p.add_argument('--k', type=int, default=5)
        p.add_argument('--iterations', type=int, default=200)
        p.add_argument('--seed', type=int, default=0)
        p.add_argument('--threshold', type=float, help='explicit software candidate cutoff; omitted = incomplete runs only')
        if name == 'nd':
            p.add_argument('--single-bounds', type=Path, required=True)
    args = parser.parse_args()
    if args.threshold is not None and not math.isfinite(args.threshold):
        parser.error('threshold must be finite')
    run(args)

if __name__ == '__main__':
    main()
