# Troubleshooting Fox skills

This guide helps you resolve common issues when installing or using Fox, Fox Explore, and Fox Review.

---

## 1. My Coding Agent Does Not Recognize the Skill

### Symptom
You type `/fox`, `/fox-explore`, or `/fox-review`, or prompt your agent, but it responds as if the skill is not installed.

### Solutions
1. **Restart your coding agent**:
   Most coding agents (including Claude Code, Cursor, Codex, and Antigravity) only scan their skills folder when a session starts. Close and re-open the chat window or restart the agent process.
2. **Verify installation location**:
   Check that the skill exists in your project workspace:
   - **Google Antigravity / OpenAI Codex**: `.agents/skills/fox`, `.agents/skills/fox-explore`, or `.agents/skills/fox-review`
   - **Claude Code**: `.claude/skills/fox`, `.claude/skills/fox-explore`, or `.claude/skills/fox-review`
   - **Cursor**: `.cursor/skills/fox`, `.cursor/skills/fox-explore`, or `.cursor/skills/fox-review`
3. **Explicitly reference the skill file**:
   If your agent UI does not support slash commands, simply paste your task prompt along with:
   ```text
   Use the instructions in .agents/skills/fox/SKILL.md to investigate this issue.
   ```

---

## 2. Re-installing or Updating a Skill Fails

### Symptom
Running `install.py` prints:
`ERROR: ... already exists; pass --force to replace`

### Solution
Pass `--force` to safely overwrite an existing installation:
```bash
python3 install.py --agent antigravity --skill all --force
```
In interactive mode (`python3 install.py`), the installer will automatically detect existing files and prompt you before replacing them.

---

## 3. Permission Denied During Installation

### Symptom
The installer reports permission errors when writing to the project or global directory.

### Solutions
- Ensure you have write permissions to the project directory:
  ```bash
  chmod -R u+w .agents/
  ```
- For global installation on Google Antigravity, ensure your user owns `~/.gemini/config/skills`:
  ```bash
  mkdir -p ~/.gemini/config/skills
  ```

---

## 4. How to Confirm the Skill is Active

Ask your agent to solve a bug or explore code. Look for these signs in its response:

- **Fox**: The agent grounds the problem first, writes a reproducer, traces to the owning layer, applies a minimal fix, and verifies counterexamples.
- **Fox Explore**: The agent provides grounded answers citing specific file paths, separates facts from inference, and advises on trade-offs without editing code.
- **Fox Review**: The agent resolves a diff or commit target, traces connected behavior, reports evidence-backed findings first, and does not change files.

If Fox Review starts repairing code, stop the run and invoke it explicitly with: `Use fox-review in read-only mode. Report findings only.` Use `fox` separately when you authorize repairs.

If you need further help, open an issue at:
https://github.com/Devaretanmay/fox/issues
