# Rules for agents working in 1_offcenter_zoom (all clusters)

Durable working rules from the user, carried over from `~/0_feedback/doc/agent_rules.md` (same user, same clusters) and extended for this
project. Agents on every cluster (Orion, Bridges-2) follow them. `CLAUDE.md` points here. Add new rules here, not only to machine-local memory.

## Git
- **Never push without asking**, including creating or deleting remote branches. Commit locally, report the commit and ask "push?".
  This overrides the global "commit and push automatically" rule. (User correction in 0_feedback, 2026-09-26.) Exception: the user
  explicitly asked for the initial sharing of this repo to Bridges (2026-10-03).
- **No Claude attribution in commits**: no `Co-Authored-By: Claude` trailer. Short one-line subject, body only when needed. Terse code comments.
- `~/arepo`: commit directly on `BHspin_feedback_NC`, no feature branches. Never stage unrelated uncommitted changes. This project needs
  **no code change** (all flags exist, see `doc/setup_notes.md` S1); do not touch `~/arepo` without asking.
- Session start: `git pull --rebase` here; check `~/arepo` is at/after a71e393f83 on `BHspin_feedback_NC`.

## Runs
- **Ask when uncertain; don't assume.** Physics/numerics parameters, Config flags, run scope (walltime, chains, node counts), output cadence,
  layout and naming. Survey the files first, then batch the open choices into one question with a recommended option. Routine mechanics
  (script bugs, file names inside scratch) need no question. The current open decisions are listed in `PROGRESS.md`.
- **Never generate ICs.** The user copies them from `/virgotng/mpa/LtU/ICs/FlagshipZoomICs/` (Orion) into `~/scratch1/MultiZoomICs/` on the
  run cluster. If an IC is missing, say which file and stop. (User, 2026-10-03.)
- Baseline physics = **fiducial TNG** as in the 0_feedback zoom template (`~/0_feedback/1-hybrid/M0_tng/tng_zoom_H16_Zf2`), Mpc/h units.
  Never `BH_TLA_*` / `BH_TORQUE_LIMITED_ACCRETION`. Only the seeding threshold, seed/dynamical masses and the BH-dynamics flags differ here;
  do not silently restore stock TNG seeding values (plan S2) and do not add untested flags without asking.
- **A run starts and finishes on one cluster** (`Cluster` column in `doc/run_status.md`). Only an agent on that cluster changes its state and
  records it there in the same session. The first-round runs are planned for **Bridges-2** (Orion quota full, user 2026-10-03).
- Create run dirs with `scripts/make_run.py` from `runs/templates/zf4_tde`; `--set` values come from `doc/run_manifest.json`. Diff every
  variant against its `fid` (`diff runs/ZF4_L/fid/param.txt runs/ZF4_L/dyn12/param.txt` must show only the intended line).
- Runs compared one-to-one (fid / dyn12 / seed50 of one bin) must share the cluster and MPI layout (0_feedback: a different task count gives a
  different realisation from z~9 on).
- Unexpected science outcomes are not grounds to reselect halos or retune (plan S5); numerical failures are diagnosed and versioned.

## Bookkeeping
- `doc/run_status.md` = state (one row per manifest label; never delete a row, mark `cancelled`), `PROGRESS.md` = narrative (what worked,
  failed, next; failed approaches recorded so they are not retried). Update both in the same session as any state change.
- Tests first for any new script (`scripts/test_<name>.py`; <=5 lines on success, verbose output to `test_logs/`). Run
  `for t in scripts/test_*.py; do python3 $t; done` before committing.
- Analysis later goes in `analysis/` (reuse `~/zoom_utils` and the 0_feedback `hyb` patterns; the zoom_utils readers need multi-file snapshot
  support). Exploratory plots are never deleted: `scratch_*.py` -> `scratch_plots/`.
