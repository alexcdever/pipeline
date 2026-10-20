# 执行层协议

这一份规定宿主侧的命令执行设施向 agent 返回什么。**它不是流程契约的一部分**——契约只要求「命令的完整输出可回查、退出码不能代替验收」，怎么把命令包装成那个样子、每个字段叫什么，是宿主执行层的事。这里给出一种统一的通用外壳。

契约与这里冲突时以契约为准。

## 结构

```json
{
  "command": "<命令>",
  "cwd": "<工作目录>",
  "status": "completed",
  "exitCode": 0,
  "timedOut": false,
  "durationMs": 18420,
  "error": null,
  "degraded": false,
  "missingFields": [],
  "stdout": {
    "bytes": 1200,
    "lines": 24,
    "previewTruncated": false,
    "preview": "<有限预览>",
    "logAvailable": true,
    "logPath": "<完整 stdout 日志路径>"
  },
  "stderr": {
    "bytes": 8000,
    "lines": 160,
    "previewTruncated": true,
    "preview": "<有限预览>",
    "logAvailable": true,
    "logPath": "<完整 stderr 日志路径>"
  },
  "postcondition": {
    "checked": false,
    "passed": null,
    "summary": null
  }
}
```

## 字段含义与约束

- `status` 使用 `completed`、`failed`、`timed_out`、`failed_to_start` 或 `terminated`。先判断是否超时：超时使用 `timed_out`，即使之后进程被终止也不使用 `terminated`；未启动成功使用 `failed_to_start`；启动后正常退出时，`exitCode === 0` 使用 `completed`，其他整数退出码使用 `failed`；启动后被外部终止且没有退出码时使用 `terminated`，被终止但拿到了整数退出码的按 `failed` 记并在 `error` 写明是被终止的。除 `completed` 和 `failed` 外，`exitCode` 必须为 `null`，并在 `error` 写明原因。`timedOut` 仅在 `status` 为 `timed_out` 时为 `true`。
- `durationMs` 是从执行开始到进程结束、超时或启动失败的毫秒数。`bytes` 按原始输出字节统计；`lines` 按换行符数量统计，若非空输出没有末尾换行则再加一。
- `previewTruncated` 只描述返回给 agent 的预览；`logAvailable` 与 `logPath` 必须保持一致：可回查时为 `true` 和路径，否则为 `false` 和 `null`。长输出命令必须使两路完整日志均可回查；宿主无法做到时将 `degraded` 设为 `true`，把缺失项以 JSON Pointer 字符串（例如 `/stdout/logPath`）写入 `missingFields`，不得宣称满足完整协议。
- `postcondition.checked` 为 `false` 时，`postcondition.passed` 和 `postcondition.summary` 必须为 `null`，表示尚未验证；为 `true` 时，`passed` 必须是布尔值，`summary` 写明验证结论。它由 agent 按验收标准填进执行结果（执行层支持回填就回填进结构，不支持的记进执行摘要或该角色自己的 `.pipeline/` 文件），执行层不能猜测。

## 业务语义在哪里

测试数量、失败用例、构建产物和迁移状态由测试工具的机器可读输出、项目适配器或明确的后置验证提供；不能从通用 `preview` 或退出码推断出来。宿主按以下顺序适配：

1. 宿主已有结构化命令执行器时，使用它并映射到本结构。
2. 宿主没有现成执行器但能运行脚本时，用宿主可用的 shell（Bash、PowerShell、sh 等）在系统临时目录生成包装脚本，捕获完整 stdout/stderr 并输出本结构；脚本用完即删。
3. 只能直接执行命令时，尽量保存长输出、按上述规则记录可获得的字段并标记缺失（`degraded` 与 `missingFields`）；关键验收必须改用更窄或机器可读的命令，或换能完整保存日志的环境重跑——不能靠一份存不下的日志过关（同 `SKILL.md` 第 5 条）。

`执行结果`是固定结构；`执行摘要`只是从它生成、用于节省上下文的有限视图。任何一层都不能用 `postcondition.passed` 代替实际验证。
