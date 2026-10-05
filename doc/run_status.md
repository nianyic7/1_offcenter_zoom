# Run status

Single source of truth for the state of every planned run. Update on every state change (`doc/workflow.md`, `doc/agent_rules.md`).
Refresh the Progress column with `python3 scripts/run_status.py` on the run's cluster.

Cluster column: `orion` (MPCDF) or `bridges` (PSC Bridges-2); a run starts and finishes on one cluster and only an agent on that cluster
changes its state. First-round runs are planned for **bridges** (Orion quota full, 2026-10-03).

Status vocabulary: `planned` (no config yet) · `configured` (config dir ready, not submitted) · `queued` · `running` · `paused` (stopped
cleanly, needs restart) · `done` (z=0) · `failed` · `cancelled`. Labels are the plan's run labels; dirs are `runs/<set>/<variant>`.

Common to all rows: template `runs/templates/zf4_tde` (fiducial TNG + BH_DF_DISCRETE family, `doc/setup_notes.md`), physical seed
`SeedBlackHoleMass 5e-5` (5e5 Msun/h), `MinDistanceForMergingBlackHoles 2` (0.8 kpc/h comoving), softening 0.4 kpc/h comoving at all z (max-phys 0.4, no cap), outputs z=6, 4 then every
100 Myr from z=3 (120 snapshots), ZF4 ICs with m_DM,hr = 2.08e-4. Nodes (decided 2026-10-05): ZF4_L 8, ZF4_H 12 (Bridges: 512 / 768 tasks).
Code: `~/arepo` a71e393f83 (`BHspin_feedback_NC`, clean tree); one binary built in `runs/ZF4_L/fid` (md5 d5817522...) and copied to the other
five dirs (identical `Config.sh`). `MaxMemSize 3200`. `OUTPUT_HOST_PROPERTIES_FOR_BH_MERGERS` off.

## ZF4_L — IC `ics_targethalos_LtU_L500_M12.75-13.00_H5_Zf4_000` (5 targets, FoF mass 10^12.75–13.00 Msun at z=0)

| Label | Required | Setting (DynamicalSeedBlackHoleMass / MinFoFMassForNewSeed) | Dir | Cluster | Status | Jobs | Progress | Notes |
|---|---|---|---|---|---|---|---|---|
| TDE_ZF4_L_FID | yes | 6e-4 (6e6 Msun/h) / 1.0 (1e10 Msun/h) | `runs/ZF4_L/fid` | bridges | queued | 47426651 `run.sh` (submitted 2026-10-04 23:53 EDT, 8 nodes x 64, 48 h) | | Reference for the L bin. First job = validation segment (workflow §2.5). One 48 h job, no restart chain queued. |
| TDE_ZF4_L_DYN12 | yes | 1.2e-3 (1.2e7 Msun/h) / 1.0 | `runs/ZF4_L/dyn12` | bridges | queued | 47426652 `run.sh` (submitted 2026-10-04 23:53 EDT, 8 nodes x 64, 48 h) | | Tests dynamical mass at fixed seeding. Same layout as L_FID. One 48 h job, no restart chain queued. |
| TDE_ZF4_L_SEED50 | yes | 6e-4 / 5.0 (5e10 Msun/h = TNG stock) | `runs/ZF4_L/seed50` | bridges | queued | 47426653 `run.sh` (submitted 2026-10-04 23:53 EDT, 8 nodes x 64, 48 h) | | Tests delayed/reduced seeding. Same layout as L_FID. One 48 h job, no restart chain queued. |
| TDE_ZF4_L_X | optional | 1.2e-3 / 5.0 | `runs/ZF4_L/x` (proposed) | | planned | | | Crossed case (plan §6); only if resources permit. |

## ZF4_H — IC `ics_targethalos_LtU_L500_M13.00-13.25_H5_Zf4_000` (5 targets, FoF mass 10^13.00–13.25 Msun at z=0)

| Label | Required | Setting (DynamicalSeedBlackHoleMass / MinFoFMassForNewSeed) | Dir | Cluster | Status | Jobs | Progress | Notes |
|---|---|---|---|---|---|---|---|---|
| TDE_ZF4_H_FID | yes | 6e-4 / 1.0 | `runs/ZF4_H/fid` | bridges | queued | 47426654 `run.sh` (submitted 2026-10-04 23:53 EDT, 12 nodes x 64, 48 h) | | Reference for the H bin; `--set InitCondFile=...M13.00-13.25...`. One 48 h job, no restart chain queued. |
| TDE_ZF4_H_DYN12 | yes | 1.2e-3 / 1.0 | `runs/ZF4_H/dyn12` | bridges | queued | 47426655 `run.sh` (submitted 2026-10-04 23:53 EDT, 12 nodes x 64, 48 h) | | One 48 h job, no restart chain queued. |
| TDE_ZF4_H_SEED50 | yes | 6e-4 / 5.0 | `runs/ZF4_H/seed50` | bridges | queued | 47426656 `run.sh` (submitted 2026-10-04 23:53 EDT, 12 nodes x 64, 48 h) | | One 48 h job, no restart chain queued. |
| TDE_ZF4_H_X | optional | 1.2e-3 / 5.0 | `runs/ZF4_H/x` (proposed) | | planned | | | Crossed case (plan §6). |

## Deferred (plan §6)
- ZF8 convergence: two matched halos, one per bin — not before the force/mass convention is fixed.
- Nucleus assignment, TDE-rate modelling, survey selection, field controls, wider mass coverage.
