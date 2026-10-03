# 1_offcenter_zoom — off-nuclear BHs and TDEs in multizoom simulations

Planning/launch/analysis directory for AREPO zoom runs on off-centre (wandering, stripped-satellite) black holes and the TDE host population.
Plan: `doc/off_nuclear_tde_first_round_runs.md` (2026-10-03: six ZF4 multizooms, two IC sets x {FID, DYN12, SEED50}). Resolved facts and
open decisions: `doc/setup_notes.md`, `PROGRESS.md`. Set-up mirrors `~/0_feedback` (same user, clusters, code, scripts); read its
`CLAUDE.md`/`doc/workflow.md` for details not repeated here.

**Agent rules (all clusters): read `doc/agent_rules.md` first.** Never push without asking; no Claude attribution in commits; never generate
ICs (the user copies them from `/virgotng/mpa/LtU/ICs/FlagshipZoomICs/`); ask before changing physics/numerics/scope.

## Clusters
- Orion (MPCDF, home `/u/nianyic`) and Bridges-2 (PSC, home `/jet/home/nianyic`): same GitHub repo, same layout under `~`, `~/scratch1` = scratch
  (Bridges: symlink to the `/ocean` project dir), same `~/arepo` (`BHspin_feedback_NC`, >= a71e393f83; Bridges `~/arepo -> ~/arepo_my`).
  Per-cluster settings: `scripts/clusters.py` (detected from `$HOME`, override `$OFFCENTER_CLUSTER`); `scripts/make_run.py --cluster/--nodes`.
  A run lives on one cluster from start to finish (`Cluster` column in `doc/run_status.md`). **First-round runs go to Bridges-2** (Orion quota full).
- Bridges-2: RM, account phy240015p, 64 tasks/node (MaxMemSize 3600), 48 h (TimeLimitCPU 190000 -> Arepo stops at 44.9 h), `~/arepo/modules_br2.sh`,
  low fairshare (long queue waits), home quota ~full (25 GiB), `lfs quota -p 554803 /ocean`. Orion: p.exclusive, 112 tasks/node, 23 h, 30-node/6-job cap.

## Layout
- `doc/` — plan, `agent_rules.md`, `workflow.md` (configure/launch/restart/monitor), `setup_notes.md` (code facts: flags, units, ICs, softenings),
  `run_manifest.json` (machine-readable six-run manifest: per-run `--set` values), `run_status.md` (state table, one row per run label).
- `runs/templates/zf4_tde/` — the run template (fiducial TNG zoom config + BH dynamics flags, ZF4 softening ladder, FID seeding values). Never submit it.
- `runs/<set>/<variant>/` — one config dir per run: `ZF4_L/{fid,dyn12,seed50[,x]}`, `ZF4_H/{...}` (`Config.sh`, `param.txt`, `outputs.txt`,
  `compile.sh`, `run.sh`, `restart.sh`, built `Arepo`). Output goes to the scratch mirror `~/scratch1/1_offcenter_zoom/runs/<set>/<variant>/`.
- `scripts/` — `make_run.py` (derive a run dir from the template; applies cluster settings), `run_status.py` (state of runs on this cluster),
  `clusters.py`, `units.py`, `test_*.py`. `test_logs/` — verbose test output (gitignored).
- `analysis/` (to come) — BH orbit/host tracking, satellite stripping, TDE-host statistics; reuse `~/zoom_utils` (`/orion/u/nianyic/zoom_utils`) and the
  0_feedback `1-hybrid/scripts/hyb` caching patterns. Snapshots are 8-file; zoom_utils single-file readers need multi-file support.
- Git remote: `origin` = git@github.com:nianyic7/1_offcenter_zoom.git (private, `main`). Pull (`git pull --rebase`) at session start.

## Conventions
- Units: Mpc/h, 1e10 Msun/h, km/s (as 0_feedback and the zoom ICs). Param masses are code units: `SeedBlackHoleMass 3.387e-5` (5e5 Msun),
  `DynamicalSeedBlackHoleMass 4.0644e-4` (6e6 Msun) / `8.1288e-4` (1.2e7), `MinFoFMassForNewSeed 1.0` (1e10 Msun/h) / `5.0` (5e10 = TNG stock).
  The "physical Msun" reading of the seed masses is provisional (`doc/setup_notes.md` S2) — settle before launch.
- Physics = fiducial TNG (0_feedback zoom template) + `BH_DF_DISCRETE`, `HIGHER_DYNAMICAL_SEED_MASS`, `MERGE_BHS_WITHIN_GAS_SOFTENING`,
  `RELATIVE_VELOCITY_CRITERION_FOR_MERGERS`, `OUTPUT_BLACKHOLE_KINEMATICS`; `BH_NEW_CENTERING` off; `REDUCE_DFD_WITH_BH_GROWTH` off; spin tracking only.
  No `BH_TLA_*`. All flags exist in `~/arepo`; no code change.
- ZF4 ICs: m_DM,hr = 2.08e-4 (~TNG50-2), z_start 63, 500 Mpc/h parent (MTNG-L500-4320-A), bins are parent **FoF GroupMass**. Softening ladder = TNG50-2
  values (0.00078/0.00039 Mpc/h) for classes 0–2, coarse classes unchanged (proposed, S4). Merge radius = 2 x class-0 softening.
- `blackhole_details_*.txt` = 18 columns (ID, t, M_BH, mdot, rho, cs, pos[3], vel[3], acc[3], DF acc[3]); mergers in `blackhole_mergers/`.

## Workflow (read `doc/workflow.md` before touching any run)
- Session start: `git pull --rebase` -> `PROGRESS.md` -> `doc/run_status.md` -> `python3 scripts/run_status.py`; reconcile the table first.
- New run: `make_run.py` from the template with the manifest's `--set` values, diff against `fid`, compile, pre-flight paths, `sbatch run.sh`,
  verify start-up (READIC counts, 18-column details), record in `doc/run_status.md`. First job = validation segment: record memory/pace, then fix node count.
- Restart: `sbatch restart.sh` (self-chaining until `output/end`).
- Every state change of a run is written to `doc/run_status.md` in the same session; `PROGRESS.md` holds the narrative.
- Tests: `for t in scripts/test_*.py; do python3 $t; done` (<=5 lines each on success).
