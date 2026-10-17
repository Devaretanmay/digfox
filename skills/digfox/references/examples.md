# Worked examples

## Example A: weekly customer report

**Trigger**: Every Monday, analyst requests report. **Input**: authorized CSV exports. **Output**: checked one-page report with cited metrics. **Risk**: invented KPIs, stale data, sending without approval.

Decision: staged workflow if reports recur and humans review drafts. Otherwise a script for metrics plus a report template may suffice.

1. Ingest: Python validates source schema/dates, removes duplicates, produces `metrics.json`.
2. Interpret: Agent reads metrics and issue notes, drafts plain-language findings with references to metric keys.
3. Verify: Python checks that numeric statements refer to permitted metrics; reviewer confirms claims.
4. Deliver: Export file; any email/send is explicitly approved by the user.

Tests: missing CSV, zero rows, date mismatch, metric discrepancy, manipulated CSV text containing instructions. Measure rework and accuracy before optimizing prompts.

## Example B: research-to-technical-video

**Trigger**: Creator selects a technical concept. **Input**: public verified sources, editorial style guide. **Output**: reviewed voiceover, scene timing, source notes, final rendered video.

1. Research: gather authoritative sources and identify unresolved claims.
2. Script: tell a short story with one clear hook; attach a source-to-claim map.
3. Storyboard: link each spoken beat to a scene and motion cue.
4. Render: programmatic graphics and captions; verify timing and asset rights.
5. QA: check audio, subtitles, factual claims, and final watch-through before posting.

An agent should not generate purported footage, testimonials, or source facts. Publishing remains an approval-gated step.

## Example C: one-off CSV rename

Input is known; output is renaming headers and exporting another CSV once. **Decision**: write a small script, not a workflow architecture. This is the correct use of Digfox when the answer is *do less*.
