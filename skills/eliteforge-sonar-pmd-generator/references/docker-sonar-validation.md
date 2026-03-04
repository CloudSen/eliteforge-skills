# Docker Sonar Validation

## Goal

Run a real SonarQube server with custom plugin JARs and validate scans against a test project.

## 1) Start SonarQube Community

```bash
docker run -d --name sonar-pmd-local \
  -p 9000:9000 \
  -v "$PWD/.sonar/plugins:/opt/sonarqube/extensions/plugins" \
  sonarqube:community
```

Place custom plugin jars in `$PWD/.sonar/plugins` before startup (or restart after copying).

## 2) Wait for readiness

```bash
until curl -fsS "http://localhost:9000/api/system/status" | grep -q '"status":"UP"'; do
  sleep 5
done
```

## 3) Create token (example)

Use Sonar UI to create a token, or API if admin credentials are available.

```bash
curl -u "admin:admin" -X POST "http://localhost:9000/api/user_tokens/generate?name=local-token"
```

If password is changed, use updated credentials.

## 4) Bind custom quality profile

Example API (replace placeholders):

```bash
curl -u "${SONAR_TOKEN}:" -X POST \
  "http://localhost:9000/api/qualityprofiles/add_project?language=java&project=<projectKey>&qualityProfile=<profileName>"
```

## 5) Run Maven scan in test project

```bash
mvn -DskipTests sonar:sonar \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=${SONAR_TOKEN} \
  -Dsonar.projectKey=<projectKey>
```

## 6) Verify scan outcome

- Project has analysis snapshot.
- Custom profile is active for project language.
- Custom rules produce expected issues on violating files.
- Compliant files do not produce false positives for smoke-test rules.

## Optional: External PMD import path

If plugin packaging is deferred, run PMD first and import report (language-property dependent).

```bash
mvn -DskipTests pmd:pmd
mvn -DskipTests sonar:sonar \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=${SONAR_TOKEN} \
  -Dsonar.java.pmd.reportPaths=target/pmd.xml
```

This path does not validate custom plugin loading.
