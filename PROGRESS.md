# PROGRESS

## 2026-10-04 (Bridges-2) — six first-round runs configured and submitted
### Done
- Pre-conditions checked: both ZF4 ICs in `~/scratch1/MultiZoomICs/` (headers read: 36837120 / 54058240 type-1, masstab 2.0764e-4, a=0.015625),
  `~/scratch1/TNG_tables`, `~/arepo` at a71e393f83 (clean), tests pass.
- User decisions (2026-10-04): max-phys softening for classes 0/1 = **0.0004** (no physical cap; 0.4 kpc/h comoving at all z);
  `OUTPUT_HOST_PROPERTIES_FOR_BH_MERGERS` **off**; all six started at once; **one 48 h job per run** ("let's try 48 hours"), 8 / 12 nodes.
- `MaxMemSize` 3600 -> **3200** for Bridges (`scripts/clusters.py`, docs, test): 0_feedback zooms were OOM-killed at 3600 after ~39 h
  (cgroup limit 240000 MB/node; user decision there 2026-10-03). The ZF4 runs need far less (~1 GB/task expected).
- Six run dirs made with `make_run.py` from the manifest (`runs/ZF4_{L,H}/{fid,dyn12,seed50}`); each variant differs from its `fid` in exactly
  one param line; stale TimeLimitCPU/MaxMemSize comments corrected by hand. Param key set checked against the running 0_feedback Bridges zoom
  (only `DynamicalSeedBlackHoleMass`, `MinDistanceForMergingBlackHoles` added, `BlackHoleCenteringMassMultiplier` dropped: match the code guards).
- Built once in `runs/ZF4_L/fid` (275 s, five dynamics flags in `arepoconfig.h`, no `BH_NEW_CENTERING`); binary copied to the other five (user:
  compile once for identical Configs). Pre-flight paths OK.
- Submitted 2026-10-04 23:53 EDT: 47426651 L_FID, 47426652 L_DYN12, 47426653 L_SEED50 (8 nodes), 47426654 H_FID, 47426655 H_DYN12,
  47426656 H_SEED50 (12 nodes); all pending. Four 16-node 0_feedback chains (submitted 10-02) are ahead in the same account.
### Failed / notes
- `mpiexec -np 1 ./Arepo` on a login node hangs without output (tried as a param-parse smoke test): do not retry; check params statically.
- `pkill -f <pattern>` from the agent shell kills the shell itself (pattern is in its own command line): kill by PID.
### Next
- Do not edit `param.txt`/`Config.sh`/`Arepo` in the six run dirs while jobs are pending: `run.sh` copies them at job start.
- When jobs start (queue wait was ~62 h for 16-node jobs on 10-02): verify start-up within ~5 min (workflow §2.5: READIC 36837120 / 54058240,
  masstab 0.00020764, no `not found`/`Terminate`, `Sync-Point 1`), then memory (`memory.txt`), pace, 18-column `blackhole_details`. Set the rows
  to `running` in `doc/run_status.md`. After the job: `sacct -j <job> -o JobID,State,MaxRSS` (OOM shows as COMPLETED), record z reached, pace
  and peak memory; ask the user whether to chain `restart.sh` (not queued: this round is a 48 h trial).
- Storage: `/ocean` project 91.1 of 102.5 TB used (11.4 TB free) on 10-04. Enough for the 48 h segments (restart sets + few snapshots, ~2 TB),
  not for six runs to z=0 (7–11 TB snapshots + restart sets) next to the 0_feedback zooms: raise with the user before chaining.
- Commit is local only: ask the user before pushing.

## 2026-10-05 (Orion) — decisions applied
### Done
- User pushed `main` to https://github.com/nianyic7/1_offcenter_zoom (the agent's push was blocked by the permission classifier; ask the user to push).
- Decisions from the user applied to template, manifest, run_status, setup_notes, CLAUDE.md, workflow (`doc/setup_notes.md` S2/S4/S5/S6):
  1. Seed masses are Msun/h: `SeedBlackHoleMass 5e-5`, `DynamicalSeedBlackHoleMass 6e-4` (FID) / `1.2e-3` (DYN12). Thresholds unchanged (1.0 / 5.0).
  2. Softening 0.4 kpc/h comoving for gas/high-res DM/stars/BH (`0.0004`); max-phys `0.0002` for classes 0/1 **assumed** (TNG factor 2).
  3. Outputs every 100 Myr from z=3 (+ z=6, 4): 120 snapshots (`runs/templates/zf4_tde/outputs.txt`, Planck15 t(a)); ~1.2–1.8 TB per run.
  4. Nodes: ZF4_L 8, ZF4_H 12 (template `-N 8`; `--nodes 12` for H).
- Tests updated and passing.
### Still open (all three settled 2026-10-04 on Bridges, see above)
- Max-phys softening for classes 0/1: 0.0002 (assumed) or 0.0004 (no extra physical cap).
- Whether to add `OUTPUT_HOST_PROPERTIES_FOR_BH_MERGERS` (host masses in the merger log; untested here).
- Start order: both FID runs first as validation segments, or all six at once.
### Next (Bridges-2 agent)
- `git clone git@github.com:nianyic7/1_offcenter_zoom.git ~/1_offcenter_zoom`; read `CLAUDE.md`, `doc/agent_rules.md`, `doc/workflow.md`, this file.
- Pre-conditions (workflow §2.0): both ZF4 ICs in `~/scratch1/MultiZoomICs/` (user transfers; Bridges cannot see `/virgotng`), `~/scratch1/TNG_tables`,
  `~/arepo` >= a71e393f83, `python3 scripts/test_clusters.py`, `lfs quota -p 554803 /ocean` (120 snapshots x 6 runs ~ 7–11 TB + restart sets).
- Make the six run dirs with `make_run.py --cluster bridges --nodes 8|12` and the manifest `--set` values, diff each against its `fid`, compile,
  pre-flight, submit, verify start-up (READIC 36837120 / 54058240, masstab 0.00020764, 18-column details), record in `doc/run_status.md`.

## 2026-10-03 (Orion) — repo initialised
### Done
- Repo created from the 0_feedback pattern: `CLAUDE.md`, `doc/{agent_rules,workflow,setup_notes,run_status}.md`, `doc/run_manifest.json`,
  `scripts/` (clusters/make_run/run_status/units + 4 tests, all passing), `runs/templates/zf4_tde/`, `.gitignore`.
- Checked in `~/arepo` (a71e393f83): all five BH-dynamics flags of the plan exist and need no code change; `BH_NEW_CENTERING` must be off with
  `BH_DF_DISCRETE`. Parameter names/units resolved (`doc/setup_notes.md` S1–S2): `DynamicalSeedBlackHoleMass`, `MinDistanceForMergingBlackHoles`
  (x softening class 0), `MinFoFMassForNewSeed` (FoF DM mass vs Omega_dm/Omega_m x value; 1e10 Msun/h = 1.0, TNG stock 5.0).
- ICs: both needed ZF4 H5 files exist in `/virgotng/mpa/LtU/ICs/FlagshipZoomICs/` (user copies them; **never generate ICs**). m_DM,hr = 2.0764e-4
  code = 3.07e6 Msun; L: 36.8M high-res DM, H: 54.1M (+ ~17M coarse each; gas generated at start-up).
- Template: 0_feedback zoom template + dynamics flags, FID seeding values (physical-Msun reading), TNG50-2 softening ladder (proposal), `-N 4`.
- Orion quota is full: no runs here. Target cluster = Bridges-2.
### Failed / not done
- GitHub remote not created: no `gh` CLI or token on Orion (SSH to GitHub works). Remote `origin` is set to
  `git@github.com:nianyic7/1_offcenter_zoom.git`; the user creates the private repo and pushes `main` (or asks the agent to push).
### Open decisions at the time (settled 2026-10-05, see above)
1. **Seed-mass units**: 5e5 / 6e6 / 1.2e7 as physical Msun (template: 3.387e-5 / 4.0644e-4 / 8.1288e-4; 6e6 = 1.96 m_DM) or Msun/h
   (5e-5 / 6e-4 / 1.2e-3; 6e6 = 2.89 m_DM), or set the fiducial to exactly 3 m_DM (6.229e-4). Recommended: Msun/h reading (matches the plan's
   "~3 m_DM" and bhspin usage) — but it is the user's call. Regenerate `run_manifest.json`, template and `run_status.md` values accordingly.
2. **Softening ladder** for ZF4 (S4): proposed TNG50-2 values 0.00078/0.00039 (classes 0/1), BH 0.00078, `MinimumComovingHydroSoftening 0.0001`.
3. **Output cadence** (S5): 50 Myr full snapshots at z<=3 = ~233 snapshots ≈ 2–3.5 TB per run; alternatives: 100–200 Myr, or mini-snapshots if
   supported. Template keeps the 11-snapshot 0_feedback list until decided. Also whether to add `OUTPUT_HOST_PROPERTIES_FOR_BH_MERGERS`.
4. **Node count / layout** on Bridges (S6): proposal 4 nodes (L) and 6 nodes (H) x 64 tasks; measure in the first job. All three variants of a bin on
   the same layout.
5. Start the two FID runs first as validation segments, or all six at once (plan allows variants to start before FID finishes).
### Next (Bridges-2 agent)
- `git clone git@github.com:nianyic7/1_offcenter_zoom.git ~/1_offcenter_zoom` (after the user created the repo and pushed); read `CLAUDE.md`,
  `doc/agent_rules.md`, `doc/workflow.md`, this file.
- Check pre-conditions (workflow §2.0): `~/scratch1/MultiZoomICs/` has both ZF4 files (user transfers them; Bridges cannot see `/virgotng`),
  `~/scratch1/TNG_tables`, `~/arepo` at >= a71e393f83, `python3 scripts/test_clusters.py`, `/ocean` free space (`lfs quota -p 554803 /ocean`).
- Settle the open decisions above with the user in one batched question, update template/manifest/status, then make the six run dirs with
  `make_run.py --cluster bridges`, diff each against its `fid`, compile, pre-flight, submit, verify start-up, record.
