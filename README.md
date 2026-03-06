# EliteForge Skills

Multi-skill repository for EliteForge workflows.

## Included skills

- `eliteforge-framework-specification`: EliteForge unified framework specification and starter selection guidance
- `eliteforge-frontend-generator`: frontend project generation workflow
- `eliteforge-git-specification`: Git governance and branch / MR policy
- `eliteforge-java-service-generator`: Java service scaffolding workflow
- `eliteforge-sonar-pmd-generator`: classify coding specs into `L1/L2/L3/L4`, generate PMD governance outputs, package custom `sonar-pmd` plugins, and validate with Docker SonarQube scans
- `qingtui-message-sender`: send a plain text message to an exact QingTui contact on macOS with pre-send verification
- `wechat-message-sender`: WeChat message sending workflow

## Verify discoverability

```bash
npx skills add CloudSen/eliteforge-skills --list
```

## Install selected skills (global)

```bash
npx skills add CloudSen/eliteforge-skills -g -y --skill eliteforge-framework-specification eliteforge-frontend-generator eliteforge-git-specification eliteforge-java-service-generator eliteforge-sonar-pmd-generator qingtui-message-sender wechat-message-sender
```

## Find by keyword

```bash
npx skills find eliteforge
```
