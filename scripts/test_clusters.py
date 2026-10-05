#!/usr/bin/env python3
"""Tests for clusters.py (per-cluster settings) and make_run.py's site rewrites of run.sh/restart.sh and param.txt."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clusters as S  # noqa: E402
import make_run as MR  # noqa: E402

fails = []
if S.detect(home="/u/nianyic") != "orion" or S.detect(home="/orion/u/nianyic") != "orion": fails.append("detect orion")
if S.detect(home="/jet/home/nianyic") != "bridges": fails.append("detect bridges")
try:
    S.detect(home="/somewhere/else"); fails.append("unknown home not rejected")
except S.SiteError:
    pass
job = """#!/bin/bash
#SBATCH -p p.exclusive
#SBATCH -N 8
#SBATCH --ntasks-per-node=112
#SBATCH --job-name=m0box
#SBATCH --time=23:00:00
codedir="$HOME/arepo"
source $codedir/load_modules.sh
mpiexec -np 896 ./Arepo  param.txt > log-$SLURM_JOB_ID
"""
site = dict(S.SITES["bridges"], account="abc123", tasks_per_node=64)
out = MR.edit_site_job(job, site, nodes=14)
for want in ("#SBATCH -p RM\n", "#SBATCH -N 14\n", "#SBATCH --ntasks-per-node=64\n", "#SBATCH -A abc123\n", "mpiexec -np 896 ./Arepo",
             "#SBATCH --time=%s\n" % site["walltime"], "source $codedir/%s\n" % site["modules"]):
    if want not in out: fails.append(f"job rewrite missing {want!r}")
if out.count("#SBATCH -A") != 1 or MR.edit_site_job(out, site, nodes=14) != out: fails.append("job rewrite not idempotent")
o = MR.edit_site_job(job, S.SITES["orion"], nodes=8)
if "#SBATCH -A" in o or "source $codedir/load_modules.sh\n" not in o or "--time=23:00:00" not in o: fails.append("orion job changed")
comp = 'codedir="$HOME/arepo"\nsource $codedir/load_modules.sh\nmake build\n'
if "source $codedir/%s\n" % site["modules"] not in MR.edit_site_compile(comp, site): fails.append("compile.sh modules")
prm = "InitCondFile   /u/nianyic/scratch1/ics\nTimeLimitCPU   81000   % x\nMaxMemSize    4000    % MB per MPI task\nTreecoolFile /u/nianyic/t\n"
p2 = MR.edit_site_param(prm, site)
if "/u/nianyic" in p2 or "/jet/home/nianyic/scratch1/ics" not in p2: fails.append(f"param home rewrite {p2!r}")
if f"MaxMemSize    {site['max_mem_mb']}" not in p2: fails.append(f"MaxMemSize {p2!r}")
if f"TimeLimitCPU   {site['time_limit_cpu']}   % x" not in p2: fails.append(f"TimeLimitCPU {p2!r}")
if MR.edit_site_param(prm, S.SITES["orion"]) != prm: fails.append("orion param changed")
try:
    S.check(dict(S.SITES["bridges"], account=None)); fails.append("unfilled account accepted")
except S.SiteError:
    pass
# Bridges RM cgroup limit is 240000 MB/node; 64 x 3600 MB (150 MB/task outside the arena) was OOM-killed after ~39 h in 0_feedback
b = S.SITES["bridges"]
head = b["node_mem_limit_mb"] / b["tasks_per_node"] - b["max_mem_mb"] if "node_mem_limit_mb" in b else -1
if head < 300: fails.append(f"bridges MaxMemSize leaves {head:.0f} MB/task below the node cgroup limit (need >= 300)")
if fails:
    print("FAIL test_clusters:"); [print("  " + f) for f in fails]; sys.exit(1)
print("PASS test_clusters: detect by $HOME, job/compile/param rewrite per cluster (modules, walltime, TimeLimitCPU; idempotent), unfilled settings rejected, Bridges node memory budget")
