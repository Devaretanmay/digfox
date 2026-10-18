# Gates: Thorough Renaming from Digfox to Fox

Scope: Rename the skill, repository references, directories, file names, and all text occurrences from Digfox/digfox/DIGFOX to Fox/fox/FOX throughout the entire repository.

- [x] G1: Skill directory is renamed from skills/digfox to skills/fox
  CHECK: test -d skills/fox && ! test -d skills/digfox && echo "OK"
  EXPECT: OK
  EVIDENCE: OK

- [x] G2: All DIGFOX_*.md deliverable files are renamed to FOX_*.md
  CHECK: ls FOX_*.md | wc -l | tr -d ' '
  EXPECT: 8
  EVIDENCE: 8

- [x] G3: All HARNESS logs and patches containing digfox in filenames are renamed to fox
  CHECK: find HARNESS/ -name "*digfox*" | wc -l | tr -d ' '
  EXPECT: 0
  EVIDENCE: 0
- [x] G4: Zero occurrences of digfox (case-insensitive) in any tracked file across the repository
  CHECK: python3 -c "import os, re; matches = sum(1 for root, dirs, files in os.walk('.') if '.git' not in root and 'node_modules' not in root for f in files if not f.endswith(('.png', '.jpg', '.pyc')) and f != 'GATES.md' and re.search(r'digfox', open(os.path.join(root, f), errors='ignore').read(), re.I)); print(f'REMAINING_MATCHES: {matches}')"
  EXPECT: REMAINING_MATCHES: 0
  EVIDENCE: REMAINING_MATCHES: 0

- [x] G5: All test suites in pytest tests/ pass cleanly under the new fox skill layout
  CHECK: pytest tests/
  EXPECT: passed
  EVIDENCE: tests/test_skill_metadata.py .....                                       [100%] | ============================== 27 passed in 1.22s ==============================

- [x] G6: Universal formatting constraints verified (strictly zero em dashes, zero en dashes, zero emojis)
  CHECK: python3 -c "import glob, re, sys; em = '\u2014'; en = '\u2013'; emoji = re.compile('[\U00010000-\U0010ffff]'); bad = [f for f in glob.glob('**/*.py', recursive=True) + glob.glob('**/*.md', recursive=True) if '.git' not in f and 'node_modules' not in f and (em in open(f, encoding='utf-8', errors='ignore').read() or en in open(f, encoding='utf-8', errors='ignore').read() or emoji.search(open(f, encoding='utf-8', errors='ignore').read()))]; print('BAD_FORMATTING: ' + str(len(bad)))"
  EXPECT: BAD_FORMATTING: 0
  EVIDENCE: BAD_FORMATTING: 0
