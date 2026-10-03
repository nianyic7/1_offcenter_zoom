# PROGRESS

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
### Open decisions (ask the user before configuring the Bridges runs; `doc/setup_notes.md` has the details)
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
