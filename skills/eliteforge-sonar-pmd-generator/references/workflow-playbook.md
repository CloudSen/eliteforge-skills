# Workflow Playbook

## Goal

Deliver a complete, reproducible path from specification to validated SonarQube findings.

## Inputs

- Specification documents.
- Target language list.
- Plugin workspace (existing or to-be-created).
- Test project workspace.
- Sonar endpoint and token strategy.

## Output Artifacts

- `mapping/spec-to-governance.csv`
- `rulesets/custom-<lang>-ruleset.xml`
- `automation/l3-tooling-plan.md`
- `manual-review/l4-review-checklist.md`
- Custom plugin JAR
- Scan evidence report (profile key, rule keys, issue examples)

## Phase 1: Requirement Extraction and Classification

1. Parse normative clauses (must/forbid/required/unified style).
2. Assign IDs (`SPEC-<LANG>-001...`).
3. Classify each item:
   - `L1`: built-in PMD coverage.
   - `L2`: XPath or custom PMD rule.
   - `L3`: non-PMD automation can detect it.
   - `L4`: human or AI review needed.
4. Fill mapping CSV with trace fields.

## Phase 2: PMD Rule Generation

1. Build `L1` rules by PMD category refs.
2. Build `L2` rules as XPath (or Java PMD rules when XPath is not safe).
3. Add traceability in rule names/messages (`SPEC-ID`).
4. Validate each custom rule using positive and negative samples.

## Phase 3: L3 Automation Planning

1. Pick the narrowest stable tool for each `L3` rule:
   - formatter
   - pre-commit hook
   - build plugin
   - Semgrep / regex script
   - ArchUnit
2. Define execution stage (`pre-commit`, `build`, `CI`, `MR check`).
3. Record expected failure mode and exemptions.

## Phase 4: L4 Review Planning

1. Define the manual review checklist item.
2. If AI review is useful, define the prompt and evidence expected from the reviewer.

## Phase 5: Sonar Plugin Packaging

1. Build PMD rules module (resources + optional Java rule classes).
2. Build Sonar plugin module (repository + profile registration).
3. Package plugin JAR.
4. Copy JAR into Sonar plugin directory.

See [plugin-packaging-blueprint.md](plugin-packaging-blueprint.md) for structure and class-level checklist.

## Phase 6: Docker Sonar Validation

1. Start SonarQube Community container.
2. Wait until system status is `UP`.
3. Confirm plugin loaded.
4. Create token and bind profile to target project.
5. Run real scan from test project (`mvn sonar:sonar`).

See [docker-sonar-validation.md](docker-sonar-validation.md) for command templates.

## Phase 7: Evidence Collection

1. Query Sonar APIs for:
   - plugin installed
   - profile active
   - rules visible
   - issues generated
2. Export issue samples with file + line + rule key.
3. Record failed checks and mitigation.

See [sonar-api-evidence-checklist.md](sonar-api-evidence-checklist.md) for API commands.

## Done Criteria

- All spec items classified.
- `L1/L2` implemented and traceable.
- `L3` tooling plan generated.
- `L4` review checklist generated.
- Plugin loaded in Docker Sonar.
- Test scan produced expected issues.
- Evidence report available.
