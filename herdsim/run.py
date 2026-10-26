import json

import numpy as np

from . import sim

POLICIES = ["close tail-chase", "drive only", "collect then drive"]
SPLITS = {"dev": dict(seeds=range(0, 12), N=40, dog_speed=1.5, wind=0.0, T=2500),
          "held_out": dict(seeds=range(1000, 1012), N=80, dog_speed=1.2, wind=0.4, T=3000)}


def evaluate(cfg):
    out = {}
    for p in POLICIES:
        rs = [sim.run(p, cfg["N"], s, dog_speed=cfg["dog_speed"], wind=cfg["wind"], T=cfg["T"]) for s in cfg["seeds"]]
        done = [r for r in rs if r["done"]]
        out[p] = {"reached_target_pct": round(100 * len(done) / len(rs)), "median_steps_when_done": int(np.median([r["steps"] for r in done])) if done else None,
                  "mean_strays": round(float(np.mean([r["strays"] for r in rs])), 1), "mean_drone_path_m": int(np.mean([r["path"] for r in rs])),
                  "mean_share_of_animals_pressured": round(float(np.mean([r["stress"] for r in rs])), 2)}
    return out


def main():
    res = {k: evaluate(v) for k, v in SPLITS.items()}
    json.dump(res, open("out/result.json", "w"), indent=1)
    for k, v in res.items():
        print(k)
        for p, d in v.items():
            print("  ", p, d)


if __name__ == "__main__":
    main()
