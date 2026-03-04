---
name: eliteforge-sonar-pmd-generator
description: Transform user-provided coding specification files into PMD governance artifacts and a validated SonarQube plugin workflow. Automatically classify each requirement into L1/L2/L3, implement L1-L2 as PMD rules for supported languages, package rules into a custom sonar-pmd plugin, and verify with Docker Sonar + real project scans.
---

# Sonar PMD Generator (Spec-driven, End-to-end)

## Overview

This skill converts coding standard documents into enforceable PMD rules and validates them through a real SonarQube server workflow.
Completion requires an end-to-end chain: spec parsing, `L1/L2/L3` classification, PMD ruleset generation, custom `sonar-pmd` plugin packaging, Docker Sonar startup, test project scan, and server-side verification.

## Progressive Loading

- Read [references/workflow-playbook.md](references/workflow-playbook.md) first for the full execution order.
- Read [references/plugin-packaging-blueprint.md](references/plugin-packaging-blueprint.md) when implementing or debugging plugin modules.
- Read [references/docker-sonar-validation.md](references/docker-sonar-validation.md) when starting Sonar in Docker and running test scans.
- Read [references/sonar-api-evidence-checklist.md](references/sonar-api-evidence-checklist.md) when collecting validation evidence.
- Use `scripts/verify_sonar_plugin.sh` for quick API-based smoke verification after scan.

## Trigger Conditions

Use this skill when the request includes one or more of these intents:
- Convert coding specifications into PMD rules.
- Auto-classify specification clauses into `L1/L2/L3`.
- Build or extend a custom Sonar PMD plugin/profile.
- Validate PMD plugin behavior in SonarQube using Docker and real scans.
- Prove custom rules are visible and producing issues in Sonar.

## Required Inputs

- One or more specification file paths.
- Target language(s) for each specification.
- Plugin workspace path (or permission to scaffold one).
- Test project path (or permission to scaffold one).
- Optional output directory for generated artifacts (default: `pmd-governance/`).
- Optional profile name (default: `custom-spec-profile`).

## Classification Contract (MUST follow)

- `L1`: can be covered by PMD built-in rule(s) for the target language.
- `L2`: can be expressed with PMD AST XPath rule(s) for the target language.
- `L3`: requires semantic/runtime/cross-module/business-process judgment and is not safely automatable in PMD.
- Never force `L3` into fragile XPath implementations.

For each spec statement, record:
- `SPEC-ID`
- original statement
- target language
- level (`L1/L2/L3`)
- detection target
- trigger condition
- exception condition
- severity
- implementation plan
- reviewer note (mandatory for `L3`)

## End-to-end Workflow (REQUIRED)

1. Parse specification statements and assign IDs (`SPEC-<LANG>-001`, ...).
2. Auto-classify every statement into `L1/L2/L3`.
3. Generate PMD governance artifacts:
   - `mapping/spec-to-pmd.csv`
   - `rulesets/custom-<lang>-ruleset.xml`
   - `manual-review/l3-review-checklist.md`
   - `README.md`
4. Build a custom PMD rules module:
   - include `L1` mapped refs and `L2` custom XPath/Java rules
   - rule keys/messages must include traceability to `SPEC-ID`
5. Build a custom Sonar plugin module:
   - register PMD rule repository
   - load custom rules into Sonar
   - provide default quality profile (`custom-spec-profile` or user-provided name)
6. Package plugin JAR and deploy into Sonar plugin directory (`extensions/plugins`).
7. Start SonarQube Community in Docker with the custom plugin loaded.
8. Wait for Sonar server readiness and initialize token/project binding.
9. Prepare a test project:
   - use real project if provided, otherwise scaffold a minimal project
   - include both violating and compliant code samples
10. Trigger real scan with Maven Sonar plugin (`mvn sonar:sonar`).
11. Verify plugin effectiveness via Sonar APIs/UI:
   - profile exists and is active
   - custom rules are listed and enabled
   - issues are produced with rule key + file + line mapping
12. Report scan evidence and unresolved gaps.

## Language Support Gate

1. Check if the target language is supported by PMD and your Sonar integration path.
2. If unsupported by PMD:
   - classify automatable candidates as `L3` fallback
   - generate manual review checklist
   - recommend alternative analyzer and optional generic external issues import

## Sonar Integration

Server-side plugin execution:  
- Preferred because this skill requires custom plugin validation.
- Scan command example:
  - `mvn -DskipTests sonar:sonar -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<token>`


## Docker Validation Baseline

Minimum checks after container startup:
- Sonar health endpoint reports ready.
- Plugin is loaded (visible in marketplace/plugins list or startup logs).
- Quality profile from the plugin is available.

Minimum checks after scan:
- At least one custom-rule issue appears on violating sample.
- Compliant sample does not trigger that custom rule.
- Issues are mapped to concrete file and line.

## Non-negotiable Rules

- Do not handcraft PMD reports; generated findings must come from actual analysis.
- `L3` items must be exported for manual review.
- End-to-end verification is incomplete without Docker Sonar + real scan evidence.
- First rollout should stay non-blocking unless user explicitly requests CI gating.

## Delivery Outputs

- Rules artifacts (`mapping`, `ruleset`, `L3 checklist`).
- Custom plugin source and packaged JAR.
- Docker startup commands and runtime evidence.
- Test project scan command and result summary.
- Verification report listing profile key, rule keys, issue count, and sampled issue locations.

## Troubleshooting Checklist

- Plugin not loaded: verify Sonar/plugin API compatibility and restart logs.
- Profile missing: verify repository key/profile registration code.
- No issues found: confirm profile binding and test code actually violates rule.
- False positives spike: narrow XPath scope and add negative samples.
- Scan auth errors: validate token and `sonar.host.url` consistency.
