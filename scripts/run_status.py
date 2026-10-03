#!/usr/bin/env python3
"""Summarise the state of every run under the scratch mirror.

For each <scratch>/runs/<set>/<variant>/ (or any dir given on the command line) report:
last redshift reached, whether the code stopped cleanly (output/cont) or finished
(output/end), the job IDs seen, the current slurm state, snapshots written, and
wall-clock hours used. Use this to refresh doc/run_status.md.

    python3 scripts/run_status.py            # all runs under ~/scratch1/1_offcenter_zoom/runs/<set>/<variant>
    python3 scripts/run_status.py <rundir>   # one run
"""
import glob, os, re, subprocess, sys

SCRATCH = os.path.expanduser("~/scratch1/1_offcenter_zoom")

def parse_log(path):
    """Return dict(last_z, last_a, steps, code_run_s, clean_exit, error) from an Arepo log."""
    info = dict(last_z=None, last_a=None, steps=None, code_run_s=None, clean_exit=False, error=None)
    with open(path, errors="replace") as f:
        for line in f:
            if line.startswith("Sync-Point"):
                m = re.match(r"Sync-Point (\d+), Time: ([0-9.e+-]+), Redshift: ([0-9.e+-]+)", line)
                if m:
                    info["steps"] = int(m.group(1)); info["last_a"] = float(m.group(2)); info["last_z"] = float(m.group(3))
            elif line.startswith("Code run for"):
                info["code_run_s"] = float(line.split()[3])
            elif line.startswith("bye!"):
                info["clean_exit"] = True
            elif "Terminate" in line or "TERMINATE" in line:
                info["error"] = line.strip()[:120]
    return info

def job_state(jobid):
    try:
        r = subprocess.run(["squeue", "-h", "-j", str(jobid), "-o", "%T %M"], capture_output=True, text=True, timeout=20)
        s = r.stdout.strip()
        return s if s else "not in queue"
    except Exception:
        return "unknown"

def find_run_dirs(root=SCRATCH):
    """Run dirs <root>/runs/<set>/<variant> (e.g. runs/ZF4_L/fid); runs/templates and symlinks are skipped."""
    dirs = glob.glob(os.path.join(root, "runs", "*", "*"))
    return sorted(d for d in dirs if os.path.isdir(d) and os.path.relpath(d, root).split(os.sep)[1] != "templates"
                  and not any(os.path.islink(os.path.join(root, *os.path.relpath(d, root).split(os.sep)[:k + 1])) for k in range(3)))

def run_summary(rundir, query_slurm=True):
    logs = sorted(glob.glob(os.path.join(rundir, "log-*")), key=lambda p: int(re.search(r"log-(\d+)", p).group(1)))
    out = os.path.join(rundir, "output")
    summ = dict(run=os.path.relpath(rundir, SCRATCH) if rundir.startswith(SCRATCH) else rundir,
                jobs=[int(re.search(r"log-(\d+)", p).group(1)) for p in logs],
                last_z=None, wall_h=0.0, snaps=len(glob.glob(os.path.join(out, "snapdir_*"))),
                ended=os.path.exists(os.path.join(out, "end")),
                cont=os.path.exists(os.path.join(out, "cont")),
                error=None, slurm=None)
    for p in logs:
        info = parse_log(p)
        if info["last_z"] is not None: summ["last_z"] = info["last_z"]
        if info["code_run_s"]: summ["wall_h"] += info["code_run_s"] / 3600.0
        if info["error"]: summ["error"] = info["error"]
    if summ["jobs"] and query_slurm:
        summ["slurm"] = job_state(summ["jobs"][-1])
    return summ

def status_word(s):
    if s["ended"]: return "done"
    if s["slurm"] and s["slurm"] not in ("not in queue", "unknown"): return s["slurm"].split()[0].lower()
    if s["error"]: return "failed"
    if s["cont"]: return "paused"
    if not s["jobs"]: return "no jobs"
    return "stopped"

def format_line(s):
    z = f"z={s['last_z']:.2f}" if s["last_z"] is not None else "z=--"
    jobs = ",".join(map(str, s["jobs"])) or "-"
    return f"{s['run']:<46} {status_word(s):<9} {z:<9} snaps={s['snaps']:<3} wall={s['wall_h']:6.1f}h jobs={jobs}"

if __name__ == "__main__":
    dirs = sys.argv[1:] or find_run_dirs()
    try:
        import clusters
        here = clusters.detect()
    except Exception as e:  # unknown machine: still list the local runs
        here = f"unknown ({e})"
    print(f"# cluster: {here} (only runs on this cluster are visible; global list: doc/run_status.md Cluster column)")
    for d in dirs:
        print(format_line(run_summary(d)))
