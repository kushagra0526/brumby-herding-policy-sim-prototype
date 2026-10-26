"""A herd and one herding drone, after the sheepdog model of Stromborn et al. (J. R. Soc. Interface 2014), with cattle-ish settings.

Animals graze at random until the drone comes within r_s; then each moves away from the drone, stays close to its neighbours (attraction
to the local centre), keeps a small gap from them, and carries inertia and noise. The drone moves at a fixed speed and chooses where to
go by a policy. Units are metres and steps; all numbers are illustrative, not cattle data.
"""
import numpy as np

PARAMS = dict(r_a=2.0, r_s=65.0, w_rep=2.0, w_att=1.05, w_dog=1.0, w_inertia=0.5, noise=0.3, step=1.0, graze=0.05, n_att=20)


def init(rng, N, spread=30.0):
    return rng.normal(0, spread, (N, 2)) + np.array([0.0, 0.0])


def animal_step(P, H, dog, rng, prm):
    N = len(P)
    d_dog = np.linalg.norm(P - dog, axis=1)
    threatened = d_dog < prm["r_s"]
    D = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2) + np.eye(N) * 1e9
    nn = np.argsort(D, axis=1)[:, :prm["n_att"]]
    com = P[nn].mean(1)
    A = com - P
    A /= np.linalg.norm(A, axis=1, keepdims=True) + 1e-9
    close = D < prm["r_a"]
    R = (P[:, None, :] - P[None, :, :]) * close[:, :, None]
    R = R.sum(1)
    R /= np.linalg.norm(R, axis=1, keepdims=True) + 1e-9
    S = P - dog
    S /= np.linalg.norm(S, axis=1, keepdims=True) + 1e-9
    noise = rng.normal(0, 1, P.shape)
    heading = prm["w_inertia"] * H + prm["w_att"] * A + prm["w_rep"] * R + prm["w_dog"] * S + prm["noise"] * noise
    heading /= np.linalg.norm(heading, axis=1, keepdims=True) + 1e-9
    move = np.zeros_like(P)
    move[threatened] = heading[threatened] * prm["step"]
    graze = ~threatened & (rng.random(N) < prm["graze"])
    g = rng.normal(0, 1, (graze.sum(), 2))
    move[graze] = g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-9) * prm["step"]
    H2 = np.where(threatened[:, None], heading, H)
    return P + move, H2, threatened


def dog_target(policy, P, dog, goal, prm):
    N = len(P)
    gcm = P.mean(0)
    far = np.linalg.norm(P - gcm, axis=1)
    f_n = prm["r_a"] * N ** (2 / 3)                  # a herd is "together" if everyone is within this of the centre
    to_goal = goal - gcm
    to_goal /= np.linalg.norm(to_goal) + 1e-9
    if policy == "close tail-chase":
        return gcm - to_goal * 5.0                    # sit right behind the herd and push
    behind = gcm - to_goal * prm["r_a"] * np.sqrt(N)
    if policy == "drive only":
        return behind
    if far.max() > f_n:                               # collect: go behind the farthest animal, relative to the centre
        i = int(np.argmax(far))
        v = P[i] - gcm
        return P[i] + v / (np.linalg.norm(v) + 1e-9) * prm["r_a"]
    return behind


def run(policy, N, seed, goal=(150.0, 0.0), radius=25.0, T=2500, dog_speed=1.5, wind=0.0, prm=PARAMS):
    rng = np.random.default_rng(seed)
    P = init(rng, N)
    H = np.zeros_like(P)
    dog = np.array([-80.0, 0.0])
    goal = np.array(goal)
    path, stress = 0.0, 0.0
    for t in range(T):
        P, H, thr = animal_step(P, H, dog, rng, prm)
        tgt = dog_target(policy, P, dog, goal, prm)
        v = tgt - dog
        dist = np.linalg.norm(v)
        move = v / (dist + 1e-9) * min(dog_speed, dist)
        move = move + rng.normal(0, wind, 2)
        dog = dog + move
        path += float(np.linalg.norm(move))
        stress += float(thr.mean())
        gcm = P.mean(0)
        if np.linalg.norm(gcm - goal) < radius:
            stray = int((np.linalg.norm(P - goal, axis=1) > 2.5 * radius).sum())
            return {"done": True, "steps": t, "strays": stray, "path": path, "stress": stress / (t + 1)}
    stray = int((np.linalg.norm(P - goal, axis=1) > 2.5 * radius).sum())
    return {"done": False, "steps": T, "strays": stray, "path": path, "stress": stress / T}
