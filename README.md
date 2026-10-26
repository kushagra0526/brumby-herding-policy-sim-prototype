# herdsim: which drone policy gets a herd to the gate?

Brumby's drones "fly to a paddock, position themselves around the mob, and move them where they need to go", replacing helicopters, motorbikes and horses (https://www.ycombinator.com/companies/brumby). How the drone positions itself and when it goes back for strays decides time, battery and how hard the animals are pushed. This prototype compares three simple policies in the published sheepdog model (Strömbom et al., J. R. Soc. Interface 2014) with cattle-ish settings. It is a model of collective motion, not of Brumby's system or of real cattle.

## The setup
`herdsim/sim.py`: animals graze at random until the drone is within 65 m, then each flees the drone, is attracted to the centre of its 20 nearest neighbours, keeps a 2 m gap, and carries inertia and noise; the drone moves at a fixed speed (1.5 m/step vs 1 m/step for animals in dev) plus wind noise. Policies:
- **close tail-chase:** sit 5 m behind the herd centre, relative to the target.
- **drive only:** stay r_a sqrt(N) behind the herd centre (the model's driving distance).
- **collect then drive:** if any animal is farther from the centre than r_a N^(2/3), go behind the farthest one to collect it; otherwise drive.
Success = herd centre within 25 m of the gate (150 m away) in the step limit. Strays = animals more than 62 m from the gate at the end. Path = drone distance flown. Pressure = share of animals within 65 m of the drone, averaged over steps.

## Results (12 herds per split)
Dev: 40 animals, drone 1.5 m/step, no wind, 2,500 steps. Held-out (seeds 1000-1011, fixed in git before the first run): 80 animals, drone 1.2 m/step, wind noise 0.4, 3,000 steps.

| | dev reached | dev median steps | dev strays | dev path (m) | held-out reached | held-out strays | held-out path (m) |
|---|---|---|---|---|---|---|---|
| close tail-chase | 17% | 269 | 33.5 | 547 | 0% | 66.5 | 2,179 |
| drive only | 92% | 249 | 5.9 | 256 | 33% | 50.2 | 1,547 |
| collect then drive | **100%** | 485 | **0.0** | 659 | 8% | 73.7 | 3,521 |

- Dev: tail-chasing scatters the herd (17% reach the gate); driving from the model's standoff distance is fast and cheap (249 steps, 256 m flown) but loses a few animals (5.9 strays); collect-then-drive brings everyone (0 strays) at about twice the time and 2.6x the flight distance.
- **Held-out: nothing works well.** With 80 animals every policy loses most of the herd (50-74 strays), and collect-then-drive, the best in dev, reaches the gate in 1 of 12 herds.
- What-if added after the run (`whatif.py`, 8 other herds at 80 animals, wind 0.4): drone speeds 1.2 / 1.5 / 2.0 m/step give drive-only 0 / 25 / 12% and collect-then-drive 0 / 0 / 0%; with no wind (4 herds, 1.5 m/step) drive-only reached 1 of 4. So speed and wind are not the cause. I suspect the model's local attraction (20 nearest animals) lets 80 animals split into several clumps that a single drone cannot re-merge, but I did not investigate or tune further.

## Read this before believing the table
The model was published for sheep and one dog; cattle, terrain, fences, water points, drone battery and wind are not in it, and the parameters here are not calibrated to anything. The held-out result is a limit of this model and these settings, not a finding about real herds. Nothing here uses Brumby data or systems.

## Run it (3 commands)
```
pip install numpy pytest
python -m pytest -q tests
python -m herdsim.run
```
numpy only. 3 tests (the run takes about 3 minutes).

Unofficial prototype by Kushagra Pratap Singh. Not affiliated with Brumby.
