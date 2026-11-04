"""Build unmodified PX4 motion_planning sources as a local shared library."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def extract_auto_methods(px4, out):
    source = px4/'src/modules/flight_mode_manager/tasks/Auto/FlightTaskAuto.cpp'
    text = source.read_text(encoding='utf-8')
    # Preserve offsets while ignoring braces in comments and literals.
    masked = re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                    lambda m:' '*len(m[0]), text, flags=re.S)
    methods=[]
    for name in ('_checkEmergencyBraking','_updateTrajConstraints','_limitYawRate',
                 '_set_heading_from_mode','_generateHeadingAlongTraj','_compute_heading_from_2D_vector'):
        match=re.search(r'(?:void|bool) FlightTaskAuto::'+name+r'\s*\(',masked)
        if match is None:
            raise RuntimeError('PX4 source interface changed: missing '+name)
        start=masked.index('{',match.end())
        level=1
        end=start+1
        while level and end<len(masked):
            level += (masked[end]=='{')-(masked[end]=='}')
            end+=1
        if level:
            raise RuntimeError('Cannot extract balanced function '+name)
        methods.append(text[match.start():end].replace('FlightTaskAuto::','AutoAdapter::'))
    license_header=text[:text.index('*/')+2]
    (out/'auto_methods.generated.hpp').write_text(license_header+'\n\n'+'\n\n'.join(methods),encoding='utf-8')
    return source

def build(px4: Path):
    px4 = px4.resolve()
    files = [px4 / 'src/lib/motion_planning' / name for name in
             ('PositionSmoothing.cpp', 'VelocitySmoothing.cpp')]
    for file in files:
        if not file.is_file():
            raise FileNotFoundError(file)
    if importlib.util.find_spec('ziglang') is None:
        raise RuntimeError('Install the compiler in this environment: python -m pip install ziglang')
    out = ROOT / 'build'
    out.mkdir(exist_ok=True)
    auto_source=extract_auto_methods(px4,out)
    library = out / ('setpoint.dll' if sys.platform == 'win32' else 'libsetpoint.so')
    cmd = [sys.executable, '-m', 'ziglang', 'c++', '-std=c++17', '-O2', '-shared',
           '-fno-sanitize=undefined', '-o', str(library)]
    if sys.platform != 'win32':
        cmd.append('-fPIC')
    for include in [ROOT / 'native/compat', out, px4 / 'src/lib', px4 / 'src/lib/matrix']:
        cmd.extend(['-I', str(include)])
    cmd.extend(map(str, [ROOT / 'native/generator.cpp', *files]))
    env = os.environ.copy()
    env['ZIG_GLOBAL_CACHE_DIR'] = str(out / 'zig-global-cache')
    env['ZIG_LOCAL_CACHE_DIR'] = str(out / 'zig-local-cache')
    with (out / 'build.log').open('w', encoding='utf-8') as log:
        completed = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=log)
    if completed.returncode:
        print((out / 'build.log').read_text(encoding='utf-8')[-6000:], file=sys.stderr)
        raise RuntimeError(f'Compiler failed ({completed.returncode}); see build/build.log')
    # Pin the actual source contents, including headers, even for zip checkouts.
    source_files = set(files+[auto_source])
    for folder in ('motion_planning', 'mathlib', 'matrix'):
        source_files.update((px4 / 'src/lib' / folder).rglob('*.hpp'))
        source_files.update((px4 / 'src/lib' / folder).rglob('*.h'))
    hashes = {str(p.relative_to(px4)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(source_files)}
    adapter_hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [ROOT/'native/generator.cpp',ROOT/'native/auto_adapter.hpp',
                                ROOT/'build_native.py',out/'auto_methods.generated.hpp',
                                *sorted((ROOT/'native/compat').rglob('*.h'))]}
    try:
        revision = subprocess.run(['git', '-C', str(px4), 'describe', '--always', '--dirty', '--tags'],
                                  capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        revision = 'unknown (source snapshot without Git metadata)'
    (out / 'provenance.json').write_text(json.dumps({
        'px4_root': str(px4), 'revision': revision, 'platform': platform.platform(),
        'build_command': cmd, 'sha256': hashes,
        'adapter_sha256':adapter_hashes,
        'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(),
    }, indent=2), encoding='utf-8')
    print(library)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--px4', type=Path, required=True)
    build(parser.parse_args().px4)
