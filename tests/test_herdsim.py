import numpy as np

from herdsim import sim


def test_animals_flee_from_a_close_drone_and_graze_when_it_is_far():
    rng = np.random.default_rng(0)
    P = sim.init(rng, 20)
    H = np.zeros_like(P)
    far = np.array([5000.0, 0.0])
    P2, _, thr = sim.animal_step(P, H, far, rng, sim.PARAMS)
    assert not thr.any() and np.linalg.norm(P2 - P, axis=1).max() <= 1.0 + 1e-9
    near = P.mean(0) + np.array([-40.0, 0.0])
    P3, _, thr = sim.animal_step(P, H, near, rng, sim.PARAMS)
    assert thr.mean() > 0.5 and P3[:, 0].mean() > P[:, 0].mean()


def test_collect_targets_the_farthest_animal_and_drive_targets_behind_the_centre():
    P = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [90.0, 0.0]])
    t = sim.dog_target("collect then drive", P, np.array([-50.0, 0.0]), np.array([200.0, 0.0]), sim.PARAMS)
    assert t[0] > 90                                   # beyond the stray, on the far side from the herd
    P2 = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    t2 = sim.dog_target("collect then drive", P2, np.array([-50.0, 0.0]), np.array([200.0, 0.0]), sim.PARAMS)
    assert t2[0] < P2[:, 0].min()                      # drive: behind the centre relative to the goal


def test_run_is_reproducible():
    assert sim.run("collect then drive", 20, 3, T=400) == sim.run("collect then drive", 20, 3, T=400)
