"""Per-cluster settings. A run starts and finishes on one cluster; make_run.py writes that cluster's values into the
new run dir (SBATCH lines, module script, walltime, param.txt home paths, MaxMemSize, TimeLimitCPU). Existing run dirs are never rewritten.

    import clusters; c = clusters.get()          # detected from $HOME (or $OFFCENTER_CLUSTER)
Values marked "verify" were not checked on the machine: confirm them before the first run there.
"""
import os

SITES = {
    "orion": dict(
        homes=("/u/nianyic", "/orion/u/nianyic"), partition="p.exclusive", account=None,
        tasks_per_node=112, node_mem_gb=512, max_mem_mb=4000,        # 112 x 4000 MB < 512 GB
        modules="load_modules.sh", walltime="23:00:00", time_limit_cpu=81000,  # Arepo stops at 85% = 19.1 h
        limits="QOS normal: 30 nodes, 6 running jobs per user"),
    "bridges": dict(                                                 # PSC Bridges-2 RM nodes (verified 2026-09-29)
        homes=("/jet/home/nianyic",), partition="RM", account="phy240015p",
        account_required=True,
        tasks_per_node=64, node_mem_gb=256, node_mem_limit_mb=240000, max_mem_mb=3200,  # 128 cores/node, cgroup limit 240000 MB/node;
                                                                     # 64 x 3200 MB (3600 was OOM-killed after ~39 h in 0_feedback, 2026-10-03)
        modules="modules_br2.sh",                                    # loads openmpi 4.0.5 again after fftw (which pulls in a broken 3.1.6)
        walltime="48:00:00", time_limit_cpu=190000,                  # RM max 48 h; 85% of 190000 s = 44.9 h, 3 h margin for the restart write
        limits="QOS rm: 25600 cores (200 RM nodes) per user, 5000 submitted jobs; RM walltime max 48 h"),
}
REQUIRED = ("partition", "tasks_per_node", "max_mem_mb", "modules", "walltime", "time_limit_cpu")


class SiteError(ValueError):
    pass


def detect(home=None):
    name = os.environ.get("OFFCENTER_CLUSTER", "").lower() if home is None else None
    if name:
        return name
    home = home or os.path.expanduser("~")
    real = os.path.realpath(home) if os.path.exists(home) else home
    for name, s in SITES.items():
        if home in s["homes"] or real in s["homes"]:
            return name
    raise SiteError(f"unknown cluster for home {home!r}; add it to scripts/clusters.py or set $OFFCENTER_CLUSTER")


def check(s):
    missing = [k for k in REQUIRED if s.get(k) in (None, "")]
    if s.get("account_required") and not s.get("account"):
        missing.append("account")
    if missing:
        raise SiteError(f"cluster settings incomplete: {missing}; edit scripts/clusters.py")
    return s


def get(name=None):
    name = (name or detect()).lower()
    return dict(check(dict(SITES[name])), name=name, home=SITES[name]["homes"][0])
