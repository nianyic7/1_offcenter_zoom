# Run status

Single source of truth for the state of every planned run. Update on every state change (`doc/workflow.md`, `doc/agent_rules.md`).
Refresh the Progress column with `python3 scripts/run_status.py` on the run's cluster.

Cluster column: `orion` (MPCDF) or `bridges` (PSC Bridges-2); a run starts and finishes on one cluster and only an agent on that cluster
changes its state. First-round runs are planned for **bridges** (Orion quota full, 2026-10-03).

Status vocabulary: `planned` (no config yet) · `configured` (config dir ready, not submitted) · `queued` · `running` · `paused` (stopped
cleanly, needs restart) · `done` (z=0) · `failed` · `cancelled`. Labels are the plan's run labels; dirs are `runs/<set>/<variant>`.

Common to all rows: template `runs/templates/zf4_tde` (fiducial TNG + BH_DF_DISCRETE family, `doc/setup_notes.md`), physical seed
`SeedBlackHoleMass 3.387e-5` (5e5 Msun, provisional unit reading), `MinDistanceForMergingBlackHoles 2`, ZF4 ICs with m_DM,hr = 2.08e-4.

## ZF4_L — IC `ics_targethalos_LtU_L500_M12.75-13.00_H5_Zf4_000` (5 targets, FoF mass 10^12.75–13.00 Msun at z=0)

| Label | Required | Setting (DynamicalSeedBlackHoleMass / MinFoFMassForNewSeed) | Dir | Cluster | Status | Jobs | Progress | Notes |
|---|---|---|---|---|---|---|---|---|
| TDE_ZF4_L_FID | yes | 4.0644e-4 (6e6 Msun) / 1.0 (1e10 Msun/h) | `runs/ZF4_L/fid` | bridges | planned | | | Reference for the L bin. First job = validation segment (workflow §2.5). |
| TDE_ZF4_L_DYN12 | yes | 8.1288e-4 (1.2e7 Msun) / 1.0 | `runs/ZF4_L/dyn12` | bridges | planned | | | Tests dynamical mass at fixed seeding. Same layout as L_FID. |
| TDE_ZF4_L_SEED50 | yes | 4.0644e-4 / 5.0 (5e10 Msun/h = TNG stock) | `runs/ZF4_L/seed50` | bridges | planned | | | Tests delayed/reduced seeding. Same layout as L_FID. |
| TDE_ZF4_L_X | optional | 8.1288e-4 / 5.0 | `runs/ZF4_L/x` (proposed) | | planned | | | Crossed case (plan §6); only if resources permit. |

## ZF4_H — IC `ics_targethalos_LtU_L500_M13.00-13.25_H5_Zf4_000` (5 targets, FoF mass 10^13.00–13.25 Msun at z=0)

| Label | Required | Setting (DynamicalSeedBlackHoleMass / MinFoFMassForNewSeed) | Dir | Cluster | Status | Jobs | Progress | Notes |
|---|---|---|---|---|---|---|---|---|
| TDE_ZF4_H_FID | yes | 4.0644e-4 / 1.0 | `runs/ZF4_H/fid` | bridges | planned | | | Reference for the H bin; `--set InitCondFile=...M13.00-13.25...`. |
| TDE_ZF4_H_DYN12 | yes | 8.1288e-4 / 1.0 | `runs/ZF4_H/dyn12` | bridges | planned | | | |
| TDE_ZF4_H_SEED50 | yes | 4.0644e-4 / 5.0 | `runs/ZF4_H/seed50` | bridges | planned | | | |
| TDE_ZF4_H_X | optional | 8.1288e-4 / 5.0 | `runs/ZF4_H/x` (proposed) | | planned | | | Crossed case (plan §6). |

## Deferred (plan §6)
- ZF8 convergence: two matched halos, one per bin — not before the force/mass convention is fixed.
- Nucleus assignment, TDE-rate modelling, survey selection, field controls, wider mass coverage.
