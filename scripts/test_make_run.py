#!/usr/bin/env python3
"""Test scripts/make_run.py: derive a run dir from the ZF4 template and verify the edits.

Prints <=5 lines on success; details in test_logs/test_make_run.log.
"""
import os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "runs", "templates", "zf4_tde")
LOG = os.path.join(ROOT, "test_logs", "test_make_run.log")


def main():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    log = open(LOG, "w")
    tmp = tempfile.mkdtemp(prefix="make_run_", dir=os.path.join(ROOT, "test_logs"))
    dest = os.path.join(tmp, "ZF9_T", "foo")
    cmd = [sys.executable, os.path.join(ROOT, "scripts", "make_run.py"),
           "--template", TEMPLATE, "--dest", dest, "--jobname", "t9foo",
           "--outdir", "$HOME/scratch1/1_offcenter_zoom/runs/ZF9_T/foo",
           "--add-flag", "REDUCE_DFD_WITH_BH_GROWTH", "--add-flag", "OUTPUT_HOST_PROPERTIES_FOR_BH_MERGERS",
           "--set", "DynamicalSeedBlackHoleMass=1.2e-3", "--set", "MinFoFMassForNewSeed=5.0",
           "--set", "LogMassRatioFullDFD=1.0", "--set", "NewTag=7",
           "--comment", "T9 test run"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    log.write(r.stdout + r.stderr)
    fails = []
    if r.returncode != 0:
        fails.append("make_run.py exit %d" % r.returncode)
    cfg = open(os.path.join(dest, "Config.sh")).read()
    prm = open(os.path.join(dest, "param.txt")).read()
    runsh = open(os.path.join(dest, "run.sh")).read()
    rst = open(os.path.join(dest, "restart.sh")).read()
    flags = [l.strip() for l in cfg.splitlines() if l.strip() and not l.startswith("#")]
    for f in ("REDUCE_DFD_WITH_BH_GROWTH", "OUTPUT_HOST_PROPERTIES_FOR_BH_MERGERS", "BH_DF_DISCRETE",
              "HIGHER_DYNAMICAL_SEED_MASS", "MERGE_BHS_WITHIN_GAS_SOFTENING", "RELATIVE_VELOCITY_CRITERION_FOR_MERGERS",
              "OUTPUT_BLACKHOLE_KINEMATICS", "BH_ADIOS_WIND"):
        if f not in flags:
            fails.append("flag missing: " + f)
    if flags.count("REDUCE_DFD_WITH_BH_GROWTH") != 1:
        fails.append("REDUCE_DFD_WITH_BH_GROWTH duplicated")
    if "BH_NEW_CENTERING" in flags:
        fails.append("BH_NEW_CENTERING must be off with BH_DF_DISCRETE")
    if "T9 test run" not in cfg.splitlines()[0]:
        fails.append("Config header comment not set")

    def val(key):
        m = re.search(r"^%s\s+(\S+)" % re.escape(key), prm, re.M)
        return m.group(1) if m else None
    exp = {"DynamicalSeedBlackHoleMass": "1.2e-3", "MinFoFMassForNewSeed": "5.0",
           "LogMassRatioFullDFD": "1.0", "NewTag": "7", "MinDistanceForMergingBlackHoles": "2",
           "DesNumNgbBlackHole": "156", "BoxSize": "500.0", "TimeBegin": "0.015625", "SeedBlackHoleMass": "5.0e-5",
           "SofteningComovingType1": "0.0004", "SofteningMaxPhysType1": "0.0004", "SofteningMaxPhysType0": "0.0004"}
    for k, v in exp.items():
        if val(k) != v:
            fails.append("param %s = %r, expected %r" % (k, val(k), v))
    if re.search(r"^%\s*LogMassRatioFullDFD", prm, re.M):
        fails.append("commented LogMassRatioFullDFD still present")
    if re.search(r"^BlackHoleCenteringMassMultiplier", prm, re.M):
        fails.append("BlackHoleCenteringMassMultiplier live although BH_NEW_CENTERING is off")
    for name, txt in (("run.sh", runsh), ("restart.sh", rst)):
        if 'outdir="$HOME/scratch1/1_offcenter_zoom/runs/ZF9_T/foo"' not in txt:
            fails.append(name + ": outdir not set")
        if "templates" in txt or "0_feedback" in txt:
            fails.append(name + ": template outdir leaked")
    if "--job-name=t9foo\n" not in runsh or "--job-name=t9foo-r\n" not in rst:
        fails.append("job names not set")
    import clusters
    tpn = clusters.get()["tasks_per_node"]
    if "-N 8" not in runsh or "-np %d" % (8 * tpn) not in runsh:
        fails.append("node layout changed")
    for junk in ("Arepo", "build", "compile.log"):
        if os.path.exists(os.path.join(dest, junk)):
            fails.append("template artefact copied: " + junk)
    if not os.path.exists(os.path.join(dest, "compile.sh")):
        fails.append("compile.sh missing")
    log.write("\n".join(fails) + "\n")
    log.close()
    shutil.rmtree(tmp)
    if fails:
        print("FAIL test_make_run: %d problems (see %s)" % (len(fails), LOG))
        for f in fails[:20]:
            print("  " + f)
        sys.exit(1)
    print("PASS test_make_run: Config flags, %d params, run/restart outdir+jobname, no build artefacts" % len(exp))


if __name__ == "__main__":
    main()
