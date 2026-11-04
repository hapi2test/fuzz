import ctypes as C
from pathlib import Path
import math
from .model import PARAMETERS, Sequence

class NativeGenerator:
    def __init__(self, library, settings, mission_types=None):
        self.settings = settings
        self.mission_types = mission_types
        self.mission_context = {'types':mission_types}
        self.library = Path(library).resolve()
        self.dll = C.CDLL(str(self.library))
        try:
            self.dll.uav_abi_version.restype=C.c_int
            if self.dll.uav_abi_version()!=2:
                raise RuntimeError('Native ABI changed; rebuild with build_native.py')
        except AttributeError as error:
            raise RuntimeError('Old native DLL; rebuild with build_native.py') from error
        dptr = C.POINTER(C.c_double)
        self.dll.uav_run.argtypes = [dptr, C.c_int, dptr, C.c_int, C.POINTER(C.c_int), dptr, C.c_int]
        self.dll.uav_run.restype = C.c_void_p
        for method in ('uav_count', 'uav_status'):
            getattr(self.dll, method).argtypes = [C.c_void_p]
            getattr(self.dll, method).restype = C.c_int
        self.dll.uav_data.argtypes = [C.c_void_p]
        self.dll.uav_data.restype = dptr
        self.dll.uav_free.argtypes = [C.c_void_p]
        self.dll.uav_free.restype = None

    def run(self, config, mission):
        p = [float(config[key]) for key in PARAMETERS]
        flat = [float(v) for point in mission for v in point]
        if len(mission) < 2 or any(len(point) != 3 for point in mission) or not all(map(math.isfinite, p+flat)):
            raise ValueError('finite config and at least two 3D waypoints required')
        s = self.settings
        args = [s[key] for key in ('dt', 'max_time', 'acceptance_radius', 'xy_error', 'z_radius', 'gain')]
        if not all(math.isfinite(x) and x > 0 for x in args):
            raise ValueError('generator settings must be finite and positive')
        if math.ceil(args[1]/args[0]) > 1_000_000:
            raise ValueError('requested sequence exceeds one million samples')
        optional = {'takeoff_ramp_time':3, 'land_alt1':10, 'land_alt2':5,
                    'ground_z':mission[0][2], 'yaw_mode':0, 'yaw_error_deg':12, 'initial_yaw_rad':0}
        args += [float(s.get(key,value)) for key,value in optional.items()]
        if not all(map(math.isfinite,args)) or args[6]<=0 or args[7]<0 or args[8]<0 or args[11]<=0:
            raise ValueError('invalid takeoff/landing/yaw settings')
        if args[10] not in range(6):
            raise ValueError('yaw_mode must be an integer from 0 to 5')
        types=['position']*len(mission) if self.mission_types is None else self.mission_types
        if len(types)!=len(mission) or any(t not in ('position','takeoff','land') for t in types):
            raise ValueError('types must specify position/takeoff/land for each waypoint')
        if any(t=='land' for t in types[:-1]):
            raise ValueError('land must be the final waypoint')
        if types[-1]=='land' and not math.isclose(mission[-1][2],args[9],abs_tol=1e-6):
            raise ValueError('landing target must lie at ground_z')
        encoded=[{'position':0,'takeoff':1,'land':2}[t] for t in types]
        handle = self.dll.uav_run((C.c_double*len(p))(*p), len(p),
                                  (C.c_double*len(flat))(*flat), len(mission),
                                  (C.c_int*len(encoded))(*encoded),
                                  (C.c_double*len(args))(*args),len(args))
        if not handle:
            raise RuntimeError('native generator failed; not classified as a UAV anomaly')
        try:
            count = self.dll.uav_count(handle)
            data = self.dll.uav_data(handle)
            rows = [[data[i*13+j] for j in range(13)] for i in range(count)]
            status = {0:'complete', 1:'time_limit', 2:'nonfinite'}[self.dll.uav_status(handle)]
            return Sequence(rows, status)
        finally:
            self.dll.uav_free(handle)
