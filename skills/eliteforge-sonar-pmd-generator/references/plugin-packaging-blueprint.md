# Plugin Packaging Blueprint

## Scope

Package custom PMD rules into a SonarQube plugin and expose a default quality profile.

## Recommended Module Layout

```text
custom-sonar-pmd/
  pom.xml
  custom-pmd-rules/
    pom.xml
    src/main/resources/rulesets/custom-<lang>-ruleset.xml
    src/main/java/... (optional Java PMD rules)
  custom-sonar-pmd-plugin/
    pom.xml
    src/main/java/.../CustomSonarPmdPlugin.java
    src/main/java/.../CustomRulesDefinition.java
    src/main/java/.../CustomProfileDefinition.java
    src/main/resources/...
```

## Compatibility Checklist

- SonarQube server version.
- `sonar-plugin-api` version.
- `sonar-pmd` plugin version (if extending/depending on it).
- PMD core/language module versions.

Lock versions explicitly in Maven BOM or dependency management.

## Rule Registration Checklist

1. Define a stable repository key (for example `custom-pmd`).
2. Register all custom rules with unique rule keys.
3. Include specification trace in rule metadata/message.
4. Register default quality profile and activate selected rules.
5. Ensure language key alignment (`java`, `xml`, etc.) with target rules.

## Minimal Plugin Responsibilities

- `Plugin` entry class: registers extensions.
- `RulesDefinition`: exposes rule repository and metadata.
- `ProfileDefinition`: seeds default profile and rule activations.

## Build and Package

```bash
mvn -DskipTests clean package
```

Expected output:
- plugin jar under `custom-sonar-pmd-plugin/target/`

## Deployment

1. Copy plugin jar to Sonar plugin directory:
   - container path: `/opt/sonarqube/extensions/plugins/`
2. Restart SonarQube.
3. Verify plugin appears in installed plugin list.

## Common Failure Modes

- API mismatch between plugin and SonarQube version.
- Missing rule repository key binding.
- Profile created but no active rules.
- Plugin loads but rules invisible due to wrong language key.

## Suggested Smoke Test Rule

Add one deterministic rule that is easy to trigger (for example, banning a known method call). Use this rule to verify end-to-end wiring before enabling the full ruleset.
