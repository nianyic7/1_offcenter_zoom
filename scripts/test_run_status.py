#!/usr/bin/env python3
"""Test run_status parsing on a synthetic run directory (no slurm needed)."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import run_status as rs

fails = []
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "output", "snapdir_000")); os.makedirs(os.path.join(d, "output", "snapdir_001"))
    open(os.path.join(d, "output", "cont"), "w").close()
    with open(os.path.join(d, "log-100"), "w") as f:
        f.write("Sync-Point 0, Time: 0.0078125, Redshift: 127, Systemstep: 0\n")
        f.write("Sync-Point 500, Time: 0.2, Redshift: 4, Systemstep: 1e-5\n")
        f.write("Code run for 3600.0 seconds!\nbye!\n")
    with open(os.path.join(d, "log-101"), "w") as f:
        f.write("Sync-Point 900, Time: 0.25, Redshift: 3, Systemstep: 1e-5\n")
        f.write("Code run for 7200.0 seconds!\nbye!\n")
    info = rs.parse_log(os.path.join(d, "log-100"))
    if info["last_z"] != 4 or info["steps"] != 500 or info["code_run_s"] != 3600.0 or not info["clean_exit"]:
        fails.append(f"parse_log: {info}")
    s = rs.run_summary(d, query_slurm=False)
    if s["jobs"] != [100, 101]: fails.append(f"jobs {s['jobs']}")
    if s["last_z"] != 3: fails.append(f"last_z {s['last_z']}")
    if abs(s["wall_h"] - 3.0) > 1e-9: fails.append(f"wall_h {s['wall_h']}")
    if s["snaps"] != 2: fails.append(f"snaps {s['snaps']}")
    if rs.status_word(s) != "paused": fails.append(f"status {rs.status_word(s)}")
    open(os.path.join(d, "output", "end"), "w").close()
    if rs.status_word(rs.run_summary(d, query_slurm=False)) != "done": fails.append("status after end != done")
    with open(os.path.join(d, "log-102"), "w") as f:
        f.write("Sync-Point 901, Time: 0.26, Redshift: 2.8\nTerminate: something bad\n")
    os.remove(os.path.join(d, "output", "end"))
    s = rs.run_summary(d, query_slurm=False)
    if rs.status_word(s) != "failed" or "something bad" not in (s["error"] or ""): fails.append(f"failed detection: {s}")
# run discovery: <root>/runs/<set>/<variant>; runs/templates and symlinks are skipped
with tempfile.TemporaryDirectory() as root:
    for rel in ("runs/ZF4_L/fid", "runs/ZF4_L/dyn12", "runs/ZF4_H/seed50", "runs/templates/zf4_tde"):
        os.makedirs(os.path.join(root, rel))
    os.symlink("fid", os.path.join(root, "runs/ZF4_L/fid_old"))   # compat link
    os.makedirs(os.path.join(root, "ICs"))
    got = [os.path.relpath(p, root) for p in rs.find_run_dirs(root)]
    want = ["runs/ZF4_H/seed50", "runs/ZF4_L/dyn12", "runs/ZF4_L/fid"]
    if got != want: fails.append(f"find_run_dirs {got}")
if fails:
    print("FAIL:"); [print("  " + f) for f in fails]; sys.exit(1)
print("PASS run_status: parse_log, multi-log summary, paused/done/failed status words, runs/<set>/<variant> discovery (templates skipped)")
