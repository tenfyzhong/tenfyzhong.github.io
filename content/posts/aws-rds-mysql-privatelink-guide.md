---
title: "AWS RDS MySQL 配置 AWS PrivateLink 教程：安全对接 TiDB Cloud DM"
date: 2026-08-28T00:00:00+08:00
draft: false
categories:
  - "运维"
tags:
  - "aws"
  - "amazon-rds"
  - "aws-privatelink"
  - "mysql"
keywords: "AWS RDS MySQL, AWS PrivateLink, Network Load Balancer, NLB, TiDB Cloud DM, VPC Endpoint Service"
---

如果需要让其他 VPC，或 TiDB Cloud DM 这类第三方云服务访问 AWS RDS MySQL，又不希望把数据库暴露到公网，AWS PrivateLink 是一个合适的连接方式。

PrivateLink 不能把 RDS 实例直接发布为 Endpoint Service。一个可行的链路是：在 RDS 前放置 Internal Network Load Balancer（NLB），将 RDS 的私网 IP 注册到 IP 类型 Target Group，再由 NLB 创建 VPC Endpoint Service，供消费者创建 Interface Endpoint。

本文以 MySQL 的 3306 端口为例，说明从配置到验证的完整过程，并重点处理 RDS IP 变化这一生产环境风险。

<!-- more -->

# 整体架构

最终链路如下：

```text
TiDB Cloud DM / 其他消费者
          │
          │ Interface VPC Endpoint
          ▼
AWS PrivateLink Endpoint Service
          │
          ▼
Internal Network Load Balancer
          │
          ▼
IP Target Group
          │
          ▼
Amazon RDS MySQL（Private IP:3306）
```

所有数据流量都在 AWS 私有网络中传递；RDS 不需要开启公网访问。

# 前置条件

开始前，请确认已有以下资源和信息：

- 一个 VPC，以及一台能访问 RDS 的 VPC 内 EC2，供后续验证。
- 一个运行在私有子网中的 RDS MySQL 实例；建议确认 `Publicly accessible` 为 `No`。
- RDS 的 Endpoint、端口、VPC、子网、可用区和安全组。例如 Endpoint 为 `mydb.xxxxxx.ap-southeast-1.rds.amazonaws.com`，端口为 `3306`。
- 消费方提供的 AWS Principal。若接入 TiDB Cloud，应以其 Private Endpoint 页面提供的账号或 Principal 为准。

NLB、Endpoint Service 和 RDS 必须位于同一 Region；NLB 与 RDS 必须位于同一个 VPC。

## 记录 RDS 的网络信息

进入以下页面，先把后续配置会用到的值记录下来：

```text
AWS Console → RDS → Databases → 选择目标数据库 → Connectivity & security
```

至少记录：

```text
VPC
Subnets
Availability Zone
Endpoint
Port
Security Group
```

例如：

```text
VPC: vpc-0123456789abcdef
Availability Zone: ap-southeast-1a
Endpoint: mydb.xxxxxx.ap-southeast-1.rds.amazonaws.com
Port: 3306
```

创建 NLB 时必须选择这个 VPC。RDS 所在可用区不必与每一个 NLB 子网完全相同，但 NLB 应覆盖多个可用区。

# 先获取并理解 RDS 的私网 IP

在 VPC 内能解析 RDS DNS 的主机上执行：

```bash
dig +short mydb.xxxxxx.ap-southeast-1.rds.amazonaws.com
```

也可以使用：

```bash
nslookup mydb.xxxxxx.ap-southeast-1.rds.amazonaws.com
```

假设结果为 `10.0.21.135`。稍后会将 `10.0.21.135:3306` 注册到 NLB 的 Target Group。

这里有一个不能忽略的限制：RDS Endpoint 是稳定的 DNS 名称，但其背后的私网 IP 并不保证不变。故障转移、维护或底层实例替换后，DNS 可能解析到新 IP。先用手工方式打通链路没有问题，但生产环境必须为 IP 漂移准备同步机制，本文后面会展开说明。

# 创建 IP 类型 Target Group

进入 AWS Console：

```text
EC2 → Load Balancing → Target Groups → Create target group
```

关键配置如下：

```text
Name: rds-mysql-tg
Target type: IP addresses
Protocol: TCP
Port: 3306
IP address type: IPv4
VPC: RDS 所在 VPC
```

不要选择 `Instances`，因为 RDS 不是账户内可注册的 EC2 实例。

Health Check 同样选择 TCP，并使用流量端口：

```text
Health check protocol: TCP
Health check port: Traffic port
```

MySQL 不是 HTTP 服务，因此不应使用 HTTP 或 HTTPS 健康检查。

在 Target Group 的 **Targets** 页面注册刚刚解析到的私网 IP：

```text
IP address: 10.0.21.135
Port: 3306
```

在控制台中依次选择 `Include as pending below` 和 `Register pending targets`，将 `10.0.21.135:3306` 加入 Target Group。刚注册时 Target 可能显示 `initial`。等待一段时间后，它应变为 `healthy`；在此之前不要继续配置 PrivateLink。

# 配置并检查 RDS Security Group

`Health checks failed` 最常见的原因之一是 NLB 无法连接 RDS。不要只看 PrivateLink 的状态，先明确检查 RDS 的入站规则。

进入：

```text
EC2 → Security Groups → 选择 RDS 使用的 Security Group → Inbound rules → Edit inbound rules
```

添加或确认以下规则：

```text
Type: MySQL/Aurora
Protocol: TCP
Port range: 3306
Source: 允许 NLB 到 RDS 的来源
```

`Source` 应按实际网络设计收紧。若创建 NLB 时为其关联了 Security Group，可在 RDS 安全组中引用该 NLB Security Group；如果没有，则使用 NLB 所在子网的精确 CIDR 或组织已定义的受控网段。不要为了排障临时开放 `0.0.0.0/0` 后忘记收回。

保存后回到：

```text
EC2 → Target Groups → 选择 rds-mysql-tg → Targets
```

等待健康检查。目标 `10.0.21.135:3306` 必须变为 `healthy` 才能继续。

还要检查网络路径没有被以下任一项阻断：

- Target Group 所选 VPC 与 RDS 所在 VPC 不一致。
- RDS 或 NLB 子网使用自定义 Network ACL，但没有允许 TCP 3306 以及返回流量。
- 路由表不允许 NLB 所在子网访问 RDS 子网。

先从同一 VPC 内的 EC2 直接测试 RDS：

```bash
nc -vz mydb.xxxxxx.ap-southeast-1.rds.amazonaws.com 3306
```

如果这一步失败，应先排查 RDS 安全组、NACL 和路由，而不是继续检查 PrivateLink。

# 创建 Internal Network Load Balancer

进入：

```text
EC2 → Load Balancers → Create load balancer → Network Load Balancer
```

选择 **Network Load Balancer**，而不是 Application Load Balancer。配置建议如下：

```text
Name: rds-mysql-nlb
Scheme: Internal
IP address type: IPv4
VPC: RDS 所在 VPC
```

选择至少两个私有子网、覆盖多个可用区可以提高 NLB 的可用性。NLB 子网不必与 RDS 使用同一个子网，但必须在同一个 VPC 中；这个场景不需要 Internet Gateway，也不应创建 Internet-facing NLB。

例如可以采用以下分布：

```text
VPC
├── ap-southeast-1a
│   ├── private-subnet-a（NLB）
│   └── RDS subnet
└── ap-southeast-1b
    ├── private-subnet-b（NLB）
    └── RDS subnet
```

接着创建 Listener：

```text
Protocol: TCP
Port: 3306
Default action: Forward to rds-mysql-tg
```

流量关系应为：

```text
NLB:3306 → Target Group:3306 → RDS:3306
```

# 验证 NLB 后再创建 PrivateLink

创建完成后，复制 NLB 的 DNS 名称，例如：

```text
internal-rds-mysql-nlb-xxxx.elb.amazonaws.com
```

从 VPC 内 EC2 验证 TCP 连通性：

```bash
nc -vz internal-rds-mysql-nlb-xxxx.elb.amazonaws.com 3306
```

成功时通常会看到类似 `Connection to ... 3306 port [tcp/mysql] succeeded!` 的输出。

也可以使用真实账号测试 MySQL：

```bash
mysql \
  -h internal-rds-mysql-nlb-xxxx.elb.amazonaws.com \
  -P 3306 \
  -u myuser \
  -p
```

推荐按以下顺序验证，能把问题隔离在最小的范围内：

```text
EC2 → RDS
       ↓
Target Group healthy
       ↓
EC2 → NLB → RDS
       ↓
PrivateLink
```

# 创建 VPC Endpoint Service

确认 NLB 正常后，进入：

```text
VPC → PrivateLink and Lattice → Endpoint services → Create endpoint service
```

选择：

```text
Load balancer type: Network
Available load balancer: rds-mysql-nlb
```

如果列表中找不到 NLB，通常是因为 NLB 类型不对、尚未创建完成，或当前控制台 Region 与 NLB 不一致。

请逐一确认 RDS、NLB 和 Endpoint Service 都位于目标 Region，例如均为 `ap-southeast-1`。

建议开启 `Acceptance required`。这样消费者创建 Interface Endpoint 后，需要由服务提供方手动批准，特别适合连接 TiDB Cloud 等外部账号。

创建后，AWS 会生成 Endpoint Service Name，形如：

```text
com.amazonaws.vpce.ap-southeast-1.vpce-svc-0123456789abcdef
```

这是交给消费者配置 PrivateLink 的核心参数。

# 限制消费者并接受连接

Endpoint Service 默认不会允许任意 AWS 账号连接。打开该服务的 **Allow principals**，添加消费者给出的 Principal，例如：

```text
arn:aws:iam::123456789012:root
```

生产环境不要使用 `*`。仅授权确实需要连接的账号，后续也更容易审计。

在 TiDB Cloud DM 或其他消费者的 Private Endpoint 配置页面中，填写所在 Region、Endpoint Service Name，以及其要求的可用区信息。消费者提交后，回到 AWS：

```text
VPC → Endpoint services → 选择服务 → Endpoint connections
```

确认请求来源正确，接受状态为 `Pending acceptance` 的连接。状态变为 `Available` 后，PrivateLink 网络链路即建立完成。

在控制台中的完整操作是：

```text
VPC → Endpoint services → 选择 Endpoint Service → Endpoint connections
Actions → Accept endpoint connection request
```

# `Health checks failed` 的排查顺序

Target Group 显示 `Unhealthy` 或 `Health checks failed` 时，按以下顺序检查：

1. 重新执行 `dig +short <RDS Endpoint>`，确认当前 DNS 解析结果与 Target Group 中的 IP 一致。
2. 确认 Target Group 的类型为 `IP addresses`，且 VPC 与 RDS 相同。
3. 确认健康检查为 TCP，端口为 `traffic port`（即 3306）。
4. 进入 RDS Security Group 的 **Inbound rules**，确认 `MySQL/Aurora`、`TCP`、`3306` 和正确的 NLB 来源均存在。
5. 检查两侧子网的 NACL、路由和直接的 `EC2 → RDS` 测试结果。

不要从 PrivateLink 端开始猜测。只要 `EC2 → NLB → RDS` 尚未连通，Endpoint Service 不会让问题变得更容易定位。

# 生产环境：处理 RDS IP 漂移

NLB 的 IP 类型 Target Group 保存的是 `10.0.21.135` 这样的地址，而不是 RDS DNS 名称。因此 RDS 发生故障转移后，即使数据库 Endpoint 没变，NLB 仍可能把流量发往旧 IP，导致 PrivateLink 中断。

建议用 EventBridge 事件或定时任务触发 Lambda（或其他自动化程序）执行以下逻辑：

```text
解析 RDS Endpoint
       ↓
读取 Target Group 当前目标
       ↓
发现 IP 不一致
       ↓
注册新 IP 并等待 healthy
       ↓
注销旧 IP
```

先注册新 IP、确认健康后再注销旧 IP，可以缩短切换期间的不可用窗口。自动化所使用的 IAM 身份需要具备解析 DNS、读取 Target Health、注册和注销 Target 的相应权限。

# 上线前检查清单

- [ ] RDS 未开启公网访问，且能从 VPC 内连接 3306。
- [ ] 已记录 RDS 的 VPC、子网、可用区、Endpoint、端口和 Security Group。
- [ ] Target Group 为 IP 类型、TCP 3306，健康检查为 TCP，状态为 `healthy`。
- [ ] NLB 为 Internal 类型，Listener 将 TCP 3306 转发到该 Target Group。
- [ ] NLB 与 RDS 已在 VPC 内完成端到端验证。
- [ ] Endpoint Service 关联了正确的 NLB，并限制了 Allowed Principals。
- [ ] 消费方的 Endpoint connection 已被确认并显示为 `Available`。
- [ ] RDS Security Group、NACL 与路由表均允许 NLB 到 RDS 的网络路径。
- [ ] 已为 RDS 私网 IP 变化准备监控或自动同步机制。

完成这些检查后，消费者就能在不暴露 RDS 公网地址的前提下，通过 AWS PrivateLink 访问 MySQL。
