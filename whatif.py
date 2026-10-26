"""What-if added after the held-out run: how fast must the drone be (relative to the animals' 1 m/step) for each policy to work on a herd of 80?"""
import numpy as np

from herdsim import sim

print("drone speed | policy | reached target % | mean strays | mean path (m)   [N=80, wind 0.4, 8 herds, T=3000]")
for speed in (1.2, 1.5, 2.0):
    for p in ("drive only", "collect then drive"):
        rs = [sim.run(p, 80, s, dog_speed=speed, wind=0.4, T=3000) for s in range(2000, 2008)]
        print(f"{speed} | {p} | {100 * np.mean([r['done'] for r in rs]):.0f} | {np.mean([r['strays'] for r in rs]):.1f} | {np.mean([r['path'] for r in rs]):.0f}", flush=True)
