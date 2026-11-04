from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import math
import random


PARAMETERS = ('MPC_ACC_HOR', 'MPC_ACC_HOR_MAX', 'MPC_TILTMAX_AIR',
              'MPC_ACC_DOWN_MAX', 'MPC_ACC_UP_MAX', 'MPC_JERK_MAX', 'MPC_JERK_AUTO',
              'MPC_XY_VEL_ALL', 'MPC_XY_CRUISE', 'MPC_XY_VEL_MAX', 'MPC_Z_VEL_ALL',
              'MPC_Z_V_AUTO_UP', 'MPC_Z_VEL_MAX_UP', 'MPC_Z_V_AUTO_DN',
              'MPC_Z_VEL_MAX_DN', 'MPC_TKO_SPEED', 'MPC_LAND_SPEED',
              'MPC_TILTMAX_LND', 'MPC_YAWRAUTO_MAX')


ACTIVE = {'MPC_ACC_HOR', 'MPC_ACC_DOWN_MAX', 'MPC_ACC_UP_MAX', 'MPC_JERK_AUTO',
          'MPC_XY_VEL_ALL', 'MPC_XY_CRUISE', 'MPC_XY_VEL_MAX', 'MPC_Z_VEL_ALL',
          'MPC_Z_V_AUTO_UP', 'MPC_Z_V_AUTO_DN', 'MPC_Z_VEL_MAX_UP',
          'MPC_Z_VEL_MAX_DN', 'MPC_TKO_SPEED', 'MPC_LAND_SPEED', 'MPC_YAWRAUTO_MAX'}

@dataclass(frozen=True)
class Domain:
    """Finite union of inclusive, zero-anchored discrete-grid intervals."""
    intervals: tuple
    step: float

    def __post_init__(self):
        if not math.isfinite(self.step) or self.step <= 0:
            raise ValueError('step must be finite and positive')
        previous = -math.inf
        for low, high in self.intervals:
            if not math.isfinite(low) or not math.isfinite(high) or low > high or low <= previous:
                raise ValueError('intervals must be finite, ordered, non-overlapping')
            previous = high

    def ticks(self):
        step = Decimal(str(self.step))
        return [(int((Decimal(str(a))/step).to_integral_value(rounding=ROUND_CEILING)),
                 int((Decimal(str(b))/step).to_integral_value(rounding=ROUND_FLOOR)))
                for a, b in self.intervals]

    def value(self, tick):
        return float(Decimal(tick) * Decimal(str(self.step)))

    def contains(self, value):
        if not math.isfinite(value):
            return False
        tick = round(value / self.step)
        return math.isclose(value, self.value(tick), abs_tol=1e-8, rel_tol=0) and any(
            a <= tick <= b for a, b in self.ticks())

    def sample(self, rng: random.Random):
        ranges = [(a, b) for a, b in self.ticks() if a <= b]
        total = sum(b-a+1 for a, b in ranges)
        if not total:
            raise ValueError('empty mutation domain')
        offset = rng.randrange(total)
        for a, b in ranges:
            if offset <= b-a:
                return self.value(a+offset)
            offset -= b-a+1
        raise AssertionError('unreachable')

    def local(self, seed):
        # ±50% for negative seeds too; one step avoids a zero-seed trap.
        radius = max(abs(seed)*0.5, self.step)
        return Domain(tuple((max(a, seed-radius), min(b, seed+radius))
                            for a, b in self.intervals if max(a, seed-radius) <= min(b, seed+radius)), self.step)

    def exclude(self, values):
        excluded = sorted({round(v/self.step) for v in values if self.contains(v)})
        output = []
        for low, high in self.ticks():
            start = low
            for tick in excluded:
                if start <= tick <= high:
                    if start < tick:
                        output.append((self.value(start), self.value(tick-1)))
                    start = tick+1
            if start <= high:
                output.append((self.value(start), self.value(high)))
        return Domain(tuple(output), self.step)

def gps_to_ned(waypoints):
    """Spherical local NED projection, reference = first waypoint (degrees/metres)."""
    if len(waypoints) < 2:
        raise ValueError('mission requires at least two waypoints')
    lat0, lon0, alt0 = waypoints[0]
    result = []
    for lat, lon, alt in waypoints:
        if not (-90 <= lat <= 90 and -180 <= lon <= 180) or not all(map(math.isfinite, (lat, lon, alt))):
            raise ValueError('invalid geographic waypoint')
        # Wrapped longitude differences permit missions across the date line.
        dlon = (lon-lon0+180) % 360-180
        result.append((6378137*math.radians(lat-lat0),
                       6378137*math.cos(math.radians(lat0))*math.radians(dlon), -(alt-alt0)))
    return result

@dataclass
class Sequence:
    rows: list
    status: str

def segment_distance(point, start, end):
    line = [b-a for a, b in zip(start, end)]
    offset = [p-a for p, a in zip(point, start)]
    length2 = sum(x*x for x in line)
    fraction = min(1, max(0, sum(a*b for a, b in zip(offset, line))/length2)) if length2 else 0
    return math.sqrt(sum((p-(a+fraction*d))**2 for p, a, d in zip(point, start, line)))

def fitness(sequence, mission):
    if sequence.status not in ('complete', 'time_limit', 'nonfinite'):
        raise ValueError('invalid generator status')
    rapid, deviation, min_speed = 0.0, 0.0, math.inf
    for row in sequence.rows:
        if len(row) not in (11,13) or int(row[1]) != row[1] or not 1 <= row[1] < len(mission):
            raise ValueError('invalid setpoint row or target segment')
        if not all(math.isfinite(x) for x in row):
            if sequence.status != 'nonfinite':
                raise ValueError('nonfinite sample without failure status')
            continue
        target = int(row[1])
        rapid = max(rapid, abs(row[10]))
        deviation = max(deviation, segment_distance(row[2:5], mission[target-1], mission[target]))
        min_speed = min(min_speed, math.sqrt(sum(v*v for v in row[5:8])))
    if sequence.status == 'complete' and not sequence.rows:
        # Coincident accepted waypoints require no motion and are not a fault.
        interruption = 0.0
    else:
        interruption = math.inf if sequence.status != 'complete' or min_speed == 0 else 1/min_speed
    return {'rapid': rapid, 'deviation': deviation, 'interruption': interruption}
