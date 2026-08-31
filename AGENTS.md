# Technical Art Knowledge Base Instructions

## Scope

This repository is a personal Obsidian knowledge base for Technical Art.
The goal is to build durable understanding from concept to mechanism, tradeoff,
and practical verification. It is not a portfolio, project diary, interview
question bank, or collection of isolated definitions.

These instructions apply to the whole repository. A nested `AGENTS.md` may add
local migration notes, but must not restore the legacy encyclopedia rules or
contradict this file.

## Primary Goals

- Build a systematic, readable, extensible Technical Art knowledge system.
- Repair knowledge that currently stops at names, APIs, or surface definitions.
- Preserve useful knowledge from old notes and course materials while replacing
  their old file organization.
- Keep writing accurate, concise, natural, and suitable for repeated study.
- Keep terminology, navigation, sources, and Git history maintainable.

## Non-Goals

- Do not organize formal knowledge around personal projects or resume entries.
- Do not turn the vault into a list of interview questions.
- Do not preserve an old file merely because it already exists.
- Do not chase completeness by creating one page for every keyword.
- Do not reproduce an external wiki tool's default schema when it conflicts with
  this repository's topic-based organization.

## Knowledge Architecture

- Organize by natural knowledge domains and learning dependencies.
- Prefer a cohesive topic article with H2/H3 sections over many tiny term pages.
- Split a page only when it contains distinct responsibilities, learning goals,
  or has become meaningfully difficult to read and maintain.
- Do not impose a universal article template. Let mechanism-heavy, comparison,
  workflow, and practical articles use structures that fit their subject.
- Keep formal knowledge separate from project process documents in `docs/` and
  source material in the designated source/archive area.
- Treat the architecture in `docs/知识库重构计划.md` as a working baseline. Change
  it only with a documented reason found during the full source audit.

As a concrete granularity example, one article named `纹理技术` may contain
texture sampling, filtering, Mipmap, addressing, compression, and their
relationships. Those terms do not each require a separate page.

## Source Audit And Migration

- Audit the complete vault, including Markdown, TXT, PDF, PPT/PPTX, DOC/DOCX,
  code, course notes, transcripts, exercises, and attachments when relevant.
- Treat course material as a source to understand, deduplicate, and integrate;
  do not copy its course-by-course structure into the formal knowledge system.
- Maintain a migration ledger with at least: source path, topic, value, target,
  processing status, and notes about uncertainty or duplication.
- A legacy file may be rewritten, moved, merged, split, archived, or deleted.
- Never delete a legacy source until its valuable content is marked as migrated,
  intentionally archived, duplicated elsewhere, or out of Technical Art scope.
- Preserve recoverability through Git commits and the migration ledger.
- Non-TA course material may remain as a source/archive, but must not pollute the
  formal Technical Art navigation.

## Content Depth

Important topics must go beyond a definition. Build the most natural path among:

- what problem the technique solves;
- why the problem exists;
- the underlying mechanism and execution flow;
- costs, limits, failure cases, and alternatives;
- what can be observed in an engine, capture, profiler, asset, or small test;
- a short example, formula, diagram, pseudocode, or code fragment when useful.

These are quality dimensions, not mandatory section headings. Do not fill empty
sections simply to satisfy a template.

## Writing Style

- Write in concise, natural Chinese note style.
- Prefer short sentences and one clear claim per sentence.
- Avoid academic filler, promotional wording, fake narrative, and long sentences.
- Keep technical terms accurate and consistent.
- Use `中文（English）` on first mention when the Chinese translation materially
  helps search or understanding, such as `时域采样（Temporal Sampling）`.
- Keep established abbreviations such as MSAA, TAA, BRDF, BVH, and PCF as titles
  when that is the clearest convention; explain the full name in the text.
- Use formulas only where they help explain a mechanism. Define every variable.
- Do not invent engine internals, GPU/driver behavior, version-specific facts, or
  performance numbers. Mark unresolved details as `待补充` or use a warning callout.

## Markdown And Obsidian

- Use normal Markdown headings to express the subject's natural structure.
- Use `**bold**` for core terms or conclusions and `==highlight==` sparingly.
- Use Obsidian callouts only when they add real value:
  - `[!warning]` for mistakes, constraints, and uncertain behavior;
  - `[!question]` for a useful reasoning check;
  - collapsed `[!tip]-` for optional depth.
- Add `[[wikilinks]]` only for meaningful prerequisites, dependencies,
  comparisons, or follow-up topics. Do not add links to inflate graph density.
- Avoid duplicate pages and aliases for the same concept. Maintain one canonical
  term and record alternate names in the terminology index or page aliases.
- Frontmatter is optional and minimal. Do not force metadata that is not used.

## Sources And Accuracy

- Prefer primary sources: specifications, engine documentation, source code,
  papers, and official technical presentations.
- Secondary articles and course notes may help explanation but do not override a
  primary source on implementation details.
- Record sources for version-specific behavior, disputed mechanisms, equations,
  hardware details, and non-obvious factual claims.
- Separate verified facts, source interpretation, and personal practical notes.
- When evidence conflicts, retain the conflict and explain it instead of silently
  selecting a convenient answer.

## Working Process

Follow these phases for a full rebuild:

1. Audit all sources and produce the inventory, topic map, duplicate map, gaps,
   terminology problems, and migration ledger.
2. Review module boundaries and article granularity using the complete audit.
3. Rebuild formal knowledge in dependency order and absorb legacy sources.
4. Establish useful links and remove duplicated explanations.
5. Review each major module and repair it before moving on.
6. Run a final vault-wide review and continue fixing until acceptance criteria
   are met.

Do not pause after every small decision. Continue through analysis, execution,
review, and correction unless access fails, data is damaged, or a genuinely
important ambiguity cannot be resolved safely.

## Autonomous Implementation Mode

When the user asks to execute the full rebuild, enter Autonomous Implementation
Mode and continue from P0 to P1 to P2 without pausing between phases, asking
whether to continue, or waiting for routine confirmation.

- P0 covers project rules, source audit, migration ledger, and architecture.
- P1 covers the core prerequisite knowledge and its module reviews.
- P2 covers specialist domains, legacy retirement, links, terminology, and the
  final vault-wide acceptance review.
- Complete each independently testable phase or task, then run its relevant
  checks before proceeding.
- Diagnose and fix failed checks. Do not skip them or weaken acceptance criteria.
- Preserve existing behavior and run regression checks where scripts or existing
  workflows are affected.
- Before each commit, inspect `git diff`, test results, documentation, indexes,
  logs, and manifests for consistency.
- Keep plans, design documents, README files, changelogs, indexes, and migration
  records synchronized with the actual repository state.
- After all phases, run the complete regression and report completed phases,
  commits, checks, documentation updates, and remaining risks.
- Stop for user input only when a hard blocker cannot be resolved from the code,
  local materials, documentation, environment, or a safe reversible approach.

Each completed phase or independently accepted task receives its own commit.
Use a Chinese summary in this form:

```text
feat(<phase>): <中文摘要>
```

Do not include unrelated user changes in these commits.

## Process Documents

Keep project-management material in `docs/`, including:

- architecture and execution plan;
- current-state audit;
- migration ledger;
- terminology decisions;
- build log;
- module and final review reports.

Formal Technical Art notes do not belong in `docs/`.

## Quality Gates

Before considering a module complete, check:

- Topic boundaries are natural and neither fragmented nor excessively large.
- Core knowledge explains mechanisms rather than listing names.
- Claims are accurate, uncertainty is visible, and important sources are tracked.
- Terminology is consistent and useful links resolve.
- Writing remains concise and does not show rigid AI-generated structure.
- Valuable legacy and course knowledge mapped to this module has been handled.
- Repeated content has been consolidated.

The final review must also check broken links, orphan pages, duplicate titles,
stale placeholders, inconsistent aliases, and material left unprocessed.

## Git

- Inspect `git status` before editing and preserve unrelated user changes.
- Use one meaningful commit per audit milestone, accepted task, or major module.
- Do not combine the whole rebuild into one opaque commit.
- Do not rewrite history or use destructive Git commands.
- The existing pre-rebuild backup commit is a recovery point, not a reason to
  skip migration accounting.
- Commit summaries must be in Chinese and follow the Autonomous Implementation
  Mode format when the full rebuild is active.

## Legacy Instructions

`system_prompt.md` and the old rules below `TA-Encyclopedia/` describe the
previous course-summary and one-term-per-page workflows. They are migration
sources only and do not govern new formal knowledge.
