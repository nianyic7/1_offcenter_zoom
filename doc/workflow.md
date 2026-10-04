# Run workflow for the off-nuclear TDE zooms

How to configure, launch, restart, monitor and record a run. Plan: `doc/off_nuclear_tde_first_round_runs.md`. Resolved facts and open
decisions: `doc/setup_notes.md`, `PROGRESS.md`. Run inventory: `doc/run_status.md` (keep current). Rules: `doc/agent_rules.md`.
This mirrors `~/0_feedback/doc/workflow.md`; read that for more detail on any step (same clusters, same code, same restart mechanics).

## 1. Where things are

| What | Path |
|---|---|
| Config dirs (one per run) | `runs/<set>/<variant>/` — sets `ZF4_L` ([12.75,13.00) bin) and `ZF4_H` ([13.00,13.25)); variants `fid`, `dyn12`, `seed50`, optional `x` |
| Template | `runs/templates/zf4_tde/` (Config.sh, param.txt, outputs.txt, compile.sh, run.sh, restart.sh) — never submit it |
| Run output (scratch mirror) | `~/scratch1/1_offcenter_zoom/runs/<set>/<variant>/` (same relative path as the config dir) |
| Manifest (per-run `--set` values) | `doc/run_manifest.json` |
| ICs | `~/scratch1/MultiZoomICs/ics_targethalos_LtU_L500_M12.75-13.00_H5_Zf4_000.hdf5` (L), `..._M13.00-13.25_H5_Zf4_000.hdf5` (H); copied by the user from `/virgotng/mpa/LtU/ICs/FlagshipZoomICs/` |
| Code | `~/arepo`, branch `BHspin_feedback_NC` (>= a71e393f83); Bridges: `~/arepo -> ~/arepo_my` |
| Module script | Orion `~/arepo/load_modules.sh`; Bridges `~/arepo/modules_br2.sh` (set per cluster by `scripts/clusters.py`) |
| TNG tables | `~/scratch1/TNG_tables/` (present on both clusters from 0_feedback) |
| Helpers + tests | `scripts/` (`make_run.py`, `run_status.py`, `clusters.py`, `units.py`, `test_*.py`); `test_logs/` |

A config dir contains the six template files plus the built `Arepo`, `build/`, `compile.log`, `slurm-*.out`. `run.sh` copies param/outputs/Config/Arepo
into the scratch mirror and runs there, so the mirror is self-describing.

## 2. Starting a run

0. **Pre-conditions** (first time on a cluster): `git pull --rebase`; `~/scratch1` exists (Bridges: symlink to the project `/ocean` dir);
   both IC files present; `~/scratch1/TNG_tables` present; `~/arepo` on the right commit; `python3 scripts/test_clusters.py` passes;
   the remaining open items in `PROGRESS.md` are settled with the user (max-phys softening, merger-host log flag).
1. **Make the dir** from the manifest, e.g. for L/DYN12 on Bridges:
   ```
   python3 scripts/make_run.py --template runs/templates/zf4_tde --dest runs/ZF4_L/dyn12 --jobname zf4Ldyn \
       --outdir '$HOME/scratch1/1_offcenter_zoom/runs/ZF4_L/dyn12' --cluster bridges --nodes 8 \
       --set DynamicalSeedBlackHoleMass=1.2e-3 --comment 'ZF4_L DYN12: dynamical seed 1.2e7 Msun/h, threshold 1e10 Msun/h'
   ```
   For `ZF4_H/*` use `--nodes 12` and add `--set InitCondFile=$HOME/scratch1/MultiZoomICs/ics_targethalos_LtU_L500_M13.00-13.25_H5_Zf4_000`.
   `make_run.py` rewrites partition/account/tasks-per-node/walltime/module script/MaxMemSize/TimeLimitCPU/home paths for the cluster.
2. **Diff against fid**: `diff runs/ZF4_L/fid/param.txt runs/ZF4_L/dyn12/param.txt` and the same for `Config.sh` (must be identical) and `run.sh`
   (job name and outdir only).
3. **Compile**: `bash compile.sh > compile.log 2>&1`; `tail -1 compile.log` is the link line; `grep -n "BH_DF_DISCRETE\|HIGHER_DYNAMICAL\|MERGE_BHS\|RELATIVE_VEL\|KINEMATICS\|BH_NEW_CENTERING" build/arepoconfig.h`
   must show the five dynamics flags and no `BH_NEW_CENTERING`. Record the `~/arepo` commit in `doc/run_status.md`.
4. **Pre-flight**: every path in `param.txt` exists:
   `for f in $(grep -E "^(InitCondFile|TreecoolFile|YieldTablePath|PreEnrichAbundanceFile|CoolingTablePath|SelfShieldingFile|PhotometricsTablePath|TreecoolFileAGN)\s" param.txt | awk '{print $2}'); do ls -d $f* >/dev/null || echo MISSING $f; done`
5. **Validation segment first** (plan S3.6): submit `run.sh` as is; the first job doubles as the validation segment. Within ~5 min check the log
   in the scratch mirror (`log-<jobid>`): no `PARAMETERS: ... not found`/`Terminate`; `READIC: Type 1: 36837120 ... masstab= 0.00020764` (L) or
   `54058240` (H); `Sync-Point 1` appears. Then after a few hours: memory per task (`memory.txt`, HEALTHTEST lines), pace (z vs wall hours), first
   BH seeds in `blackhole_details/` (18 columns), `blackhole_mergers/` present. Record peak memory and pace in `doc/run_status.md`; fix the node
   count for the set from that (all three variants of a bin on the same layout).
6. **Record** in `doc/run_status.md` (status, job ID, date, commit) and `PROGRESS.md`.

## 3. Restarting

Arepo stops at 85 % of `TimeLimitCPU` (Bridges 190000 s -> 44.9 h; Orion 81000 s -> 19.2 h), writes `output/restartfiles/` and touches
`output/cont`; `output/end` means TimeMax reached. `sbatch restart.sh` continues and re-submits itself (`--dependency=afterany`) until `end`
exists. `run.sh` does not chain: after the first job pauses, somebody must submit `restart.sh` (0_feedback practice: queue the chain right after
the first job starts). Never change `Config.sh` between restart-file restarts. Snapshot restart (`./Arepo param.txt 2 <snap>`) loses the BH
details since that snapshot — note it in the run table.

## 4. Output layout (`~/scratch1/1_offcenter_zoom/runs/<set>/<variant>/output/`)

`snapdir_NNN/snapshot_NNN.k.hdf5` (8 files), `groups_NNN/fof_subhalo_tab_NNN.k.hdf5` (FoF+SubFind HBT, `MERGERTREE`), `blackhole_details/`
(`blackhole_details_<task>.txt`: 18-column kinematics lines; `blackhole_unified_<task>.txt`: the 0_feedback unified log; `blackhole_spin_*`),
`blackhole_mergers/`, `blackholes.txt`, `sfr.txt`, `cpu.txt`, `memory.txt`, `restartfiles/`, `cont`/`end`; `../log-<jobid>` per job.

## 5. Monitoring

`python3 scripts/run_status.py` (one line per run on this cluster: status, z, snapshots, wall hours, job IDs);
live: `grep ^Sync-Point ~/scratch1/1_offcenter_zoom/runs/<set>/<variant>/log-<jobid> | tail -1`. Bridges: `squeue -u nianyic`,
`lfs quota -p 554803 /ocean` before launching (a zoom to z=0 needed ~1.1 TB for H16_Zf2; restart sets 430 GB each there).

## 6. Pitfalls (from 0_feedback)
- kpc/h vs Mpc/h: everything here is Mpc/h (TNG reference files are kpc/h). `MaxSfrTimescale 0.00227`, `NSNS_MassPerEvent 5000` (Msun, code converts).
- `MaxMemSize 3600 x 64` on Bridges RM, `4000 x 112` on Orion; do not raise tasks/node.
- `sbatch` returns even when the queue is full: check `squeue` and the log before recording "running".
- Bridges fairshare is low: 16-node jobs waited 62–67 h in the queue on 2026-09-30. Smaller (4–6 node) jobs should wait less — record it.
