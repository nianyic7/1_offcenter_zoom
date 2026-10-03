#!/usr/bin/env python3
"""Derive a new run config dir from a template (the ZF4 TDE template: runs/templates/zf4_tde).
Run dirs live under runs/<set>/<variant> (e.g. runs/ZF4_L/fid); the scratch outdir mirrors the dest path.

Copies Config.sh, param.txt, outputs.txt, compile.sh, run.sh, restart.sh (never build/, Arepo,
logs), then:
  --add-flag F       append Config flag F (once; placed after the last BH_* line)
  --remove-flag F    drop Config flag F
  --set KEY=VALUE    set param KEY (uncomments a '%KEY' line, replaces an existing value, or
                     appends to the end of the BH block)
  --jobname NAME     SBATCH job name (restart.sh gets NAME-r)
  --outdir PATH      scratch output dir written into run.sh/restart.sh (use $HOME/...)
  --comment TEXT     first-line comment of Config.sh
  --cluster NAME     cluster the run will live on (default: detected from $HOME; see clusters.py): sets SBATCH
                     partition/account/tasks-per-node/walltime, module script (run/restart/compile.sh), param.txt home paths, MaxMemSize, TimeLimitCPU
  --nodes N          node count (default: the template's -N); mpiexec -np = N x tasks-per-node
Example (the manifest doc/run_manifest.json lists the exact --set values per run):
  python3 scripts/make_run.py --template runs/templates/zf4_tde --dest runs/ZF4_L/dyn12 \
      --jobname zf4Ldyn --outdir '$HOME/scratch1/1_offcenter_zoom/runs/ZF4_L/dyn12' \
      --set DynamicalSeedBlackHoleMass=8.1288e-4 --comment 'ZF4_L DYN12: ...'
"""
import argparse, os, re, shutil, sys

import clusters

FILES = ["Config.sh", "param.txt", "outputs.txt", "compile.sh", "run.sh", "restart.sh"]
MODULE_RE = re.compile(r"^source \$codedir/\S+$", re.M)


def edit_config(text, add, remove, comment):
    lines = text.splitlines()
    if comment:
        if lines and lines[0].startswith("#"):
            lines[0] = "# " + comment
        else:
            lines.insert(0, "# " + comment)
    flags = [l.strip() for l in lines]
    for f in remove:
        lines = [l for l in lines if l.strip() != f]
    for f in add:
        if f in [l.strip() for l in lines]:
            continue
        idx = max(i for i, l in enumerate(lines) if l.strip().startswith("BH_") or l.strip() == "BLACK_HOLES")
        lines.insert(idx + 1, f)
    return "\n".join(lines) + "\n"


def edit_param(text, sets):
    lines = text.splitlines()
    for key, value in sets:
        pat_live = re.compile(r"^" + re.escape(key) + r"\s+\S+(.*)$")
        pat_dead = re.compile(r"^%\s*" + re.escape(key) + r"\s+\S+(.*)$")
        done = False
        for i, l in enumerate(lines):
            m = pat_live.match(l)
            if m:
                lines[i] = "%-38s %s%s" % (key, value, m.group(1))
                done = True
                break
        if not done:
            for i, l in enumerate(lines):
                m = pat_dead.match(l)
                if m:
                    lines[i] = "%-38s %s%s" % (key, value, m.group(1))
                    done = True
                    break
        if not done:
            # append right after BlackHoleFeedbackDebugOutput (end of the BH block) or at EOF
            idx = next((i for i, l in enumerate(lines) if l.startswith("BlackHoleFeedbackDebugOutput")), len(lines) - 1)
            lines.insert(idx + 1, "%-38s %s" % (key, value))
    return "\n".join(lines) + "\n"


def edit_job(text, jobname, outdir, suffix):
    if jobname:
        text = re.sub(r"^#SBATCH --job-name=.*$", "#SBATCH --job-name=%s%s" % (jobname, suffix), text, flags=re.M)
    if outdir:
        text = re.sub(r'^outdir=.*$', 'outdir="%s"' % outdir, text, flags=re.M)
    return text


def edit_site_job(text, site, nodes):
    """SBATCH partition/-N/tasks-per-node/account/walltime, module script and mpiexec -np for the target cluster (idempotent)"""
    tpn = site["tasks_per_node"]
    text = edit_site_compile(text, site)
    text = re.sub(r"^#SBATCH -p .*$", "#SBATCH -p %s" % site["partition"], text, flags=re.M)
    text = re.sub(r"^#SBATCH --time=.*$", "#SBATCH --time=%s" % site["walltime"], text, flags=re.M)
    text = re.sub(r"^#SBATCH -N .*$", "#SBATCH -N %d" % nodes, text, flags=re.M)
    text = re.sub(r"^#SBATCH --ntasks-per-node=.*$", "#SBATCH --ntasks-per-node=%d" % tpn, text, flags=re.M)
    text = re.sub(r"^#SBATCH -A .*\n", "", text, flags=re.M)
    if site.get("account"):
        text = re.sub(r"^(#SBATCH -p .*)$", r"\1\n#SBATCH -A %s" % site["account"], text, count=1, flags=re.M)
    return re.sub(r"mpiexec -np \d+", "mpiexec -np %d" % (nodes * tpn), text)


def edit_site_compile(text, site):
    """`source $codedir/<module script>` -> the target cluster's script (run.sh, restart.sh, compile.sh)"""
    return MODULE_RE.sub("source $codedir/%s" % site["modules"], text)


def edit_site_param(text, site):
    """home paths of any known cluster -> the target cluster's home; MaxMemSize per task; TimeLimitCPU"""
    home = site["homes"][0]
    for s in clusters.SITES.values():
        for h in s["homes"]:
            if h != home and h not in site["homes"]:
                text = re.sub(re.escape(h) + r"(?=/)", home, text)
    text = re.sub(r"^(MaxMemSize\s+)\d+", lambda m: m.group(1) + str(site["max_mem_mb"]), text, flags=re.M)
    return re.sub(r"^(TimeLimitCPU\s+)\d+", lambda m: m.group(1) + str(site["time_limit_cpu"]), text, flags=re.M)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--jobname")
    ap.add_argument("--outdir")
    ap.add_argument("--comment")
    ap.add_argument("--add-flag", action="append", default=[])
    ap.add_argument("--remove-flag", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--force", action="store_true", help="overwrite an existing dest")
    ap.add_argument("--cluster", help="target cluster (default: detected)")
    ap.add_argument("--nodes", type=int, help="node count (default: template's)")
    a = ap.parse_args()
    if os.path.exists(a.dest) and not a.force:
        sys.exit("dest exists: %s (use --force)" % a.dest)
    os.makedirs(a.dest, exist_ok=True)
    for f in FILES:
        shutil.copy2(os.path.join(a.template, f), os.path.join(a.dest, f))
    sets = []
    for s in a.set:
        k, v = s.split("=", 1)
        sets.append((k.strip(), v.strip()))
    def rewrite(path, fn):
        # read fully before opening for write (open(path, "w") would truncate first)
        new = fn(open(path).read())
        with open(path, "w") as fh:
            fh.write(new)

    rewrite(os.path.join(a.dest, "Config.sh"), lambda t: edit_config(t, a.add_flag, a.remove_flag, a.comment))
    site = clusters.get(a.cluster)
    nodes = a.nodes or int(re.search(r"^#SBATCH -N (\d+)", open(os.path.join(a.template, "run.sh")).read(), re.M).group(1))
    rewrite(os.path.join(a.dest, "param.txt"), lambda t: edit_site_param(edit_param(t, sets), site))
    for f, suf in (("run.sh", ""), ("restart.sh", "-r")):
        rewrite(os.path.join(a.dest, f), lambda t, suf=suf: edit_site_job(edit_job(t, a.jobname, a.outdir, suf), site, nodes))
    rewrite(os.path.join(a.dest, "compile.sh"), lambda t: edit_site_compile(t, site))
    print("made %s for %s (%d nodes x %d tasks): +%s -%s, %d params set" % (
        a.dest, site["name"], nodes, site["tasks_per_node"], a.add_flag, a.remove_flag, len(sets)))


if __name__ == "__main__":
    main()
