# EliteForge Skills

Multi-skill repository for EliteForge workflows.

## Skill Catalog

### Engineering Governance

- `eliteforge-framework-specification`: unified framework specification, starter selection, integration, upgrade, and troubleshooting guidance
- `eliteforge-git-specification`: Git governance, branch naming, MR policy, squash rules, release, and hotfix workflow
- `eliteforge-sonar-pmd-generator`: classify coding specs into `L1/L2/L3/L4`, generate PMD governance outputs, package custom `sonar-pmd` plugins, and validate with Docker SonarQube scans

### Project Generation

- `eliteforge-java-service-generator`: scaffold Java services from the Maven archetype wrapper and run required post-generation checks
- `eliteforge-frontend-generator`: scaffold frontend app, UI component, and SDK projects with deterministic naming and command assembly

### Task Workflow

- `eliteforge-task-progress-tracker`: maintain a live task memo in `docs/tasks/<task-description>.md`, sync acceptance criteria and progress, and record git checkpoint commits for resumable work

### Messaging Automation

- `qingtui-message-sender`: send a plain text message to an exact QingTui contact on macOS with OCR-based pre-send verification
- `wechat-message-sender`: send a plain text message to an exact WeChat contact on macOS with exact-match safety checks

## Verify discoverability

```bash
npx skills add CloudSen/eliteforge-skills --list
```

## Install All Skills

```bash
npx skills add CloudSen/eliteforge-skills -g -y --skill eliteforge-framework-specification eliteforge-frontend-generator eliteforge-git-specification eliteforge-java-service-generator eliteforge-sonar-pmd-generator eliteforge-task-progress-tracker qingtui-message-sender wechat-message-sender
```

## Install By Topic

Engineering governance:

```bash
npx skills add CloudSen/eliteforge-skills -g -y --skill eliteforge-framework-specification eliteforge-git-specification eliteforge-sonar-pmd-generator
```

Project generation:

```bash
npx skills add CloudSen/eliteforge-skills -g -y --skill eliteforge-java-service-generator eliteforge-frontend-generator
```

Task workflow:

```bash
npx skills add CloudSen/eliteforge-skills -g -y --skill eliteforge-task-progress-tracker
```

Messaging automation:

```bash
npx skills add CloudSen/eliteforge-skills -g -y --skill qingtui-message-sender wechat-message-sender
```

## Find by keyword

```bash
npx skills find eliteforge
```
