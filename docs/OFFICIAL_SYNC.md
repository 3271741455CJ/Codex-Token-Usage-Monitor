# Official account synchronization / 官方账号同步

The owner authorized optional official synchronization on 2026-10-29. Default collection and the HTML viewer remain offline. The current version is still the unpublished 0.1.0 baseline; this addition is under Unreleased.

## Run / 使用

```powershell
python -I -S -B .\run.py --sync-official
```

Requires the Windows Store installation of the official Codex desktop app and a readable ChatGPT login in the selected Codex home's `auth.json`. The adapter selects the highest installed `OpenAI.Codex_*__2p2nqsd0c76g0` package's `app/resources/codex.exe`. It does not execute PATH shims or download software. API-key-only login, credential-store-only login and other operating systems are not supported by this optional adapter. The ordinary collector remains usable.

No-argument `run.py` remains static and offline. The interactive launcher uses loopback only unless `--sync-official` is supplied; its update button then requests a fresh official snapshot through the guarded worker. Standalone HTML refresh never contacts the service. Run the command again for a new snapshot. `--json` also saves the allowlisted official data in the private report JSON. No separate manual snapshot import is implemented.

## Data contract / 数据口径

Official documentation checked on 2026-10-29:

- [Codex app-server account methods](https://learn.chatgpt.com/docs/app-server#auth-endpoints): `account/usage/read` returns `summary` and optional `dailyUsageBuckets`; `account/rateLimits/read` returns window snapshots.
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference): ephemeral credentials and telemetry controls.

| Official data | Display |
| --- | --- |
| `lifetimeTokens`, `peakDailyTokens` | Account cumulative and peak daily Token values |
| `longestRunningTurnSec` | Longest-running turn in seconds, not Tokens |
| `currentStreakDays`, `longestStreakDays` | Activity streak days |
| `dailyUsageBuckets[].startDate`, `tokens` | Daily chart and paginated table, original service dates |
| `rateLimitsByLimitId` / legacy `rateLimits` | Prefer the map; never sum it with the legacy field |
| Window percentage, duration, reset time | Remaining percentage at capture; expired or unknown reset is labeled |
| Numeric credits balance and credit flags | Balance is not a Token count; arbitrary response text is not retained |

Account statistics can reflect other devices to the extent included by the official service. These methods do not promise a complete per-device, per-model or per-turn remote ledger. We cannot manufacture details absent from both the API and local logs. A null field remains unknown; an empty daily list does not imply zero lifetime usage. Official daily dates are not converted to local time.

官方账号统计和本地明细分别展示。官方统计不受本地模型、日期或创建者筛选影响，不与本地 Token 相加，也不计算“官方减本地＝其他电脑用量”。统计窗口、时区、同步延迟、登录账号切换和本地缺失日志都会影响比较。接口成功只表示取得官方响应，不证明与用户网页同时刻、同范围逐项相等；本项目未登录网页抓取或验证 overview / analytics 页面的一致性。

## Credential and execution boundary / 凭据与执行边界

1. Only `--sync-official` authorizes one exact official stdio child process. Python sockets, arbitrary subprocesses, source writes and original SQLite connections remain blocked.
2. Use a fresh `.official-*` directory inside the allowed output. Set the child home, Codex home, app-data and temporary paths there. Do not copy original config, credentials, sessions or databases. Do not inherit API keys, proxy/endpoint overrides or telemetry environment variables.
3. Before sending authentication, read effective configuration and require ephemeral credential storage, the official ChatGPT base URL, OpenAI provider, disabled analytics/OTel/update checks/hooks, and no configured MCP servers/notify hooks. Unexpected configuration fails closed.
4. The owner explicitly permits the selected login's necessary access token and account ID solely for OpenAI official authentication; no other destination or credential output is permitted. Read only those authentication fields. Send them over private stdin using the documented experimental `chatgptAuthTokens` mode. Do not pass secrets in command arguments or environment variables; never read or send refresh tokens for renewal. A renewal request is refused; the user must restore login using the official app.
5. Request only usage and limits after authentication. Never start a model turn, consume a reset, buy credits, email anyone, change the original login or upload local logs. Discard server error text and stderr; expose only fixed status codes. Responses have size/time bounds and an output allowlist.
6. Recheck the selected account after synchronization; discard the snapshot if it changed. Kill the isolated process and remove its temporary directory. Cleanup failure is visible in the report. Before HTML/JSON serialization, the shared privacy layer removes identities, titles, credential fragments and paths, replacing sensitive originals with anonymous references/local viewing guides. CSV uses that sanitized data. Usage statistics still must stay local.

The official native executable, OS, and managed machine policies remain trusted components. The Python audit hook is not an OS sandbox for that child. Configuration checks and memory-only authentication reduce exposure but do not justify an absolute guarantee against a compromised OS/client or future client bugs. No firewall configuration is changed. HTTP is performed by the official client, not by a copied private-web-API implementation.

## Failure behavior / 失败处理

Missing client/login, account changes, unsafe effective configuration, timeout and unsupported methods are explicit states. Usage and limits can fail independently. Local collection continues; it never substitutes local totals for failed official totals. Captured data is a timestamped snapshot even when the request just succeeded. Do not label it permanently live or complete.
