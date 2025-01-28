from typing import Optional

from pymoo.core.algorithm import LoopwiseAlgorithm
from pymoo.core.sampling import Sampling


class RandomSamplingAlgorithm(LoopwiseAlgorithm):
    sampling: Optional[Sampling]
    batch_size: int
    n_sample_points: int
    def __init__(self, sampling: Optional[Sampling], n_sample_points: int, batch_size: int = -1, **kwargs):
        super().__init__(**kwargs)
        self.sampling = sampling
        self.n_sample_points = n_sample_points
        self.batch_size = batch_size if batch_size != -1 else n_sample_points


    def _next(self):
        return self

    def send(self, _infill):
        gen_size: int = min(self.batch_size, self.n_sample_points)
        self.n_sample_points -= gen_size
        if gen_size == 0:
            raise StopIteration()
        return self.sampling.do(self.problem, gen_size)