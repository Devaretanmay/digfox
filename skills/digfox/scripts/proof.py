#!/usr/bin/env python3
"""Digfox: evidence-to-delivery ledger. Python 3.10+, standard library only.

Never executes analyzed targets, contacts networks, or changes external systems.
It records claims and checks integrity, not their truth.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

SCHEMA = 1
PHASES = ("scope", "investigate", "decide", "build", "verify", "deliver")
KIND = ("observation", "source", "test-log", "rea-report", "artifact")
CONFIDENCE = ("observed", "inferred", "unresolved")
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
ID = re.compile(r"^(E|C|D|T)\d{3,}$")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def must_be_case(root: Path) -> Path:
    root = root.expanduser().resolve()
    if not (root / "case.json").is_file():
        raise ValueError(f"Not a Digfox case: {root}")
    return root


def read_case(root: Path) -> dict:
    state = json.loads((root / "case.json").read_text(encoding="utf-8"))
    if state.get("schema") != SCHEMA:
        raise ValueError("Unsupported case schema; do not rewrite an unknown case")
    return state


def write_case(root: Path, state: dict) -> None:
    """Atomic replace after fsync; no silent partial state on normal failures."""
    path = root / "case.json"
    fd, tmp = tempfile.mkstemp(prefix=".case-", suffix=".json", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def case_init(out: Path, question: str, target: str, authorized: bool, intent: str) -> Path:
    root = out.expanduser().resolve()
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite existing case: {root}")
    if len(question.strip()) < 12:
        raise ValueError("Provide a concrete falsifiable question (at least 12 characters)")
    if not target.strip():
        raise ValueError("Target / input description is required")
    if intent not in ("investigate", "design", "build", "audit", "extract"):
        raise ValueError("Invalid intent")
    root.mkdir(parents=True)
    try:
        (root / "evidence").mkdir()
        (root / "outputs").mkdir()
        (root / "notes").mkdir()
        (root / "notes" / "ASSUMPTIONS.md").write_text("# Assumptions and limitations\n\n", encoding="utf-8")
        write_case(root, {
            "schema": SCHEMA, "created_utc": now(), "question": question.strip(),
            "target": target.strip(), "intent": intent, "authorized": authorized,
            "phase": "scope", "phase_history": [{"phase": "scope", "at": now()}],
            "evidence": [], "claims": [], "decisions": [], "tests": [],
            "approvals": [], "constraints": [], "limitations": []
        })
    except BaseException:
        shutil.rmtree(root)
        raise
    return root


def newid(items: list, prefix: str) -> str:
    used = {x.get("id") for x in items}
    for number in range(1, 1000000):
        candidate = f"{prefix}{number:03d}"
        if candidate not in used:
            return candidate
    raise ValueError("Too many records")


def add_file(root: Path, file: Path, kind: str, locator: str, note: str) -> str:
    root = must_be_case(root)
    if kind not in KIND:
        raise ValueError("Invalid evidence kind")
    supplied = file.expanduser()
    if supplied.is_symlink():
        raise ValueError("Refusing a symlink as an evidence source")
    src = supplied.resolve(strict=True)
    if not src.is_file():
        raise ValueError("Evidence must be a regular file")
    if not locator.strip() or not note.strip():
        raise ValueError("An evidence locator and description are required")
    if src.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("Evidence exceeds 100 MiB: keep a redacted excerpt or externally managed manifest")
    if (root / "evidence").is_symlink():
        raise ValueError("Refusing a symlinked evidence directory")
    state = read_case(root)
    evidence_id = newid(state["evidence"], "E")
    # Never store original basename: filenames may contain sensitive identifiers.
    extension = src.suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension):
        extension = ".bin"
    dest = root / "evidence" / (evidence_id + extension)
    if dest.exists():
        raise FileExistsError(dest)
    # Copy bytes without following symlinks at destination.
    shutil.copyfile(src, dest)
    digest = sha256(dest)
    if digest != sha256(src):
        dest.unlink()
        raise ValueError("Evidence copy changed during capture")
    state["evidence"].append({
        "id": evidence_id, "kind": kind, "path": str(dest.relative_to(root)),
        "sha256": digest, "bytes": dest.stat().st_size,
        "locator": locator.strip(), "note": note.strip(), "captured_utc": now()
    })
    write_case(root, state)
    return evidence_id


def add_claim(root: Path, statement: str, refs: list[str], confidence: str,
              locator: str, alternative: str, falsifier: str) -> str:
    root = must_be_case(root)
    state = read_case(root)
    if confidence not in CONFIDENCE:
        raise ValueError("Invalid confidence")
    if len(statement.strip()) < 8:
        raise ValueError("Claim statement is too short")
    if not refs:
        raise ValueError("Every claim must reference evidence")
    known = {x["id"] for x in state["evidence"]}
    if len(set(refs)) != len(refs) or not set(refs).issubset(known):
        raise ValueError("Unknown or duplicated evidence IDs")
    if confidence == "observed" and (not locator.strip() or not alternative.strip() or not falsifier.strip()):
        raise ValueError("Observed claims require precise locator, competing explanation and falsification test")
    claim_id = newid(state["claims"], "C")
    state["claims"].append({
        "id": claim_id, "statement": statement.strip(), "evidence": refs,
        "confidence": confidence, "locator": locator.strip(),
        "alternative": alternative.strip(), "falsifier": falsifier.strip(), "created_utc": now()
    })
    write_case(root, state)
    return claim_id


def add_decision(root: Path, selection: str, alternatives: list[str], reasoning: str,
                 refs: list[str], reversible: bool, kill_condition: str) -> str:
    root = must_be_case(root)
    state = read_case(root)
    if not selection.strip() or not reasoning.strip() or not kill_condition.strip():
        raise ValueError("Decision requires choice, tradeoff reasoning and stop/revisit condition")
    if not alternatives or not all(s.strip() for s in alternatives):
        raise ValueError("Include at least one genuine alternative")
    if selection in alternatives:
        raise ValueError("Chosen path cannot be repeated as an alternative")
    all_refs = {x["id"] for x in state["claims"]}
    if not set(refs).issubset(all_refs):
        raise ValueError("Decision references unknown claims")
    decision_id = newid(state["decisions"], "D")
    state["decisions"].append({
        "id": decision_id, "selection": selection.strip(), "alternatives": alternatives,
        "reasoning": reasoning.strip(), "claims": refs, "reversible": reversible,
        "revisit_when": kill_condition.strip(), "created_utc": now()
    })
    write_case(root, state)
    return decision_id


def record_test(root: Path, label: str, log: Path, exit_code: int, scope: str) -> str:
    root = must_be_case(root)
    if not label.strip() or not scope.strip():
        raise ValueError("Test label and scope are required")
    evidence_id = add_file(root, log, "test-log", f"test: {label}", scope)
    state = read_case(root)
    test_id = newid(state["tests"], "T")
    state["tests"].append({"id": test_id, "label": label.strip(), "evidence": evidence_id,
                           "exit_code": exit_code, "scope": scope.strip(), "recorded_utc": now(),
                           "attestation": "reported by operator; log integrity checked, execution not independently attested"})
    write_case(root, state)
    return test_id


def add_approval(root: Path, operation: str, reason: str) -> None:
    root = must_be_case(root)
    allowed = ("active-observation", "execute-unknown-target", "send", "publish", "spend", "deploy", "delete", "sensitive-data-sharing")
    if operation not in allowed or not reason.strip():
        raise ValueError(f"Approval must name one of {', '.join(allowed)} and a reason")
    state = read_case(root)
    # A recorded approval is an audit statement, not cryptographic identity proof.
    state["approvals"].append({"operation": operation, "reason": reason.strip(), "recorded_utc": now()})
    write_case(root, state)


def safe_evidence_path(root: Path, path: str) -> Path | None:
    rel = Path(path)
    if rel.is_absolute() or any(p in ("..", "") for p in rel.parts) or len(rel.parts) != 2 or rel.parts[0] != "evidence":
        return None
    candidate = root / rel
    if candidate.is_symlink() or not candidate.is_file():
        return None
    if candidate.resolve().parent != (root / "evidence").resolve():
        return None
    return candidate


def check(root: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    root = must_be_case(root)
    s = read_case(root)
    errors, warnings = [], []
    ids = set()
    for record in s.get("evidence", []):
        rid = record.get("id", "")
        if rid in ids or not ID.fullmatch(rid) or not rid.startswith("E"):
            errors.append(f"Duplicate or invalid evidence ID: {rid}")
        ids.add(rid)
        path = safe_evidence_path(root, record.get("path", ""))
        if path is None or sha256(path) != record.get("sha256"):
            errors.append(f"Evidence {rid}: missing, unsafe path or SHA-256 mismatch")
        if not record.get("locator") or not record.get("note"):
            errors.append(f"Evidence {rid}: locator/note missing")
    claim_ids = set()
    for c in s.get("claims", []):
        cid = c.get("id", "")
        if cid in claim_ids or not ID.fullmatch(cid) or not cid.startswith("C"):
            errors.append(f"Duplicate or invalid claim ID: {cid}")
        claim_ids.add(cid)
        if not c.get("statement") or not c.get("evidence") or not set(c["evidence"]).issubset(ids):
            errors.append(f"Claim {cid}: missing statement or evidence references")
        if c.get("confidence") not in CONFIDENCE:
            errors.append(f"Claim {cid}: invalid confidence")
        if c.get("confidence") == "observed" and not all(c.get(x) for x in ("locator", "alternative", "falsifier")):
            errors.append(f"Claim {cid}: missing observed-claim challenge")
    for d in s.get("decisions", []):
        if not d.get("selection") or not d.get("alternatives") or not d.get("reasoning") or not d.get("revisit_when"):
            errors.append(f"Decision {d.get('id')}: lacks choice/tradeoff/revisit criteria")
        if not set(d.get("claims", [])).issubset(claim_ids):
            errors.append(f"Decision {d.get('id')}: references unknown claims")
    for t in s.get("tests", []):
        if t.get("evidence") not in ids or not isinstance(t.get("exit_code"), int):
            errors.append(f"Test {t.get('id')}: invalid log or result")
    if s.get("phase") not in PHASES:
        errors.append("Invalid phase")
    if s.get("intent") == "investigate" and not s.get("authorized"):
        warnings.append("Target authorization is not recorded; restrict to authorized passive work")
    if s["phase"] in PHASES[3:] and not s.get("decisions"):
        errors.append("Decision gate: choose a route and document alternatives before build")
    if s["phase"] in PHASES[4:] and not any(t.get("exit_code") == 0 for t in s.get("tests", [])):
        errors.append("Verification gate: at least one recorded passing test is required")
    if s["phase"] in PHASES[4:] and not any(t.get("exit_code") != 0 for t in s.get("tests", [])):
        warnings.append("No recorded failing/negative test; edge cases may be untested")
    if s["phase"] in PHASES[4:] and not s.get("claims"):
        warnings.append("No evidence-backed claims; test results may lack interpretation")
    if not s.get("evidence"):
        warnings.append("No evidence registered")
    if not s.get("claims"):
        warnings.append("No claims registered")
    if not s.get("decisions"):
        warnings.append("No design decision logged")
    if not s.get("tests"):
        warnings.append("No execution tests recorded")
    if s["phase"] == "deliver":
        if not s.get("limitations"):
            errors.append("Delivery gate: explicit limitations required")
        if not (root / "REPORT.md").is_file():
            errors.append("Delivery gate: render report before delivery")
    if strict and (warnings or errors):
        errors.extend(f"Strict mode: {w}" for w in warnings)
        warnings = []
    return errors, warnings


def phase_change(root: Path, phase: str) -> None:
    root = must_be_case(root)
    s = read_case(root)
    index = PHASES.index(s["phase"])
    if phase not in PHASES or PHASES.index(phase) != index + 1:
        raise ValueError("Only sequential forward phase transitions are allowed")
    if phase == "decide" and not s["evidence"]:
        raise ValueError("Investigation gate: register some evidence, or stay in investigate")
    if phase == "build" and not s["decisions"]:
        raise ValueError("Decision gate: record a decision with a rejected alternative")
    if phase == "verify" and not s["tests"]:
        raise ValueError("Verification gate: record an actual test log before advancing")
    if phase == "deliver":
        if not s["limitations"]:
            raise ValueError("Delivery gate: document limitations")
        if not (root / "REPORT.md").is_file():
            raise ValueError("Delivery gate: render report first")
    s["phase"] = phase
    s["phase_history"].append({"phase": phase, "at": now()})
    write_case(root, s)
    errors, warnings = check(root)
    # Roll back failed transition. Do not mistake warnings for failures.
    if errors:
        s["phase"] = PHASES[index]
        s["phase_history"].pop()
        write_case(root, s)
        raise ValueError("Phase gate failed: " + "; ".join(errors))


def escape_md(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").replace("`", "'")


def report(root: Path) -> Path:
    root = must_be_case(root)
    s = read_case(root)
    errors, warnings = check(root)
    lines = ["# Digfox case report", "", f"**Question:** {escape_md(s['question'])}",
             f"**Target:** {escape_md(s['target'])}", f"**Mode:** {s['intent']}",
             f"**Phase:** {s['phase']}", f"**Recorded authorization:** {s['authorized']}",
             "", "## Evidence (integrity-checked records)", "",
             "| ID | Kind | Captured item | Locator |", "|---|---|---|---|"]
    for e in s["evidence"]:
        lines.append(f"| {e['id']} | {e['kind']} | `{e['path']}` SHA256 `{e['sha256'][:12]}…` | {escape_md(e['locator'])} |")
    lines.extend(["", "## Claims (claims are not automatically verified by hashes)", "",
                  "| ID | Status | Assertion | Evidence | Competing explanation | Falsifier |",
                  "|---|---|---|---|---|---|"])
    for c in s["claims"]:
        lines.append(f"| {c['id']} | {c['confidence']} | {escape_md(c['statement'])} | {','.join(c['evidence'])} | {escape_md(c['alternative'])} | {escape_md(c['falsifier'])} |")
    lines.extend(["", "## Decisions and rejected alternatives", ""])
    for d in s["decisions"]:
        lines.extend([f"### {d['id']}: {d['selection']}",
                      f"- Alternatives: {', '.join(d['alternatives'])}",
                      f"- Reasoning: {d['reasoning']}", f"- Supported claims: {', '.join(d['claims']) or 'None (explicit assumption)'}",
                      f"- Reversible: {d['reversible']}", f"- Revisit if: {d['revisit_when']}", ""])
    lines.extend(["## Tests (operator-recorded execution)", "", "| ID | Test | Exit code | Log | Coverage |",
                  "|---|---|---|---|---|"])
    for t in s["tests"]:
        lines.append(f"| {t['id']} | {escape_md(t['label'])} | {t['exit_code']} | {t['evidence']} | {escape_md(t['scope'])} |")
    lines.extend(["", "## Approvals on record (not proof of user identity)", ""])
    lines.extend(f"- {a['operation']}: {a['reason']}" for a in s["approvals"])
    lines.extend(["", "## Limitations and unresolved risks", ""])
    lines.extend(f"- {x}" for x in s["limitations"])
    lines.extend(["", "## Integrity and quality gates", ""])
    lines.extend(f"- ERROR: {x}" for x in errors)
    lines.extend(f"- WARNING: {x}" for x in warnings)
    if not errors and not warnings:
        lines.append("- No structural or evidence-integrity findings.")
    lines.extend(["", "**Scope of verification:** SHA-256 checks establish saved-file integrity only; "
                  "they do not certify source authenticity, semantic truth, authorization, or actual runtime execution.", ""])
    path = root / "REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def import_rea(root: Path, rea_case: Path) -> list[str]:
    """Ingest REA artifacts preserving attribution; never re-label as independently verified."""
    root = must_be_case(root)
    rea = rea_case.expanduser().resolve(strict=True)
    if not rea.is_dir() or not (rea / "case.json").is_file() or not (rea / "REPORT.md").is_file():
        raise ValueError("REA case must contain case.json and REPORT.md. Run REA render first.")
    refs = []
    for name, kind in (("case.json", "source"), ("REPORT.md", "rea-report")):
        refs.append(add_file(root, rea / name, kind, f"REA case {rea.name}/{name}",
                             "Imported from REA Investigator; provenance only; independently review its claim citations"))
    return refs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init", help="Create an immutable-name case folder")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--intent", default="investigate", choices=("investigate", "design", "build", "audit", "extract"))
    p.add_argument("--authorized", action="store_true", help="Record operator attestation of target authorization")
    p = sub.add_parser("evidence", help="Copy and hash a local evidence file")
    p.add_argument("case", type=Path)
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--kind", choices=KIND, default="source")
    p.add_argument("--locator", required=True)
    p.add_argument("--note", required=True)
    p = sub.add_parser("claim", help="Register evidence-backed claim")
    p.add_argument("case", type=Path)
    p.add_argument("--statement", required=True)
    p.add_argument("--evidence", nargs="+", required=True)
    p.add_argument("--confidence", choices=CONFIDENCE, default="inferred")
    p.add_argument("--locator", default="")
    p.add_argument("--alternative", default="")
    p.add_argument("--falsifier", default="")
    p = sub.add_parser("decision", help="Register decision with trade-offs")
    p.add_argument("case", type=Path)
    p.add_argument("--choose", required=True)
    p.add_argument("--instead-of", nargs="+", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--claims", nargs="*", default=[])
    p.add_argument("--reversible", action="store_true")
    p.add_argument("--revisit-when", required=True)
    p = sub.add_parser("test", help="Register a real saved test log (does not execute tests)")
    p.add_argument("case", type=Path)
    p.add_argument("--label", required=True)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--exit-code", required=True, type=int)
    p.add_argument("--scope", required=True)
    p = sub.add_parser("approve", help="Record a human-authorized side-effect boundary")
    p.add_argument("case", type=Path)
    p.add_argument("--operation", required=True)
    p.add_argument("--reason", required=True)
    p = sub.add_parser("limit", help="Record uncertainty/limitation")
    p.add_argument("case", type=Path)
    p.add_argument("--text", required=True)
    p = sub.add_parser("phase", help="Advance by one gated lifecycle state")
    p.add_argument("case", type=Path)
    p.add_argument("to", choices=PHASES)
    p = sub.add_parser("import-rea", help="Import REA case and report with original attribution")
    p.add_argument("case", type=Path)
    p.add_argument("--rea-case", type=Path, required=True)
    p = sub.add_parser("check", help="Check evidence integrity, references and gates")
    p.add_argument("case", type=Path)
    p.add_argument("--strict", action="store_true")
    p = sub.add_parser("report", help="Render readable REPORT.md")
    p.add_argument("case", type=Path)
    p = sub.add_parser("doctor", help="Check local runtime prerequisites")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "init":
            print(case_init(args.out, args.question, args.target, args.authorized, args.intent))
        elif args.cmd == "evidence":
            print(add_file(args.case, args.file, args.kind, args.locator, args.note))
        elif args.cmd == "claim":
            print(add_claim(args.case, args.statement, args.evidence, args.confidence,
                            args.locator, args.alternative, args.falsifier))
        elif args.cmd == "decision":
            print(add_decision(args.case, args.choose, args.instead_of, args.why,
                               args.claims, args.reversible, args.revisit_when))
        elif args.cmd == "test":
            print(record_test(args.case, args.label, args.log, args.exit_code, args.scope))
        elif args.cmd == "approve":
            add_approval(args.case, args.operation, args.reason)
            print("Approval recorded (not identity-verified)")
        elif args.cmd == "limit":
            if not args.text.strip():
                raise ValueError("Empty limitation")
            root = must_be_case(args.case)
            state = read_case(root)
            state["limitations"].append(args.text.strip())
            write_case(root, state)
            print("Limitation recorded")
        elif args.cmd == "phase":
            phase_change(args.case, args.to)
            print(f"Phase: {args.to}")
        elif args.cmd == "import-rea":
            print("Imported REA references: " + ", ".join(import_rea(args.case, args.rea_case)))
        elif args.cmd == "check":
            errors, warnings = check(args.case, args.strict)
            for e in errors: print("ERROR: " + e)
            for w in warnings: print("WARN: " + w)
            print(f"Gate result: {len(errors)} errors, {len(warnings)} warnings")
            return 1 if errors else 0
        elif args.cmd == "report":
            print(report(args.case))
        elif args.cmd == "doctor":
            print("Python: " + sys.version.split()[0] + " (stdlib tools available)")
            print("REA CLI (optional): " + (shutil.which("rea") or "not found"))
            print("Digfox: file-backed audit only; no direct model, network, or execution integration")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
