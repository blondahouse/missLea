# Evaluation policy — requirements before tests

**Applies to:** every Miss Lea research lab and every future decision to select, replace, or retire a component. This policy governs decisions, not merely test implementation.

## Order of work

1. **Define the decision first.** State the actual operating context, intended use, candidates or discovery boundaries, and what outcome the research must enable. Decide whether the decision concerns *technology selection*, *Demo integration*, or *production authorization*; they have different evidence requirements.
2. **Freeze selection criteria before designing comparative tests or looking at candidate-specific benchmark results.** Mark each requirement **mandatory**, **trade-off**, or **optional**; define acceptable thresholds, safety vetoes, unknown-data treatment, tie-breakers, and a **stopping rule**. Prefer the smallest set that can realistically change the decision. Record who approved the criteria and when.
3. **Map each criterion to evidence.** Design the least costly valid test, review of source/vendor documentation, or operational observation that can confirm or disprove it. For each mandatory criterion, record how PASS, FAIL and NOT TESTED will be distinguished, and what would invalidate the measurement. Tests that do not answer an explicit criterion belong to optional exploratory research, not the selection score.
4. **Collect comparable evidence.** Pin relevant versions and configurations; use equivalent workloads and threat models; report extra dependencies and confounds. An unsupported or unconfigured feature is not automatically a product failure. A useful test is one that distinguishes candidates or closes a mandatory uncertainty.
5. **Apply the predeclared decision rule and stop.** Reject observed blockers; do not fill unknowns with assumed successes or failures. Choose a candidate when the required evidence is sufficient, or state the *specific* remaining decision-blocking unknown and the minimum test needed. Do not add tests merely because more can be written.
6. **Keep integration acceptance separate.** Once a technology is selected, verify that *its actual deployment* works with real providers, real permissions, backup/recovery and spending boundaries as appropriate. Passing research tests does not automatically authorize production.

## Handling unexpected findings

Exploration and vulnerability discoveries are welcome. If a new result reveals a **material risk or missing requirement**, write down why the criteria must change and update them **before** doing the additional comparative test. Keep the previous criteria, date, rationale and evidence visible; do not quietly change thresholds to favor an already observed winner.

A reproduced critical security issue may immediately block a candidate, even if that particular attack was not in the original test plan. The block and the methodology change must both be documented. This is a safety exception, **not** a license to retrofit arbitrary preference weights.

If criteria were written **after** experiments, label the decision **retrospective** and explain the potential selection bias. Do not present it as preregistered. The newly recorded criteria become the prospective baseline for further experiments or reconsideration.

## Minimal record for each decision

A short decision record is sufficient:

- **Question and scope:** what choice is being made and for which operating context?
- **Criteria and decision rule:** mandatory gates, trade-offs, unknowns, stopping condition; recorded before comparative testing when possible.
- **Evidence plan:** which small set of tests/observations addresses each gate? A criterion-to-evidence map is preferred to a large unrelated test catalogue.
- **Outcome:** select / reject / defer, with evidence and unresolved risks.
- **Revisit triggers:** what new fact would justify reopening the choice?

The default is **criterion → evidence needed → test → result → decision**, never **test → interesting metric → invented criterion → preferred winner**.

## Historical application to Router Lab

The LLM Router Lab initially grew from exploratory functionality and security tests. Its formal selection gates in [ADR-001](router-decision-record.md) were written **after** much of that evidence had been collected: the current Bifrost selection is therefore a **retrospective provisional technology decision**, not a preregistered comparative experiment. The ADR fixes an explicit threshold for continuing to Demo integration; the remaining provider/credential/recovery checks are integration acceptance, not permission to keep inventing selection criteria.

For any future component evaluation or reopening of the router choice, adopt this policy *before* conducting candidate-specific comparative tests. See the [Memory Lab](../labs/memory/docs/memory-experiments.md) and [Router Lab](router-fair-comparison.md).
