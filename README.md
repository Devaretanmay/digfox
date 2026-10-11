# REA Investigator

**One command → a planned investigation across 13 capabilities → evidence-backed technical report.**

This is a **single Agent Skill**, `rea-investigate`, for Claude Code, Codex and tools compatible with the open Agent Skills convention. It does **not** invoke or depend on REA's shipped `reverse-engineer-anything` skill, nor does it install any of the former 13-skills pack. Everything is led by one `SKILL.md`; subject-specific reference files are ordinary documentation, **not extra skills**.

Inspired by Matt Pocock's engineering approach: a user-invoked skill, a stable procedure, explicit exit criteria, progressive disclosure of rare branches, small deterministic helpers and reproducible primary sources. It is independently written, not a copy or endorsement.

## Usage

After installing, type in your coding agent:

```
/rea-investigate /Applications/Example.app — explain exactly how the Export PDF button works, from click to output file, and produce a report.
```

Or:

```
/rea-investigate /path/to/example.asar — trace local search end to end. Static only, no execution.
/rea-investigate /path/to/old.apk /path/to/new.apk — compare the login feature and show the evidence.
/rea-investigate https://example.test — investigate the public UI request flow, with browser capture only if authorized.
```

The agent identifies the applicable branches, uses your local REA CLI/MCP capabilities and other approved inspection tools, keeps source Evidence and a claim ledger, audits gaps, then saves **REPORT.md** in a separate case folder. A feature reconstruction is optional and requires an explicit instruction to write code.

## Install one skill

Download/unzip this repository, then in its root:

```sh
python3 install.py --agent codex --project /path/to/your/project
# or
python3 install.py --agent claude --project /path/to/your/project
```

This copies **one directory** to `<project>/.agents/skills/rea-investigate` or `<project>/.claude/skills/rea-investigate`. It refuses to replace an existing skill unless you add `--force`. You can preview paths with `--dry-run`.

If published as a GitHub repo, the directory layout also supports distribution through the community agent-skills installer, e.g. `npx skills add <your-github-user>/<your-repo> --skill rea-investigate`. **No GitHub release exists for this generated ZIP.**

### Instrument setup (separate)

The skill is the orchestration process, **not a decompiler, browser or execution sandbox**. Install and configure REA separately to access its actual analysis tools:

```sh
# REA requires a supported recent Node.js runtime and npm.
npm install --global rea-agents
rea --help
rea capabilities --json
rea providers --json
```

The native providers (Hopper/Ghidra/IDA), JADX/JDK, compatible browser, firmware extractor and target host capabilities depend on the selected stage. Consult the original project's current instructions: https://github.com/morluto/rea. REA's `setup` command may also add its own upstream skill; it is **not required** to install this single skill. For MCP-based operation, configure the upstream REA MCP server using its documented setup if you prefer, while avoiding duplicate skill entry points.

## What happens during the invocation

```text
REQUEST /rea-investigate
     |
     v
Scope + consent + precise question (S01)
     |
     v
Artifact / website identification (S02)
     |
     +--> Applicable branches only (S03-S10, S13)
     |    JS/Electron | Web/UI | HAR/network | native
     |    APK | .NET | process | build/version | firmware
     |                   |
     |                   v
     |    Exact evidence, trace and reproducible experiments
     |
     +--> Optional independent reimplementation (S11, explicit request)
     |
     v
Adversarial evidence audit (S12)
     |
     v
13-row coverage ledger + claims + references + REPORT.md
```

The system **accounts for all 13** rather than pointlessly trying to run Android analysis against an Electron app. Every stage ends `done`, `not-applicable` with a reason or `blocked` with a reason. Missing tooling is **blocked**, never claimed to have been run. The report makes coverage transparent.

## What the report contains

- Executive answer and artifact identity, including SHA-256 when locally available.
- Stage-by-stage coverage (13/13 assessed) with sources/blocked reasons.
- Architecture/trust-boundary map and trigger-to-side-effect trace.
- Network captures, version changes or parity results if pertinent.
- Explicit tests, repro commands, supported claim IDs with evidence locators and SHA-256 register.
- A skeptical counteranalysis and remaining uncertainty.

An illustrative **full generated report** is in `skills/rea-investigate/assets/example-synthetic-report.md` (explicitly synthetic, not evidence from a real app).

## Case lifecycle helpers

The agent runs these internally. They are safe to run manually too. Resolve them relative to the installed skill directory:

```sh
python3 skills/rea-investigate/scripts/case.py init \
  --target /absolute/path/to/app.asar \
  --question 'Where does Export write its output?' \
  --authorization 'I own this build; static inspection only' \
  --out /tmp/rea-export-case

python3 skills/rea-investigate/scripts/case.py stage /tmp/rea-export-case S01 done
# The agent then records evidence/claim IDs, writes notes, and closes stages.
python3 skills/rea-investigate/scripts/case.py render /tmp/rea-export-case
python3 skills/rea-investigate/scripts/case.py check /tmp/rea-export-case --strict
```

`case.py` is a deterministic **ledger/report generator**, not a wrapper that automatically reverse-engineers arbitrary code. Actual analysis is performed by the coding agent using REA and available approved tools. The strict check catches missing stages, source corruption, unsubstantiated registered claims and empty reports; it cannot prove semantic correctness on its own. If the platform/provider cannot perform an intended check, expect a **qualified report with explicit blocked stages**, not fictitious success.

## Project files

```
rea-one-skill/
├── README.md
├── install.py
├── tests/
└── skills/
    └── rea-investigate/
        ├── SKILL.md          # the only invocable skill
        ├── references/       # progressive disclosure, not skills
        │   ├── capabilities.md
        │   ├── evidence.md
        │   ├── report.md
        │   ├── tooling.md
        │   └── techniques/
        │       ├── applications.md
        │       ├── binaries.md
        │       └── change-and-rebuild.md
        ├── scripts/
        │   ├── case.py       # scope / coverage / evidence / claims / report / strict check
        │   └── rea_payload.py # constructs documented trace / view / compare JSON
        └── assets/
            ├── example-report-excerpt.md
            └── example-synthetic-report.md
```

## Safety and disclosure

Only inspect targets you own or are authorized to analyze. Active execution and authenticated capture require separate approval. Keep secrets, cookie values, API credentials, private captures and personal data out of reports and shared archives. Reverse engineering can carry legal and IP restrictions; reproductions should independently implement authorized observable behavior. REA and Matt Pocock's skills are separate projects; neither has endorsed this package.

## Verification

Run `python3 -m unittest discover -s tests -v` to validate the local CLI lifecycle and guards. These tests do **not** run REA against an actual app, and none should be represented as native decompilation or browser parity coverage.
