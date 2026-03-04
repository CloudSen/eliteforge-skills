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

- `mapping/spec-to-pmd.csv`
- `rulesets/custom-<lang>-ruleset.xml`
- `manual-review/l3-review-checklist.md`
- Custom plugin JAR
- Scan evidence report (profile key, rule keys, issue examples)

## Phase 1: Requirement Extraction and Classification

1. Parse normative clauses (must/forbid/required/unified style).
2. Assign IDs (`SPEC-<LANG>-001...`).
3. Classify each item:
   - `L1`: built-in PMD coverage.
   - `L2`: XPath or custom PMD rule.
   - `L3`: manual review needed.
4. Fill mapping CSV with trace fields.

## Phase 2: PMD Rule Generation

1. Build `L1` rules by PMD category refs.
2. Build `L2` rules as XPath (or Java PMD rules when XPath is not safe).
3. Add traceability in rule names/messages (`SPEC-ID`).
4. Validate each custom rule using positive and negative samples.

## Phase 3: Sonar Plugin Packaging

1. Build PMD rules module (resources + optional Java rule classes).
2. Build Sonar plugin module (repository + profile registration).
3. Package plugin JAR.
4. Copy JAR into Sonar plugin directory.

See [plugin-packaging-blueprint.md](plugin-packaging-blueprint.md) for structure and class-level checklist.

## Phase 4: Docker Sonar Validation

1. Start SonarQube Community container.
2. Wait until system status is `UP`.
3. Confirm plugin loaded.
4. Create token and bind profile to target project.
5. Run real scan from test project (`mvn sonar:sonar`).

See [docker-sonar-validation.md](docker-sonar-validation.md) for command templates.

## Phase 5: Evidence Collection

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
- `L3` checklist generated.
- Plugin loaded in Docker Sonar.
- Test scan produced expected issues.
- Evidence report available.
