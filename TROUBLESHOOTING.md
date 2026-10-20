# Troubleshooting Fox & Fox Graph

This guide helps you resolve common issues when installing or using Fox and Fox Graph.

---

## 1. My Coding Agent Does Not Recognize the Skill

### Symptom
You type `/fox` or prompt your agent, but it responds as if the skill is not installed.

### Solutions
1. **Restart your coding agent**:
   Most coding agents (including Claude Code, Cursor, Codex, and Antigravity) only scan their skills folder when a session starts. Close and re-open the chat window or restart the agent process.
2. **Verify installation location**:
   Check that the skill exists in your project workspace:
   - **Google Antigravity / OpenAI Codex**: `.agents/skills/fox` or `.agents/skills/fox-graph`
   - **Claude Code**: `.claude/skills/fox` or `.claude/skills/fox-graph`
   - **Cursor**: `.cursor/skills/fox` or `.cursor/skills/fox-graph`
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

## 3. Fox Graph: GitNexus Provider Not Found

### Symptom
When running Fox Graph on TypeScript, JavaScript, Go, or Rust projects, you see:
`npx: command not found` or a provider initialization warning.

### Solutions
- **For Python projects**: You do not need Node.js or GitNexus. Fox Graph defaults to the built-in Python AST provider with zero external dependencies.
- **For multi-language projects**: Ensure Node.js (v18+) and npm are installed on your PATH so `npx gitnexus` can run locally.
- To force the local Python provider explicitly:
  ```bash
  python3 skills/fox-graph/scripts/fox_graph.py --repo . --provider python-ast
  ```

---

## 4. Permission Denied During Installation

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

## 5. How to Confirm the Skill is Active

Ask your agent to solve a bug or inspect a change. Look for these signs in its response:

- **Fox**: The agent grounds the problem first, writes a reproducer, traces to the owning layer, applies a minimal fix, and verifies counterexamples.
- **Fox Graph**: The agent reports changed symbols, callers up to depth 3, unpatched sibling entry points, and a prioritized regression plan.

If you need further help, open an issue at:
https://github.com/Devaretanmay/fox/issues
