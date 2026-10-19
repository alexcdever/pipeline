# 从旧版本迁过来

**这份文件不是契约的一部分。** 它是一次性的清理说明，做完就该忘掉；`SKILL.md` 与 `GLOSSARY.md` 才是规则本身。

新流程不读旧版的任何产物，所以换技能目录这件事本身零成本。但旧版在**项目仓库里**留下的东西要清一次——其中一条不清就会真的坏。

## 前提

不满足其中任何一条，就**别照下面的清单做**：

- **这个项目里没有还在跑的旧任务。** 旧版 worktree 里的中间态（规划 stage 文件、`progress.jsonl`、`amendments.json`、freeze 哈希、`goal.json`）在新流程里**没有对应物**，翻译不过来。等它结束，或者明说放弃，再动。
- **你接受删掉旧证据。** 旧证据的前提是「证据进 Git、永久归档」——新 `SKILL.md` 明确否定了这件事（「证据不进入 Git」「做完就清场」）。删它是有意为之，不是损失。

## 旧版留下了什么

旧版（`legacy-tools-v0.18.0`）除了 `SKILL.md`，还会往项目里放这些：

| 路径 | 是什么 | 处置 |
|---|---|---|
| `pipeline_tools/` | 旧版的 Python 机械闸门（`python -m pipeline_tools task validate / gate pre-merge / …`） | 删 |
| `references/` `templates/` `scripts/` `bin/` `tests/` | 旧版的契约文档、任务单模板、脚本，以及它自己的测试 | 删，**但要先确认是旧版带进来的** |
| `docs/tasks/` | 旧版放「进行中或待派发」任务单的地方 | 删里面的旧任务单 |
| `.pipeline/<task-id>/` | 阶段报告与机器结果：`<task-id>.md`、`executor-report.md`、`executor-result.json`、`review-report.md`、`reviewer-result.json`、`final-check.md`、`final-result.json`、`finalization.json` | 全部删除并取消跟踪 |
| `.pipeline/archive/<task-id>.md` | 终态任务单的隔离区 | 同上 |

**未跟踪、但可能还在的项目本地文件**（旧版的 `.gitignore` 只挡了其中一部分）：`.pipeline/config.json`（审批策略，旧版要手工创建）、`.pipeline/recovery-index.json`、`.pipeline/metrics/`、`.pipeline/<task-id>/<task-id>-progress.jsonl`。一并删。

`tests/`、`bin/`、`scripts/`、`docs/`、`references/`、`templates/` 这几个名字太通用，**多半也有你自己的东西在里面**。删之前先看一眼那是谁的：

```bash
git log --oneline -- pipeline_tools references templates tests bin scripts docs
```

条目全是旧版的阶段提交，才整块删；有自己的提交就只挑出来。

## 唯一的硬阻塞：`.gitignore` 与已跟踪的 `.pipeline/`

新 `SKILL.md` 要求 `.gitignore` **在创建第一个 worktree 之前**就提交 `/.worktrees/` 与 `/.pipeline/`。旧版的 `.gitignore` 里**没有** `/.pipeline/`——旧版的设计恰恰是把证据提交进 Git。

而且 **`.gitignore` 对已跟踪的文件无效。** 旧项目里 `.pipeline/` 下的文件是被跟踪的，所以光加一行 ignore 没有用：执行子代理的 `git add -A` 照样会把 `.pipeline/` 的改动提进分支。必须先取消跟踪。

## 清单

在主工作树根目录执行。步骤 3 给了 POSIX 与 Windows PowerShell 两种写法；其余单份示例的命令在 Windows 下把 `rm -rf` 换成 `Remove-Item -Recurse -Force`。

**1. 补 `.gitignore`**

```
/.worktrees/
/.pipeline/
```

`/.worktrees/` 旧版本来就有，留着；`/.pipeline/` 是新增的那一条。

**2. 取消跟踪并删除旧证据（不可逆）**

```bash
git rm -r --cached --ignore-unmatch .pipeline   # 不存在或本就未跟踪时不报错（同步骤 3 的写法）
rm -rf .pipeline
```

取消跟踪只在 index 里，**先把它落进提交**（`git commit`，或并入步骤 6 那次提交；`.pipeline/` 的删除已随步骤 2 的 `git rm --cached` 暂存在 index，提交时直接带走即可），不然建第一个 worktree 时检出的是旧 HEAD 树，`.pipeline/` 在那里仍被跟踪，`.gitignore` 照样失效。

**3. 删掉旧版带进来的工具、模板与任务单**

```bash
# POSIX（Linux/macOS/WSL/git-bash）——先按上面 `git log` 那段确认归属：
# 只有该目录的提交历史全是旧版带来的，才整块删；混有自有提交的，只挑旧文件删。
for d in pipeline_tools references templates scripts bin tests; do
  [ -d "$d" ] || continue                       # 只处理存在的目录，免得整句 fatal
  git status --porcelain -- "$d" | grep -q . && { echo "$d 有未提交改动，先确认再删"; continue; }
  git rm -r --ignore-unmatch "$d" 2>/dev/null; rm -rf "$d"   # 删被跟踪的部分，再清掉未跟踪残留（分号：无条件都跑）
done
# 旧任务单：确认目录里只有旧版任务单（带 `<!-- Task ID: -->` 标记或 `pipeline-contract` 区块）才整删；
# 下面这行是「整删」的做法，只在确认过之后执行；混有自有文档时逐个挑出来删，删完目录空了再删目录。
[ -d docs/tasks ] && ! git status --porcelain -- docs/tasks | grep -q . && { git rm -r --ignore-unmatch docs/tasks 2>/dev/null; rm -rf docs/tasks; } || echo "docs/tasks 有改动或不存在：先确认归属再删"
```

```powershell
# Windows PowerShell 等价写法
foreach ($d in 'pipeline_tools','references','templates','scripts','bin','tests') {
  if (-not (Test-Path $d)) { continue }
  if (git status --porcelain -- $d) { Write-Host "$d 有未提交改动，先确认再删"; continue }
  git rm -r --ignore-unmatch $d 2>$null; Remove-Item -Recurse -Force $d
}
if ((Test-Path docs/tasks) -and -not (git status --porcelain -- docs/tasks)) { git rm -r --ignore-unmatch docs/tasks 2>$null; Remove-Item -Recurse -Force docs/tasks } else { Write-Host "docs/tasks 有改动或不存在：先确认归属再删" }
```


**4. 去掉 `.gitattributes` 里两行**

```
docs/tasks/*.md -text
.pipeline/** -text
```

保留 `* text=auto eol=lf`。不再有会被跟踪的 `.pipeline/**`，这两条属性没有对象了。

**5. 清掉旧版遗留的 worktree**

```bash
git worktree list
```

`.worktrees/` 下每个目录都是一个旧任务（旧版也用这个父目录）。目录已被手工删掉、`git worktree list` 还列着的（stale 登记）先 `git worktree prune`，再删分支。其余逐个——**先按步骤 3 那套认归属**（目录里有旧版 `.pipeline/` 痕迹、或分支可确认是旧任务），认不出的别动、问用户；新版任务也挂在这个父目录下，别误删在跑的任务：

```bash
git worktree remove .worktrees/<task-id>   # 留有未提交改动或未跟踪文件的加 --force
git branch -D <task-id>                    # -D 会静默丢掉未并入的提交；删前先 `git log <主分支>..<task-id>` 看一眼，确认没有要留的再删
```

**6. 提交一次**

先确认工作区只剩本清单产生的改动（有别的东西先按项目惯例处置），再提交；嫌 `git add -A` 太宽的，只 add 实际还存在的路径（例如 `git add .gitignore .gitattributes`，目录不存在的剔除）——`.pipeline/` 的删除已随步骤 2 的 `git rm --cached` 进了 index，不用再 add（它已从磁盘消失，写进 pathspec 会 fatal）。

```bash
git add -A
git commit -m "清除 pipeline v0.18 残留"
```

## 迁完之后

从此不再做的三件事：

- **不把 `.pipeline/` 或任何证据提交进 Git。** 它随 worktree 一起生灭。
- **不再有 `docs/tasks/`、任务单冻结与 `amend`、`*result.json`。** 一个任务的记录就是 `<worktree>/.pipeline/` 下那四个文件。
- **不再需要 `.pipeline/** -text`。** 没有会被跟踪的证据，就没有需要逐字节保真的 blob。
