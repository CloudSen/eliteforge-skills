# EliteFoege Git 管理规范参考

## 1. 分支管理模型

以需求为最小单元进行开发。

| 源分支 | 目标分支 | 操作 | 合并目的 |
| :--- | :--- | :--- | :--- |
| `master` | `feature/<version>/<developer>/<taskId>/<taskDesc>`、`qa/<version>`、`release/<version>` | 从 `master` 新建分支 | 本地开发与自测 |
| `master` | `feature/<version>/...`、`qa/<version>`、`release/<version>` | `git rebase` | 及时同步 `master` 最新变更 |
| `feature` | `nightly` | 开发者自行 `git merge` | 部署开发环境联调 |
| `feature` | `qa/<version>` | 创建 GitLab MR + `make deploy VERSION=<version>-SNAPSHOT MODEL=client or starter` | 提测与回归，发布 SNAPSHOT `client`/`starter` |
| `feature`（已 squash） | `release/<version>` | `Squash and merge` | 预生产部署与回归，保持 `release` 历史整洁 |
| `release/<version>` | `release/<version>` | `git tag <version>` + `make deploy VERSION=<version> MODEL=client or starter` | 发布正式版本 `client`/`starter` |
| `release/<version>` | `master` | `Fast-forward only merge` | 正式发布并保持 `master` 线性历史 |

### 1.1 正常迭代伪命令

```bash
git fetch -v -f -t --prune

# 创建迭代分支
git switch -c feature/<version>/... --track origin/master
git switch -c qa/<version> --track origin/master
git switch -c release/<version> --track origin/master
git switch feature/<version>/...

# 开始开发
git commit -m "feat(#taskId): xxx"
git commit -m "feat(#taskId): yyy"
git commit -m "feat(#taskId): zzz"

# 发布 dev 环境（先合并到 nightly，再 push feature）
git switch nightly
git merge feature/<version>/...
git push
make deploy
git switch feature/<version>/...
git push

# 提测 qa 环境
# 在 GitLab 页面创建 MR，指定 assignee=自己，reviewer=负责人
# MR 通过后执行：
make deploy VERSION=<version>-SNAPSHOT

# 继续修复 qa 问题
git switch feature/<version>/...
git commit -m "fix(#taskId): xxxx"
# 重复发布 dev 和 qa 流程

# feature 测试完毕，进行 squash
git switch feature/<version>/...
git rebase -i <此分支第一个提交的上一个commit hash>
git push --force --no-verify

# release 合并已 squash 的 feature
git switch release/<version>/...
git merge feature/<version>/1
git merge feature/<version>/2
git merge feature/<version>/3

# 基于远程 master 变基
git fetch -v -f -t --prune
git rebase origin/master
git push --force --no-verify

# 先发 snapshot
make deploy VERSION=<version>-SNAPSHOT

# 打 tag 并发布正式版
git tag <version>
git push origin <version>
make deploy VERSION=<version>

# 合回 master
git switch master
git merge --ff-only release
```

## 2. 提交信息规范

遵循 Angular commit message 规范：  
`<type>(<scope>): <subject>`

### 2.1 提交类型 type

- `build`: 修改构建系统或外部依赖
- `ci`: 修改 CI 配置或脚本
- `docs`: 修改文档
- `feat`: 新特性
- `fix`: 修复 bug
- `perf`: 性能优化
- `refactor`: 非新增功能/非修 bug 的重构
- `style`: 不影响语义的格式调整
- `test`: 增加或修正测试

### 2.2 作用域 scope

强制要求：
- 当 `type` 为 `feat` 或 `fix` 时，`scope` 必须为任务/缺陷编号：`#<ID>`。

示例：
- `feat(#11241): 新增用户注册功能`
- `fix(#9939): 修复登录接口参数校验错误`

其他类型可选 scope：
- `docs(readme): 更新使用说明`
- `refactor(auth): 优化认证逻辑结构`
- `build: 增加xxx依赖`

### 2.3 主题 subject

- 一句话简洁描述
- 使用命令式、现在时
- 结尾不加句号

### 2.4 正文 body

修改较多时，按清单列出变更内容。

```text
feat(#123): 优化主页内容展示

- 优化用户头像圆框，更顺滑
- 优化个人任务提示方式
- 优化xxxx
```

### 2.5 页脚 footer

破坏性变更：

```text
BREAKING CHANGE:

任务隔离策略进行了重构，需要对历史数据进行迁移操作。
迁移数据注意事项：
......
```

关闭任务：

```text
Closes #123, #245, #992
```

### 2.6 合规案例

```text
feat(#123): 添加xxx功能
fix(#321): 修复xxxbug
style: 调整代码格式
docs: 添加代码贡献说明
doc(#789): 更新xxx注释
build: 更新xxx依赖
build(#789): 更新xxx脚本
refactor(#456): 重构xxx代码
refactor(web): 重构AuthFilter支持白名单
```

## 3. MR 规范

- 项目根目录通常包含 MR 模板：`.gitlab/merge_request_templates/default.md`。
- 开发中可持续提交 `Draft:` MR，提前对齐方向。
- 联调通过且需求冒烟完成后，才发正式 MR。
- 最终 MR 前必须将本地分支所有 commit squash 为一个。
- MR title 必须与 squash 后 commit message 一致。
- 提交 MR 时必须使用 `default` 模板并完成模板自检。
- pipeline 全部成功后，再通知 reviewer 走查。
- reviewer 提出的整改建议必须全部处理。

## 4. 热修规范

- 仅现场阻塞功能或缺陷允许走热修。
- 热修分支命名：`hotfix/2.8.x-0325`。
  - 含义：2.8 版本热修，上线时间 3 月 25 日。
  - 分支 `pom version`：`2.8.x-0325-SNAPSHOT`。
  - 上线日发布热修后，再决定最终稳定版本（如 `2.8.2`）。
  - 目的：避免过早定版，保留紧急事项插入空间。

## 5. 冲突规避策略

1. 尽量保证需求独立，一个人负责一个需求。
2. 同一需求多人开发时，先拉 `feature/<version>/common/<taskId>` 维护共性代码，再拉个人分支实现接口；`common` 变更要及时同步。
3. 不兼容升级场景禁止多迭代并行开发。
4. 大范围重构或重写场景禁止多迭代并行开发。

## 6. 配套 CLI

### 6.1 `auto-merge`

```text
auto-merge -h
用法：auto-merge [--ff-only | --merge | --rebase]

  --ff-only   执行 git pull --ff-only（默认），禁止 merge commit。
  --merge     执行普通 git pull，允许非 fast-forward 合并。
  --rebase    执行 git pull --rebase，以 rebase 方式更新当前分支。
  -h, --help  显示帮助。
```

示例：

```bash
auto-merge
auto-merge --merge
auto-merge --rebase
```

### 6.2 `check_merge`

```text
$ check_merge -h
使用方法: /usr/local/bin/check_merge <version> <branch>
```

### 6.3 `delete_local_branches`

无需参数，删除除 `master` 以外的本地分支。执行前确认本地分支均已 push。

### 6.4 `git-rename-branch`

```text
git-rename-branch <旧分支名> <新分支名>
```
