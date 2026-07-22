# 基于 Raft 的分布式 KV 数据库

这是“大数据存储技术”课程作业项目，实现了一个可独立运行的 Raft 分布式 KV 数据库。系统使用 Go 标准库、HTTP + JSON RPC 和本地 JSON 文件持久化，默认提供三节点配置，并支持按配置文件扩展节点数。选举、日志复制和提交逻辑根据当前成员数计算多数派，完整提供 Leader 选举、心跳、日志复制、多数派提交、Put / Get / Delete、快照压缩、Lease Read、成员变更与 Web 可视化控制台。

## 环境要求

- Go 1.21 或以上；
- Windows PowerShell / CMD，或 Linux / macOS 终端；
- 不需要 Docker、Redis、MySQL 或其他外部数据库。

如果 Go 已安装但未加入 PATH，可以使用绝对路径执行，例如 Windows 下 `D:\Go\bin\go.exe test ./...`。

## 目录结构

```text
cmd/node/          节点启动入口
config/            三节点与五节点集群配置
raft/              Raft 选举、日志复制、持久化和节点状态
kv/                KV 状态机
server/            HTTP API 与 Raft RPC
server/static/     内置 Web 前端页面
scripts/           Windows 和 Linux/macOS 启动测试脚本
tools/bonuscheck/  全功能自动验收与 SVG 图表生成命令
data/              节点持久化目录
logs/              运行日志目录
report/            中文开发报告与测试结果
report/screenshots/ 真实运行截图，已按时间顺序和测试场景重命名
```


## 编译与测试

```bash
go test -buildvcs=false ./...
go build -buildvcs=false -o raft-kv-node ./cmd/node
```

测试代码不是只依赖命令行脚本：

- `kv/state_machine_test.go`：KV 状态机单元测试；
- `raft/node_test.go`：Raft 投票、日志复制、快照和成员变更单元测试；
- `server/integration_test.go`：真实 HTTP/RPC 多节点集成测试，覆盖 Follower 重定向、Leader 宕机、五节点容错、快照、Lease Read 和动态添加节点。

Windows 如果遇到 build cache 权限问题，可临时指定项目内缓存：

```powershell
$env:GOCACHE = (Resolve-Path .).Path + "\.gocache"
go test -buildvcs=false ./...
```

全功能自动验收与画图：

```powershell
$env:GOCACHE = (Resolve-Path .).Path + "\.gocache"
D:\Go\bin\go.exe run -buildvcs=false ./tools/bonuscheck -out report/bonus_artifacts
```

该命令会自动启动临时真实集群，覆盖核心 Put/Get/Delete、Follower 重定向、Follower 宕机继续写、Leader 宕机重选主、快照、Lease Read 和动态添加节点，并额外运行五节点集成测试，最后生成 JSON、Markdown 摘要和 SVG 图表。

## 启动三节点

手动启动：

```bash
go run -buildvcs=false ./cmd/node --id=1 --config=config/cluster.json
go run -buildvcs=false ./cmd/node --id=2 --config=config/cluster.json
go run -buildvcs=false ./cmd/node --id=3 --config=config/cluster.json
```

Windows 脚本启动：

```bat
scripts\start_cluster.bat
```

Web 前端：

```text
http://127.0.0.1:8001/ui/
http://127.0.0.1:8002/ui/
http://127.0.0.1:8003/ui/
```

前端随每个节点的 API 端口一起提供。页面会展示节点状态、Leader、提交进度、日志与快照字段，并提供 Put、Get、Delete、添加节点和移除节点操作；写入类操作会自动根据 `/leader` 路由到当前 Leader。

Linux / macOS：

```bash
chmod +x scripts/*.sh
./scripts/start_cluster.sh
```

## 启动五节点

五节点配置用于展示系统不局限于 3 个节点，端口为 API `8001-8005`、Raft RPC `9001-9005`：

```bat
scripts\start_cluster5.bat
```

```bash
./scripts/start_cluster5.sh
```

也可以手动启动任意配置文件中的节点：

```bash
go run -buildvcs=false ./cmd/node --id=4 --config=config/cluster5.json
go run -buildvcs=false ./cmd/node --id=5 --config=config/cluster5.json
```

停止集群：

```bat
scripts\stop_cluster.bat
```

```bash
./scripts/stop_cluster.sh
```

## HTTP API

查询节点状态：

```bash
curl http://127.0.0.1:8001/status
```

查询 Leader：

```bash
curl http://127.0.0.1:8001/leader
```

写入键值：

```bash
curl -X POST http://127.0.0.1:8001/kv/put -H "Content-Type: application/json" -d "{\"key\":\"name\",\"value\":\"raft\"}"
```

读取键值：

```bash
curl http://127.0.0.1:8001/kv/get?key=name
```

删除键值：

```bash
curl -X POST http://127.0.0.1:8001/kv/delete -H "Content-Type: application/json" -d "{\"key\":\"name\"}"
```

查询当前成员：

```bash
curl http://127.0.0.1:8001/cluster
```

添加节点需要先向当前 Leader 提交成员变更日志，然后再启动新节点进程：

```bash
curl -X POST http://127.0.0.1:8001/cluster/add -H "Content-Type: application/json" -d "{\"id\":4,\"api_addr\":\"127.0.0.1:8004\",\"raft_addr\":\"127.0.0.1:9004\",\"data_dir\":\"data/node4\"}"
go run ./cmd/node --id=4 --config=config/cluster5.json
```

移除节点：

```bash
curl -X POST http://127.0.0.1:8001/cluster/remove -H "Content-Type: application/json" -d "{\"id\":4}"
```

如果请求发到 Follower，系统会返回：

```json
{
  "error": "not leader",
  "leader_id": 1,
  "leader_addr": "127.0.0.1:8001"
}
```

## 故障测试

基础 KV 测试：

```bat
scripts\test_basic.bat
```

Leader 宕机切换测试：

```bat
scripts\test_leader_failover.bat
```

手动测试建议：

1. 启动 3 个节点并等待 2 秒；
2. 访问 8001、8002、8003 的 `/status`，确认只有一个 Leader；
3. 关闭一个 Follower，继续向 Leader 写入；
4. 关闭 Leader，等待 1 到 3 秒，确认剩余节点重新选举；
5. 重启旧 Leader，确认最终只有一个 Leader。

## 已实现功能

- 默认三节点 Raft 集群配置；
- 支持按配置文件启动 3、5 或更多节点；
- Follower / Candidate / Leader 状态转换；
- 随机选举超时与心跳；
- RequestVote 与 AppendEntries RPC；
- 日志匹配检查、冲突截断、追加复制；
- 多数派提交与状态机应用；
- Put / Get / Delete；
- 非 Leader 返回 Leader 信息；
- currentTerm、votedFor、log、commitIndex、lastApplied、snapshot、peers 本地持久化；
- 快照压缩与 InstallSnapshot 追赶落后节点；
- Lease Read：Leader 读前确认多数派租约，不为读请求追加日志；
- 简化动态成员变更：`/cluster/add`、`/cluster/remove` 通过 Raft 日志提交后生效；
- Follower 宕机后继续写入；
- Leader 宕机后自动重新选举；
- Go 单元测试、真实 HTTP 集成测试和 Windows/Linux 脚本；

## 简化与未实现功能

- 动态成员变更为简化版，未实现生产级 Raft joint consensus；
- Lease Read 使用多数派心跳确认租约，未实现完整 ReadIndex；
- 网络分区通过多数派和 term 机制处理，未提供复杂网络代理模拟。

## 常见问题

1. `go` 命令找不到：确认 Go 已安装并加入 PATH，或使用 `D:\Go\bin\go.exe` 这类绝对路径。
2. 端口被占用：运行 `scripts\stop_cluster.bat`，或手动释放 8001-8005、9001-9005。
3. 写请求返回 `not leader`：先访问 `/leader` 或 `/status` 找到 Leader，再向 Leader 端口重试。
4. 重启后状态不干净：删除 `data/node*/state.json` 后重新启动集群。
