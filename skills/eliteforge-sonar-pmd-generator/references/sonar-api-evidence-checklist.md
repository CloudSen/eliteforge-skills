# Sonar API Evidence Checklist

## Variables

```bash
export SONAR_HOST="http://localhost:9000"
export SONAR_TOKEN="<token>"
export PROJECT_KEY="<projectKey>"
export PLUGIN_KEY="<customPluginKey>"
export RULE_REPO_KEY="<customRuleRepoKey>"
export PROFILE_KEY="<language>-<profileKey>"
```

## 1) Server status

```bash
curl -u "${SONAR_TOKEN}:" -sS "${SONAR_HOST}/api/system/status"
```

Expect: `"status":"UP"`.

## 2) Plugin installed

```bash
curl -u "${SONAR_TOKEN}:" -sS "${SONAR_HOST}/api/plugins/installed"
```

Expect: plugin list contains `PLUGIN_KEY`.

## 3) Quality profile exists

```bash
curl -u "${SONAR_TOKEN}:" -sS "${SONAR_HOST}/api/qualityprofiles/search"
```

Expect: profile list contains target profile name/key.

## 4) Project-profile binding

```bash
curl -u "${SONAR_TOKEN}:" -sS "${SONAR_HOST}/api/qualityprofiles/search?project=${PROJECT_KEY}"
```

Expect: target language profile for project is the custom profile.

## 5) Rules visible in repository

```bash
curl -u "${SONAR_TOKEN}:" -sS "${SONAR_HOST}/api/rules/search?repositories=${RULE_REPO_KEY}&ps=500"
```

Expect: rules count > 0 and includes smoke-test rule key.

## 6) Issues generated

```bash
curl -u "${SONAR_TOKEN}:" -sS "${SONAR_HOST}/api/issues/search?componentKeys=${PROJECT_KEY}&ps=100"
```

Expect: at least one issue tied to custom rule key on violating samples.

## 7) Issue location spot-check

Use issue payload fields to confirm:
- file/component path
- line number
- rule key
- message includes traceable `SPEC-ID`

## Evidence Bundle Recommendation

Capture and store:
- plugin installed response snippet
- profile search snippet
- rule search snippet
- issue search snippet
- scan command and commit hash of test project
