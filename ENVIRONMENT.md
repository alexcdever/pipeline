# 环境事实

这一份收集**工具本身的真实行为**：命令怎么报错、系统怎么骗人、哪条路能走通。正文（`SKILL.md`）只写判据与证据要求，需要解释「为什么判据长这样」时来这里查。

**每一条都是实测过的**，改它之前先按它跑一次——把实测结果改掉写回去，比留一条过时的「常识」更糟。

**它只解释判据的来历，不新增规则。** 与 `SKILL.md` 冲突时以 `SKILL.md` 为准。

## git

**两点 `git diff <主分支> <id>` 会漏掉主分支前移后别人的提交。** 它比较的是两个尖端快照，merge-base 之后主分支上落的提交不出现在结果里；要和 merge-base 比（`git diff <主分支>...<id>`），或逐条看 `git log --name-only <主分支>..<id>` 的文件清单。

**`worktree remove --force` 的递归删除会顺着 junction / symbolic link 穿透到目标本身**，而且绕过回收站——一次清场就足以把 gitignore 的数据目录连同几 GB 数据库删光（真实事故：worktree 里为跑测试建了指向主树 `data/` 的 junction，清场时主库连同备份、staging 全被删）。所以清场要先摘链接再删树。

**`info/exclude` 是全局的。** 它挂在公共 gitdir 上（`git rev-parse --git-common-dir` 所指那份），条目对主树和所有 worktree 同时生效。写成裸目录或裸通配（`out/`、`*.log`）时，并行中的别的任务、以及主树里的合法文件会被 `git add -A` **静默跳过**，不报错、不改退出码，一路到主树复验才发现少了文件。所以条目要锚定到具体路径并带 `<id>`。

**私有 gitdir 的 `info/exclude` Git 不读。** worktree 自带的那个 `.git` 文件指向的私有目录里写什么都不生效，要写公共那份。

**`git -C <目录>` 只在「目录不存在」或「`.git` 文件格式坏」时报错。** 真正的静默陷阱是 `.git` 文件被指向**别的有效 gitdir**——比如改成指向主仓时，`git -C` 会返回主树的 HEAD 与 status，exit 0、看起来一切正常。所以判某个 worktree 的状态要用 `git worktree list --porcelain`，或者先 `git rev-parse --show-toplevel` 自证站在哪个仓里。

**`git branch -D` 遇到 worktree 占用会报 `cannot delete branch`。** 反过来则安全：`worktree remove` 不删分支，所以先 `worktree remove --force` 再 `branch -D`，两条都跑完才干净。顺序反了就是分支删不掉，或者操作中断后留下一条指向已删目录的 stale 登记（`git worktree list` 里看得见）。

**`git clean -ffdx` 会删掉整个 `.worktrees/`。** 第二个 `-f` 才删嵌套仓库，`-fdx` 不带它反而跳过；带上的那次清掉的是**正在进行的工作**，不是缓存。

**`git add -A` 会把项目里的临时目录一起捡进提交。** 项目里建 `.tmp/` 之类的目录，执行者一提交就进去了。

**`.gitignore` 对已跟踪的文件不起作用。** 旧版留下的 `.pipeline/` 若已被跟踪，光写进 `.gitignore` 不够，要 `git rm -r --cached` **并落进提交**；只改 index 不提交时，建 worktree 检出旧 HEAD 会让它照样被跟踪。

## Windows 与 PowerShell

**同一端口可以被多个进程同时监听。** 双方都 LISTEN、都不报错（`SO_REUSEADDR` 一类的套接字选项允许共享绑定），请求只会落到其中一个。所以「端口能起」不足以判断 worktree 里没有残留进程：它常常起得来，然后复验打到 **worktree 的代码**上，拿到假通过。

**`Get-NetTCPConnection` 在双监听者下常只回一行，进程号还会交替。** 两个进程命令行可能逐字相同，于是「按端口反查进程号」这条路在两个进程同时监听时不可靠；`netstat -ano` 才看得到两行。

**`Rename-Item` 对一个还有进程当前目录指向它（工作目录在那个目录里）的目录，仍可能成功。** 只有在目录里有打开的文件句柄时才失败。所以 rename 成功**不能**证明没进程，它是不可靠的间接信号。

**`worktree remove` 在 Windows 上遇到文件占用会 `Permission denied`。** 而它失败之前已经删掉了文件与 `.pipeline/`、也移除了登记，只留下一个空目录加 `.git` 文件与分支。这一格极难辨认，处置见 `RECOVERY.md`。

**`Start-Process -PassThru`（POSIX：`cmd & echo $!`）拿到的进程号要记下来。** 这是唯一可靠的停机依据；进程号丢了就只能按 `SKILL.md` 第 9 条问用户。

## Rust / Cargo

**`CARGO_TARGET_DIR` 指向共享目录即可让多个 worktree 复用编译产物。** Cargo 的指纹按 crate 内容寻址、不含绝对路径；registry 依赖跨 checkout 直接命中。冷编译动辄几十分钟的项目，新 worktree 跑构建/测试前在派发材料里给出共享 target，实测可省掉整块冷编译（某 610 包项目 26–30min → 约 2min）。

**共享 target 下裸 `cargo clean` 删的是整个目录**——所有 worktree 一起遭殃。`cargo clean -p <spec>` 只按 package 清，但同样不区分哪个 checkout 编的。

**共享 target 下多个 cargo 构建在 `debug/.cargo-build-lock` 上串行排队**（报 `Blocking waiting for file lock on build directory`）——不互踩产物但并行不了。要并行跑多 worktree 构建就各用各的 target。

**`cargo clean` 不存在「只清本 worktree」的语义。** 复用共享 target 的项目要把「禁止裸 clean」写进项目约定。

**生成式 workspace 把 crate 挂成绝对路径 `path` 依赖时，每个 checkout 是不同 unit，本地 crate 不复用**（例：nsh 给每个 checkout 生成 `.nsh/rust` 容器 crate）。所以共享 target 省掉的是依赖，省不掉本地 crate 本身。也别指望 sccache 补这一段：`SCCACHE_BASEDIRS` 归一化的是 rustc 的参数与 CWD，改变不了 Cargo 按 `PackageId` 分桶——实测过的项目里 Rust 编译几乎零命中（少数命中都来自 vendored 的 C 代码）。

## Node / pnpm

**pnpm 复用的不是 `node_modules`，是它下面的内容寻址 store。** `node_modules/.pnpm` 里的文件与 `pnpm store path` 所指的全局 store 是同一份数据（Windows 下 `fsutil hardlink list` 可见两者互为硬链接）；顶层条目是 `SYMLINKD`，但只指向**本树内**的 `.pnpm`，不越出 worktree。实测：首个目录装完后，第二个目录 `pnpm add` 同版本包约 1.3s。所以 worktree 的等价方案是「每棵树一份 `node_modules`，共用同一个 store」——与 Cargo 共享 target 同一层，且没有 build-lock 那类串行点：并发 `install` 只向 store 追加内容寻址的新条目，不互踩。

**`node_modules` 本身按名字寻址，一份目录只能装一套版本**——这与 Cargo target 的本质区别：指纹分桶让不同代码状态的产物在一个 target 里共存，`node_modules/<包名>` 一个位置只放得下一个版本。所以它不能跨 worktree 共享；共享发生在 store 层，各树仍各写各的 `.pnpm`。同一 store 里不同版本并存，锁文件分叉的分支也各装各的。

**直接把 `node_modules` 用 junction 指到主树或共享目录，落进 git 一节记的同一个坑**：`worktree remove --force` 顺着链接把目标删光。`node_modules` 保持每棵树一份实体目录。

**store 与 `node_modules` 必须在同一卷上。** 硬链接不能跨卷：仓在 `D:`、store 在 `C:`（`pnpm store path` 可查）时退化为整目录复制——安装仍快、缓存仍命中，但磁盘省不下来，和 store 共享的预期不符。

**npm / yarn classic 只有一层缓存等价。** `~/.npm` 的 cacache 同样内容寻址、跨 worktree 共享，省掉下载；但每棵树仍要完整解压出自己的 `node_modules`——省网络，不省磁盘与安装时间。这一段的 pnpm 结论对它们不成立。

## 宿主执行层

**退出码只能说明进程是否正常退出，说明不了业务结果。** 测试数量、失败用例、构建产物、迁移状态都不在退出码里，要从测试工具的机器可读输出、项目适配器或明确的后置验证里拿，从通用 `preview` 里推断不出来。

**系统临时目录会被回收。** 长输出日志放在那里，过一段时间可能就读不到了；关键验收的日志读不到时按证据缺失处理、重跑取回。

**`--no-verify` 这类开关只要存在就一定会被用。** 纯钩子方案挡得住「忘了跑」，挡不住「故意不跑」，而且用户手工 push、别的 agent push 都绕得过去。这就是 `SKILL.md` 要求这道检查必须由项目侧自动化强制、`TESTING.md` 里又要求「能上远端规则就上远端规则」的原因：那一层绕不过去。

**装好的钩子不等于生效。** 路径写错、可执行位没设、在 worktree 里钩子目录不生效、CI 配了但没设成必需检查，每一种都会让它在应该失败的时候静默放行。唯一跨系统都成立的验证方式是故意让它失败一次。
