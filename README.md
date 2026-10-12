# Proofwork

**Investigate deeply. Decide proportionately. Build only what's necessary. Prove what actually works.**

Proofwork unifies two complimentary skill disciplines:

- **REA Investigator** (`Devaretanmay/rea-investigate`): authorized deep investigation of applications, binary artifacts, firmware, network and version changes with 13 capabilities, evidence hashes, counteranalysis and a strictly validated report.
- **Systemcraft**: outcome-first automation design, deterministic work before AI where appropriate, staged file workspaces, human checkpoints, and validation.

**Architecture decision:** A *single* `proofwork` orchestration skill ships here with integrated Systemcraft scaffolding and a native evidence/decision/test ledger. The upstream REA Investigator can be installed alongside it without rewriting or weakening its specialized investigation code. The two interact through an attributed case/report handoff, preserving independent verification scopes. This is deliberate: concatenating two large `SKILL.md` files would produce overlapping instructions and poorer maintainability.

The package is **offline and useful without REA** for source-level research, workflow design, scaffold/audit, and evidence tracking. **It does not embed the original REA implementation**, because that repository was not available as a local artifact during assembly; the optional `--rea-path` route uses your exact local checkout. For deep app/binary forensics, install REA and its upstream tools separately.

## Install

Requires Python 3.10+ and a local project directory.

```sh
# One skill, default (offline; no dependencies)
python3 install.py --agent codex --project /path/to/your/project
python3 install.py --agent claude --project /path/to/your/project
python3 install.py --agent cursor --project /path/to/your/project

# Full two-skill integration: pass an existing local clone of REA
python3 install.py --agent codex --project /path/to/your/project \
  --rea-path /path/to/rea-investigate

# Preview first; existing installations are protected by default
python3 install.py --agent codex --project /path/to/your/project --dry-run
```

The default installs to `.agents/skills/proofwork` on Codex, `.claude/skills/proofwork` on Claude Code, `.cursor/skills/proofwork` on Cursor. When `--rea-path` is supplied, it also installs the **original** REA skill in the adjacent `rea-investigate` folder. Files are copied into temporary directories before replacement; `--force` is required to replace existing skills.

## Example requests

```text
Use proofwork to investigate how our current onboarding system works.
Trace one user record across ingestion, verification and billing; cite the actual
source, document alternatives, implement one small safe improvement, and run
regression tests. Do not send messages or modify production data.
```

```text
Use proofwork to turn my repeated competitor research into the simplest working
process. First decide if a script or an agent is really needed. Deliver one
reproducible example with evidence citations and clearly labeled unknowns.
```

```text
Use proofwork for a verified handoff from rea-investigate's authorized
investigation of this desktop app. Preserve REA's original case, select a
minimum viable automation from the findings, and build a tested thin slice.
```

## Utilities

```sh
python3 skills/proofwork/scripts/proof.py doctor
python3 skills/proofwork/scripts/proof.py --help
python3 skills/proofwork/scripts/scaffold.py weekly-report --output ./workflows \
  --stages collect,transform,verify
python3 skills/proofwork/scripts/audit.py ./workflows/weekly-report
python3 -m unittest discover -s tests -v
```

`proof.py` persists a case ledger (copied evidence files + SHA-256, claims and alternatives, architectural decisions, recorded test logs, approvals, limitations). `check` verifies hashes, paths, references, and phase-specific minimum documentation; `report` generates a human-readable case report. These cannot prove a claim is true or a test was executed as recorded.

`scaffold.py` generates an **unimplemented blueprint**. `audit.py` checks basic structure, not functional correctness. Agent execution and specialist REA tooling depend on the tools and access available in the host coding agent.

## Decision pipeline

| Gate | Required result | What blocks progression |
|---|---|---|
| Scope | Narrow question, permissions, acceptance | Unbounded, unauthorized work |
| Investigate | Actual sources, locators, contradictory hypotheses | Unsupported causal narrative |
| Decide | Chosen implementation, credible alternative, kill criterion | Speculative architecture |
| Build | Small vertical slice, stable contracts | Unreviewed side effects |
| Verify | Real test logs and negative cases | Fabricated/unverified runs |
| Deliver | Audit trail, observed outcomes, limitations | Unqualified success claims |

## Tested boundaries

The built-in standard-library tools require local read/write permission and do not run unknown code, reach the network, create credentials, or obtain permissions. Sensitive material must be redacted before capture. REA itself requires separate authorization for live observation and may need `rea` CLI/providers for deep traces.

## Layout

```text
proofwork/
├── install.py
├── skills/
│   └── proofwork/
│       ├── SKILL.md
│       ├── scripts/{proof.py,scaffold.py,audit.py}
│       ├── references/{rea-interop,decisions,cli,design-rules,...}.md
│       └── assets/{OUTCOME,STAGE,REVIEW}.md
├── tests/
├── examples/
├── SOURCES.md
└── LICENSE
```

## Status

**v1.0.0 candidate.** CLI and installer are locally testable; there is no measured success-rate or cost-reduction claim for autonomous agents. Benchmarking on representative real tasks is future validation, not a completed result.

Licensed MIT. Original REA Investigator is preserved from your repository when you explicitly supply its checkout. Project is not affiliated with or endorsed by Matt Pocock, Jake Van Clief, or the Agent Skills specification maintainers.

See [DESIGN.md](DESIGN.md) for the architecture tradeoffs and limitations, and [EVALUATION.md](EVALUATION.md) for the agent-level benchmark protocol.
