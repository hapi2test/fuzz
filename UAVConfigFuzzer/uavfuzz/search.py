from dataclasses import dataclass, asdict
import random
from .model import fitness

@dataclass
class Trial:
    stage: str
    target: str
    correlated: str | None
    iteration: int
    config: dict
    scores: dict
    status: str

class Search:
    def __init__(self, generator, defaults, mission, n=100, k=5, iterations=200, seed=0, sink=None):
        if n < 1 or k < 1 or k > n or iterations < 1:
            raise ValueError('require N >= K >= 1, iterations >= 1')
        self.generator, self.defaults, self.mission = generator, defaults, mission
        self.n, self.k, self.iterations = n, k, iterations
        self.rng, self.sink = random.Random(seed), sink

    def evaluate(self, stage, target, correlated, iteration, config):
        sequence = self.generator.run(config, self.mission)
        trial = Trial(stage, target, correlated, iteration, config,
                      fitness(sequence, self.mission), sequence.status)
        if self.sink:
            self.sink(asdict(trial))
        return trial

    def run(self, domains, objective, pairs=None):
        """N tests per target/round for 1-D; 3N per directed pair for n-D.

        Every candidate is retained by the sink. Top K determines only seed
        selection, never the anomaly cutoff. Infrastructure errors propagate.
        """
        if objective not in ('rapid', 'deviation', 'interruption'):
            raise ValueError('unknown objective')
        if pairs is None:
            targets = [(target, None) for target in domains]
        else:
            targets = [(target, related) for target, related in pairs
                       if domains[target].intervals and domains[related].intervals]
        best = []
        for target, related in targets:
            domain = domains[target]
            if not domain.intervals:
                continue
            seeds = []
            for iteration in range(self.iterations):
                batch = []
                for _ in range(self.n):
                    selected = domain if not seeds else domain.local(self.rng.choice(seeds).config[target])
                    value = selected.sample(self.rng)
                    if related is None:
                        critical = [None]
                    else:
                        ticks = domains[related].ticks()
                        critical = [domains[related].value(ticks[0][0]),
                                    domains[related].value(ticks[-1][1]), self.defaults[related]]
                    for correlated_value in critical:
                        config = self.defaults.copy()
                        config[target] = value
                        if related:
                            config[related] = correlated_value
                        batch.append(self.evaluate('nd' if related else '1d', target, related, iteration, config))
                def rank(trial):
                    return (trial.scores[objective], trial.status != 'complete')
                seeds = sorted(seeds+batch, key=rank, reverse=True)[:self.k]
            best.extend(seeds)
        return sorted(best, key=lambda trial:trial.scores[objective], reverse=True)
