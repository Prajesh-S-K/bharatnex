# Geo-Sentry research vault

`vault/` is a verbatim import of the project's Obsidian research vault (49 topic
folders, imported 2026-08-30). It is **research and evidence-control material**, not
a spec for this repo's code — it exists so that every threshold, sensor choice, and
citation used anywhere in Geo-Sentry can be traced to a credited source instead of an
invented number. `[[wikilinks]]` inside these files only resolve in Obsidian.

Start here:

- [`vault/00 MASTER CONTROL/Geo-Sentry Prototype Module Priority Plan.md`](vault/00%20MASTER%20CONTROL/Geo-Sentry%20Prototype%20Module%20Priority%20Plan.md) — the module build order this repo follows.
- [`vault/00 MASTER CONTROL/Geo-Sentry Sourced Parameter Register.md`](vault/00%20MASTER%20CONTROL/Geo-Sentry%20Sourced%20Parameter%20Register.md) — **the only place a new alarm/threshold value may come from.** As of this import it records `THR-0001 | _None approved_ | blocked` for our sensors — see `../INDUSTRIAL_ROADMAP.md` for what that means for `intelligence/config.py`.
- [`vault/00 MASTER CONTROL/Geo-Sentry Prototype Evidence and Demonstration Checklist.md`](vault/00%20MASTER%20CONTROL/Geo-Sentry%20Prototype%20Evidence%20and%20Demonstration%20Checklist.md) — what the running prototype must actually prove, and how demo/synthetic data must be labeled.
- [`vault/48 PROTOTYPE MODULES/`](vault/48%20PROTOTYPE%20MODULES/) — one tracking file per module. These were imported as unfilled templates (`status: planned`); `../INDUSTRIAL_ROADMAP.md` is where each module's real status against this codebase is recorded as work lands, module by module.

## Rule this repo follows

No number from `vault/` becomes a threshold, pin assignment, or factual claim in
`apps/`, `intelligence/`, or `firmware/` unless it is either (a) already an agreed,
frozen contract value (`contracts/*.schema.json`), or (b) explicitly labeled by its
source classification from the Sourced Parameter Register (regulatory/guidance limit,
source observation, site baseline, Geo-Sentry experiment, design assumption, or
derived value) — never presented as more certain than that classification allows.
