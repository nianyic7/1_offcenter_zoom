# Off-nuclear TDE project: first-round runs

3 October 2026 | Setup handoff draft v2

## Decision

Start six ZF4 multizoom simulations on two IC sets, each containing five target halos: three configurations per halo-mass bin. The shared fiducial separates the effects of dynamical mass and seeding threshold without requiring a full factorial grid. Start with short validation segments of these same production runs, then continue to z = 0.

This supersedes the earlier two-run launch recommendation and the earlier 1e7 Msun dynamical-mass variant. No simulation has been launched by this document. Repository, cluster, IC paths, and resource requests must be filled from the actual environment.

## 1. Production queue

All physical BH seeds have mass 5 x 10^5 Msun (provisional interpretation: physical Msun, not Msun/h; confirm before launch). Each row below is one multizoom job with five targets.

| Run label | Parent z = 0 log10(M200c/Msun) | Dynamical seed mass (physical Msun) | Seeding halo threshold (Msun/h) |
| --- | --- | --- | --- |
| TDE_ZF4_L_FID | [12.75, 13.00) | 6 x 10^6 | 1 x 10^10 |
| TDE_ZF4_L_DYN12 | Same lower-bin ICs | 1.2 x 10^7 | 1 x 10^10 |
| TDE_ZF4_L_SEED50 | Same lower-bin ICs | 6 x 10^6 | 5 x 10^10 |
| TDE_ZF4_H_FID | [13.00, 13.25) | 6 x 10^6 | 1 x 10^10 |
| TDE_ZF4_H_DYN12 | Same upper-bin ICs | 1.2 x 10^7 | 1 x 10^10 |
| TDE_ZF4_H_SEED50 | Same upper-bin ICs | 6 x 10^6 | 5 x 10^10 |

Total: six jobs, thirty target-halo realizations, ten distinct targets, two IC sets. The optional crossed case (1.2 x 10^7 Msun dynamical mass and 5 x 10^10 Msun/h threshold) adds one run per bin, giving eight jobs. It is required to measure the interaction between these choices; the initial six measure each change relative to the fiducial and cannot establish separability.

DYN12 versus FID tests dynamical mass at fixed seeding. SEED50 versus FID tests the consequences of delayed/reduced seeding, including possible changes to BH growth, feedback, and galaxy structure; it is not merely a post-processing abundance rescaling. Match galaxies using IC particle ancestry, not BH IDs or final stellar mass alone.

Use a documented common parent mass definition; M200c is the proposed selection convention, subject to identifying the actual catalog field. The seeding threshold uses the mass definition in the existing seeding code, potentially FoF mass, which need not equal the parent-selection M200c. Fix bins from the parent selection; hydro evolution does not trigger reselection.

Select five eligible halos per bin reproducibly, without inspecting their BH outcomes. Apply the existing IC pipeline's technical suitability requirements and record exclusions. Do not impose a new strong isolation, morphology, or merger-history cut for this first project. Nearby selected regions can be combined by the multizoom pipeline; check that target systems are distinct, and record shared environments.

## 2. Fixed physics configuration

Use the working TNG configuration as the base. Retain its galaxy formation, cooling, star formation, winds, BH accretion/feedback, and all seeding conditions except the specified halo threshold and seed mass. The common physical seed mass and seeding thresholds below are explicit project choices; do not silently restore stock TNG values.

```text
BH_DF_DISCRETE
HIGHER_DYNAMICAL_SEED_MASS
MERGE_BHS_WITHIN_GAS_SOFTENING
RELATIVE_VELOCITY_CRITERION_FOR_MERGERS
OUTPUT_BLACKHOLE_KINEMATICS

# Disabled:
# BH_NEW_CENTERING
# REDUCE_DFD_WITH_BH_GROWTH
```

```text
SeedBlackHoleMass                    <verified value for 5e5 physical Msun>
MinDistanceForMergingBlackHoles       2
DynamicalSeedBlackHoleMass           <verified value for 6e6 or 1.2e7 Msun>
<actual halo-seeding parameter>      <verified value for 1e10 or 5e10 Msun/h>
```

The nominal baseline dynamical seed mass is 6 x 10^6 physical Msun. The intended numerical condition is about three times the high-resolution DM particle mass. Verify these together before freezing the parameter: the earlier approximate ZF4-to-TNG100 mass scaling and the approximately 2 x 10^6 Msun DM estimate are not a substitute for reading the IC header. If the actual DM mass makes 6 x 10^6 Msun appreciably less than three particle masses, flag the mismatch and settle one common baseline value before production; do not silently change either the mass or its units.

Code-unit conversion, if the parameter mass unit is 10^10 Msun/h:

| Quantity | Code-unit value |
| --- | --- |
| Physical seed: 5e5 physical Msun | 5e-5 times h |
| Fiducial dynamical seed: 6e6 physical Msun | 6e-4 times h |
| Variant dynamical seed: 1.2e7 physical Msun | 1.2e-3 times h |
| Seeding threshold: 1e10 Msun/h | 1 |
| Seeding threshold: 5e10 Msun/h | 5 |

If the user intends a physical seed of 5e5 Msun/h instead, its code value is 5e-5. This unit assumption is not yet confirmed. Resolve the actual parameter name and units in the source; do not paste placeholders into a runtime parameter file. Use identical values across both parent bins for each configuration. The dynamical-to-physical seed ratios under the physical-Msun interpretation are 12 and 24.

The new physical seed replaces the earlier 1e-05 code-unit choice. Models cannot directly represent BHs below their seed mass; the lower-mass observed TDE systems can still inform galaxy-environment comparisons but are not direct BH-mass matches.

Use the existing implemented DF and merger criteria. Inspect and record which softening the distance criterion actually uses, the physical/comoving convention, the velocity/binding expressions, the mass used by gravity/DF/merger checks, and how dynamical mass evolves after accretion or mergers. Check for other active repositioning paths. Do not implement a new model during setup.

## 3. IC and launch checks

1. Record parent simulation, cosmology, target IDs, mass field/units, positions, masses, R200, selection seed, and eligibility cuts. Preserve particle IDs and target mappings for matched variants and ZF8 reruns.
2. Generate the two ZF4 IC sets using the established multizoom workflow, with its validated Lagrangian padding and refinement transitions. Preserve phase information, masks, and generation settings.
3. Verify gas and high-resolution DM masses, particle counts/types, periodic coordinates, starting redshift, cosmology, and high-resolution coverage. The mask must cover material feeding target satellites, not just the final central galaxy. If the pipeline lacks validated coverage, complete its normal inexpensive contamination check before committing hydro production.
4. Use the established ZF4 softening and timestep prescription as the starting point; record species softenings, physical/comoving transitions, and BH softening. Avoid introducing an untested softening change merely to make a 1 kpc target appear resolved.
5. Build from a recorded commit and save the effective compile configuration and parameter file. Check the intended dynamics flags are in the executable.
6. Run a short segment of each production setup. Verify initialization, finite quantities, output schema, memory/I/O, checkpoint/restart, and IC consistency. This need not reach low redshift.
7. Separately verify the DF/merger path with an existing suitable regression case, restart, or small diagnostic if no BH forms during that segment. Lack of early BHs does not validate the implementation. Check that BH creation at both thresholds, mass assignment, kinematic outputs, and merger records behave as intended. Verify the 1e10 Msun/h progenitors are adequately represented at seeding; confirm seeding cadence and restrictions in already occupied groups.
8. Continue all six validated runs toward z = 0. Baseline validation need not finish the full cosmological evolution before variants start. Set scheduler resources from measured memory and runtime, with checkpoint margins; do not invent node counts or total cost from halo mass alone.

## 4. Outputs to decide before the long runs

The main irreversible risk is missing progenitor or orbital information. Nuclear-cluster models, TDE rates, and survey selection can be chosen later.

| Output | Minimum content | Proposed cadence or handling |
| --- | --- | --- |
| Full snapshots | Standard hydro fields, particle IDs, positions, velocities, masses, stellar formation times and metallicities, physical/dynamical BH masses | Retain the existing production schedule and z = 0 output |
| Galaxy-tracking outputs | DM, stars, BHs and required gas fields for valid bound-mass catalogs; membership IDs and halo/subhalo catalogs | Starting proposal: every 50 Myr at z <= 3; retain standard early outputs and ensure relevant progenitors are captured before infall |
| BH details | ID, time, physical/dynamical mass, position, velocity; existing accretion and DF diagnostics | Use existing high-frequency details; measure actual cadence and data volume |
| Galaxy centers | Time-dependent centers and velocities for main galaxies and tracked progenitors | Must support orbital analysis on comparable timescales; sparse centers cannot be repaired by frequent BH positions alone |
| BH events | Seed time/host, host mass and mass definition at creation, physical/dynamical seed masses; merger time, both IDs and survivor; available separation/velocity diagnostics | Event-driven, persistent across restarts |
| Checkpoints | Restart files and matching metadata | Rolling recovery copies plus useful retained milestones within budget |

The 50 Myr proposal is for galaxy stripping, not a guarantee of resolved inner pericenters. Before coarse-graining BH details, test a cadence of at most roughly one tenth of the relevant crossing time, r/v, for both BH motion and center tracking. For example, 1 kpc at 200 km/s corresponds to about 5 Myr. If existing outputs cannot support sub-Myr center tracking, identify that limit and the lowest-cost targeted output option; do not claim inner-orbit completeness from BH details alone.

A stars-plus-BHs file alone is insufficient for total binding estimates. Use existing mini-snapshot support only if it retains the components required by the analysis/catalog pipeline. Prefer existing outputs over adding large new logging systems; identify genuinely missing, unrecoverable fields before the long run. Merger trees, infall properties, pericenters, and stripping fractions can be derived later if the underlying outputs are retained.

## 5. Early review without retuning

After outputs contain relevant satellites and BHs, inspect representative systems for seed occupation, mass ratios, BH trajectories, merger distances, stellar sizes, and contamination. Compare central stellar masses with the intended approximately 10^11 Msun population when the runs reach low redshift. Unexpected science outcomes are not grounds to reselect halos or retune feedback; numerical failures should be diagnosed and versioned.

The resolution goal is stripping of the extended satellite galaxy. Do not require resolved stellar nuclei. Flag declining galaxy particle counts and sizes relative to softening; disappearance from a finder is not proof that every bound star is gone.

## 6. Queue next, not required to launch now

- **Crossed seeding/dynamical-mass case:** add the 1.2e7 Msun dynamical mass with the 5e10 Msun/h seeding threshold in both bins if resources permit or interaction effects become a core question. Use the same ICs, outputs, and all other settings.
- **ZF8 convergence:** preserve the option for two matched halos, one per bin. Finalize the force/mass comparison convention before starting; do not change dynamical mass with resolution without distinguishing that change from resolution itself.
- Defer nucleus assignment, TDE-rate modeling, survey selection, dedicated field-control runs, wider halo-mass coverage, and parent merger-history experiments. Preserve data for these choices rather than delaying the baseline simulations.

## 7. Setup handoff deliverables

- A target manifest and complete IC provenance for both IC sets.
- A common physics configuration plus a machine-readable six-run manifest. Parameter differences must be limited to the intended seeding threshold/dynamical mass and run-specific paths/ICs; diff every variant against its fiducial.
- Resolved code-unit parameters, measured DM/baryon masses, softenings, and mass ratios.
- Executable commit/build provenance, restartable job scripts, output schedule, and measured resource estimate.
- A short validation receipt listing completed checks and any remaining limitation.

Repository paths, parent catalog, IC generator invocation, scheduler partition/account, and storage budget are environment-specific inputs still to be supplied. This document is a launch plan, not a claim that those resources or jobs have been configured.
