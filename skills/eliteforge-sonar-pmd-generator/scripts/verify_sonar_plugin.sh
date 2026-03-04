#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: verify_sonar_plugin.sh --host <url> --token <token> [--project <key>] [--plugin <key>] [--repo <key>] [--profile <name>] [--rule <key>]

Checks SonarQube readiness and plugin/profile/rule/issue visibility.
USAGE
}

HOST=""
TOKEN=""
PROJECT_KEY=""
PLUGIN_KEY=""
REPO_KEY=""
PROFILE_NAME=""
RULE_KEY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="$2"; shift 2 ;;
    --token)
      TOKEN="$2"; shift 2 ;;
    --project)
      PROJECT_KEY="$2"; shift 2 ;;
    --plugin)
      PLUGIN_KEY="$2"; shift 2 ;;
    --repo)
      REPO_KEY="$2"; shift 2 ;;
    --profile)
      PROFILE_NAME="$2"; shift 2 ;;
    --rule)
      RULE_KEY="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2 ;;
  esac
done

if [[ -z "$HOST" || -z "$TOKEN" ]]; then
  echo "--host and --token are required" >&2
  usage
  exit 2
fi

call_api() {
  local path="$1"
  curl -fsS -u "${TOKEN}:" "${HOST}${path}"
}

assert_contains() {
  local body="$1"
  local expected="$2"
  local message="$3"
  if [[ "$body" == *"$expected"* ]]; then
    echo "[PASS] $message"
  else
    echo "[FAIL] $message (missing: $expected)" >&2
    exit 1
  fi
}

echo "Checking Sonar status..."
status_body="$(call_api "/api/system/status")"
assert_contains "$status_body" '"status":"UP"' "Sonar status is UP"

echo "Checking plugin installation list..."
plugins_body="$(call_api "/api/plugins/installed")"
if [[ -n "$PLUGIN_KEY" ]]; then
  assert_contains "$plugins_body" "\"key\":\"${PLUGIN_KEY}\"" "Plugin ${PLUGIN_KEY} is installed"
else
  echo "[SKIP] Plugin key not provided"
fi

echo "Checking quality profiles..."
profiles_body="$(call_api "/api/qualityprofiles/search")"
if [[ -n "$PROFILE_NAME" ]]; then
  assert_contains "$profiles_body" "$PROFILE_NAME" "Profile ${PROFILE_NAME} is visible"
else
  echo "[SKIP] Profile name not provided"
fi

if [[ -n "$REPO_KEY" ]]; then
  echo "Checking rule repository ${REPO_KEY}..."
  rules_body="$(call_api "/api/rules/search?repositories=${REPO_KEY}&ps=500")"
  assert_contains "$rules_body" '"total":' "Rules API responded for repository ${REPO_KEY}"
  if [[ -n "$RULE_KEY" ]]; then
    assert_contains "$rules_body" "$RULE_KEY" "Rule ${RULE_KEY} is present"
  else
    echo "[SKIP] Rule key not provided"
  fi
else
  echo "[SKIP] Rule repository key not provided"
fi

if [[ -n "$PROJECT_KEY" ]]; then
  echo "Checking project issues for ${PROJECT_KEY}..."
  issues_body="$(call_api "/api/issues/search?componentKeys=${PROJECT_KEY}&ps=100")"
  assert_contains "$issues_body" '"total":' "Issues API responded for project ${PROJECT_KEY}"
  echo "[INFO] issues payload sample:"
  echo "$issues_body" | head -c 400
  echo
else
  echo "[SKIP] Project key not provided"
fi

echo "Verification completed successfully."
