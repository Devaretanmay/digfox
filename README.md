<p align="center">
  <img src="assets/banner.jpg" alt="REA: Investigate Anything" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Devaretanmay/rea-investigate"><img src="https://img.shields.io/badge/tests-12%2F12%20passing-brightgreen.svg" alt="Tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/morluto/rea"><img src="https://img.shields.io/badge/instrument-REA%20CLI-orange.svg" alt="REA CLI"></a>
  <a href="https://github.com/Devaretanmay/rea-investigate"><img src="https://img.shields.io/badge/agent%20skill-Claude%20%7C%20Codex%20%7C%20Antigravity-purple.svg" alt="Supported Agents"></a>
</p>

---

# REA Investigator

**One command -> a planned investigation across 13 capabilities -> an evidence-backed technical report.**

**REA Investigator** is a unified, production-grade **Agent Skill** (`rea-investigate`) compatible with Claude Code, Codex, Antigravity, and tools supporting the open Agent Skills specification. 

Instead of juggling fragmented prompts or shallow summaries, REA Investigator equips coding agents with a structured 4-phase lifecycle: **Plan**, **Trace**, **Verify**, and **Report**, backed by an immutable SHA-256 evidence ledger and adversarial auditing gates.

---

## Quick Invocation

Once installed, invoke the skill directly inside your agent:

```bash
/rea-investigate /Applications/Example.app: explain exactly how the Export PDF button works, from click to output file, and produce a report.
```

Or target specific bundles, builds, or network flows:

```bash
# Static bundle inspection
/rea-investigate ./app.asar: trace local search end to end. Static only, no execution.

# Version and release comparison
/rea-investigate ./v1.0.apk ./v2.0.apk: compare the authentication feature and document evidence.

# Web application UI interaction trace
/rea-investigate https://example.test: investigate the public request flow with browser observation.
```

The agent autonomously categorizes the target, evaluates the 13 capabilities, invokes local REA/system tools, logs cryptographic evidence hashes, challenges conclusions adversarially, and renders a comprehensive `REPORT.md`.

---

## Investigation Lifecycle

```text
               REQUEST: /rea-investigate <target>
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. PLAN: Scope, Consent & Target Identity (S01, S02)        │
│    SHA-256 fingerprinting, directory manifest, boundaries    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. TRACE: Route to Applicable Capabilities (S03-S10, S13)   │
│    JS/Electron · Web UI · Network/HAR · Native Mach-O/ELF   │
│    Android APK · .NET PE · Process capture · Build diff     │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. VERIFY: Adversarial Evidence Audit (S12)                 │
│    Skeptical counteranalysis: observation vs hypothesis     │
│    Validation gates: no unverified edges, no missing hashes  │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. REPORT: Verified Delivery & Case Artifacts               │
│    13-capability ledger + claim provenance + REPORT.md      │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

Install `rea-investigate` into your local project environment with a single command:

```bash
# Install for Claude Code
python3 install.py --agent claude --project /path/to/your/project

# Install for Codex / Agent Skills convention
python3 install.py --agent codex --project /path/to/your/project

# Dry run preview
python3 install.py --agent claude --project /path/to/your/project --dry-run
```

The installer installs cleanly to `<project>/.claude/skills/rea-investigate` or `<project>/.agents/skills/rea-investigate` and never silently overwrites existing files without `--force`.

### Underlying REA Tools (Optional per modality)
REA Investigator orchestrates the investigation process. When decompilation, AST parsing, or network capture is needed, configure the upstream [REA CLI](https://github.com/morluto/rea):

```bash
npm install --global rea-agents
rea --help
rea capabilities --json
rea providers --json
```

---

## The 13 Capabilities

Every investigation rigorously assesses all 13 capabilities, categorizing each as `done`, `not-applicable` (with concrete rationale), or `blocked` (with missing prerequisites):

| Stage | Capability | Description | Verification Gate |
| :---: | :--- | :--- | :--- |
| **S01** | Scope & Authorization | Target definition, bounds, and consent | Falsifiable question & permissions |
| **S02** | Artifact Mapping | File/bundle classification & hash manifest | SHA-256 verified; no guessed formats |
| **S03** | JS/Electron Trace | Renderer, preload, main IPC, and route trace | Graph source locator per hop |
| **S04** | Browser Observation | Web interaction, DOM changes, and network | Before/action/after state delta |
| **S05** | Network Reconstruction | Offline HAR / MITM capture request-response | Credential scrubbed; record ordinals |
| **S06** | Native Binary Analysis | Mach-O, ELF, PE functions and xrefs | Decompiler checked vs instructions |
| **S07** | Android Package (APK) | Manifest, DEX classes, methods & JNI | Decompiled class + method locators |
| **S08** | Managed .NET Analysis | CIL metadata, types, and P/Invoke boundaries | Verified PE/CLI token mapping |
| **S09** | Process Capture | CLI invocation, stdout/stderr, file effects | Full input, output & exit code record |
| **S10** | Build Comparison | Differential analysis between two releases | Paired coverage; proved diffs |
| **S11** | Behavior Synthesis | Clean-room behavioral contract specification | Formal contract tests (opt-in) |
| **S12** | Adversarial Audit | Skeptical review challenging all claims | `notes/audit.md` counter-hypotheses |
| **S13** | Firmware Inventory | Firmware partition and embedded image map | Offset map & entropy without flashing |

---

## Case Ledger and Strict Audit

REA Investigator includes a built-in standard-library case ledger CLI (`case.py`) to enforce scientific rigor:

```bash
# Initialize a new isolated case
python3 skills/rea-investigate/scripts/case.py init \
  --target /path/to/artifact \
  --question "How does feature X authenticate?" \
  --out ./cases/feature-x

# Register evidence, claims, and notes
python3 skills/rea-investigate/scripts/case.py stage ./cases/feature-x S01 done
python3 skills/rea-investigate/scripts/case.py render ./cases/feature-x

# Run strict structural validation gate
python3 skills/rea-investigate/scripts/case.py check ./cases/feature-x --strict
```

The strict check automatically fails if:
- Any stage is left pending or unreasoned.
- Claims cite unregistered evidence IDs.
- Evidence files have mismatched SHA-256 digests.
- Required notes (`overview`, `architecture`, `trace`, `verification`, `limitations`, `audit`) are missing.

---

## Repository Structure

```text
rea-investigate/
├── .gitignore
├── LICENSE                               (MIT License)
├── README.md                             (Documentation & quickstart)
├── install.py                            (Agent installer script)
├── assets/
│   └── banner.jpg                        (Project header illustration)
├── skills/
│   └── rea-investigate/
│       ├── SKILL.md                      (Primary Agent Skill instruction)
│       ├── assets/                       (Synthetic & excerpt reports)
│       ├── references/                   (Capabilities, evidence rules, guides)
│       │   ├── capabilities.md
│       │   ├── evidence.md
│       │   ├── report.md
│       │   ├── tooling.md
│       │   └── techniques/               (Applications, binaries, change-and-rebuild)
│       └── scripts/
│           ├── case.py                   (Deterministic case ledger & auditor)
│           └── rea_payload.py            (JSON payload schemas)
└── tests/
    └── test_pack.py                      (Unit test suite: 12 tests)
```

---

## Testing

Run the local test suite using Python standard library:

```bash
python3 -m unittest discover -s tests -v
```

All 12 tests validate case initialization, evidence hashing, integrity verification, and strict qualification gates.

---

## Boundaries and Ethics

- Analyze **only** software, captures, and systems you own or have explicit authorization to inspect.
- Never bypass technical protections, extract third-party secrets, or exfiltrate credentials.
- Process capture executes with local user privileges; sandbox and isolate when needed.
- REA Investigator is independently authored and not officially affiliated with or endorsed by upstream tool authors.
