---
title: "AWS CLI v2 使用教程：从安装配置到自动化实战"
date: 2026-07-28T00:00:00+08:00
draft: false
categories:
  - "工具"
tags:
  - "aws-cli"
  - "aws"
  - "automation"
  - "tutorial"
keywords: "AWS CLI, AWS CLI v2, IAM Identity Center, SSO, Profile, JMESPath, S3, EC2"
---

管理 AWS 资源不一定要反复打开控制台。AWS CLI 可以在终端里调用几乎所有 AWS 服务，既适合临时查询，也适合编写自动化脚本。

本文以 AWS CLI v2 为基础，从安装、认证和 Profile 管理开始，逐步介绍 S3、EC2、输出过滤、分页与排错。读完后，你将能够建立一套安全、可复用的 AWS 命令行工作流。

<!-- more -->

# AWS CLI 是什么？

AWS CLI（AWS Command Line Interface）是 AWS 官方提供的命令行工具。它的基本命令结构非常统一：

```text
aws <service> <operation> [parameters]
```

例如：

```bash
# 查看当前调用者身份
aws sts get-caller-identity

# 查看 S3 Bucket
aws s3 ls

# 查看 EC2 实例
aws ec2 describe-instances
```

这里的 `sts`、`s3` 和 `ec2` 是服务名，`get-caller-identity`、`ls` 和 `describe-instances` 是操作名。

AWS CLI v2 还提供了 SSO、自动提示、YAML 输出等能力。新安装时应直接使用 v2；如果电脑里已经有 v1，需要注意两个版本都使用同一个 `aws` 命令。

# 安装 AWS CLI v2

## macOS

使用 AWS 官方安装包：

```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg ./AWSCLIV2.pkg -target /
```

安装完成后可以删除下载的 `AWSCLIV2.pkg`。

## Linux

x86_64 系统执行：

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

ARM64（AArch64）系统将下载地址改为：

```text
https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip
```

以后更新官方安装版本时，重新下载安装包并执行：

```bash
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
```

正式环境还可以按照官方文档校验安装包的 PGP 签名，防止使用损坏或被篡改的文件。

## Windows

下载并运行 64 位 MSI 安装包：

```text
https://awscli.amazonaws.com/AWSCLIV2.msi
```

安装后重新打开 PowerShell 或命令提示符，让新的 `PATH` 生效。

## 验证安装结果

```bash
aws --version
```

正常情况下会看到以 `aws-cli/2.` 开头的版本信息。如果显示的仍然是 v1，可以用以下命令确认实际执行的是哪个文件：

```bash
# macOS 或 Linux
which aws

# Windows
where aws
```

# 配置身份认证

AWS CLI 发出的每个请求都需要明确三件事：

1. **我是谁**：凭证对应的用户或角色。
2. **我能做什么**：IAM 策略授予的权限。
3. **操作哪里**：目标 Region，例如 `ap-southeast-1`。

对于人工用户，AWS 的安全最佳实践是使用身份联合和临时凭证。最常见的选择是 IAM Identity Center（原 AWS SSO）。长期 Access Key 更适合无法使用角色或临时凭证的兼容场景，不应为日常使用创建 Root 用户 Access Key。

## 推荐方式：IAM Identity Center（SSO）

如果公司已经配置 IAM Identity Center，执行：

```bash
aws configure sso --profile company-dev
```

根据提示填写 SSO Session 名称、Start URL、SSO Region，并选择 AWS 账号和角色。配置完成后登录：

```bash
aws sso login --profile company-dev
```

浏览器认证成功后，先验证身份：

```bash
aws sts get-caller-identity --profile company-dev
```

输出中的 `Account` 是账号 ID，`Arn` 表示当前使用的角色。SSO 会使用可过期的临时凭证；会话过期后重新运行 `aws sso login` 即可。需要清除本地缓存的 SSO 会话时执行：

```bash
aws sso logout
```

## 兼容方式：Access Key

只有在不能使用 SSO 或 IAM Role 时，才考虑配置 IAM 用户的 Access Key：

```bash
aws configure --profile personal
```

命令会依次询问：

```text
AWS Access Key ID [None]:
AWS Secret Access Key [None]:
Default region name [None]: ap-southeast-1
Default output format [None]: json
```

请为 IAM 用户配置最小权限，不要使用 Root 用户密钥，也不要把真实凭证写进代码、Git 仓库、聊天记录或博客示例。

`aws configure` 默认把内容保存在两个文件中：

```text
~/.aws/credentials  # Access Key 等敏感凭证
~/.aws/config       # Region、输出格式、角色和 SSO 配置
```

这两个文件都是明文文件，应限制文件权限并避免被同步到公开位置。

# 使用 Profile 管理多个环境

如果同时管理个人账号、开发环境和生产环境，不要反复覆盖 `default`，而应为每个环境创建独立 Profile：

```bash
aws configure --profile personal
aws configure sso --profile company-dev
aws configure sso --profile company-prod
```

查看已有 Profile：

```bash
aws configure list-profiles
```

单次命令使用指定 Profile：

```bash
aws s3 ls --profile company-dev
```

连续执行多条命令时，可以在当前 Shell 会话设置环境变量：

```bash
export AWS_PROFILE=company-dev
export AWS_REGION=ap-southeast-1
```

之后就不必为每个命令添加 `--profile` 和 `--region`。操作完成后可以取消变量：

```bash
unset AWS_PROFILE
unset AWS_REGION
```

当结果与预期不一致时，下面这个命令非常重要：

```bash
aws configure list --profile company-dev
```

它不仅显示当前使用的 Profile、凭证和 Region，还会告诉你每个值来自配置文件、环境变量还是其他位置。

实践中，命令行参数可以覆盖本次命令的环境变量和 Profile 配置，环境变量又可以覆盖 Profile 中的同名设置。因此排错时不要只查看 `~/.aws/config`，还要检查当前 Shell 的环境变量。

# 先掌握帮助系统

AWS 服务和参数非常多，没有必要全部背下来。CLI 自带分层帮助：

```bash
aws help
aws s3 help
aws s3 cp help
aws ec2 describe-instances help
```

AWS CLI v2 还可以为陌生命令打开交互式提示：

```bash
aws dynamodb list-tables --cli-auto-prompt
```

它会提示可用参数和部分资源值，适合探索命令；自动化脚本中则不要开启交互提示。

# S3 常用操作

AWS CLI 的 `s3` 子命令是易用的高级封装，适合文件传输；`s3api` 更接近底层 API，参数更完整。

## 查看 Bucket 和对象

```bash
# 查看当前账号可访问的 Bucket
aws s3 ls

# 查看指定 Bucket 的对象
aws s3 ls s3://example-bucket/

# 递归查看指定前缀下的对象
aws s3 ls s3://example-bucket/backups/ --recursive --human-readable --summarize
```

Bucket 名称在整个 AWS 分区内需要唯一。请把示例中的 `example-bucket` 替换成自己的名称。

## 上传和下载文件

```bash
# 上传单个文件
aws s3 cp ./report.csv s3://example-bucket/reports/report.csv

# 下载单个文件
aws s3 cp s3://example-bucket/reports/report.csv ./report.csv

# 递归复制目录
aws s3 cp ./dist/ s3://example-bucket/site/ --recursive
```

## 同步目录

```bash
# 先预览将要发生的变化
aws s3 sync ./dist/ s3://example-bucket/site/ --dryrun

# 确认无误后执行同步
aws s3 sync ./dist/ s3://example-bucket/site/
```

如果添加 `--delete`，目标端多出来的对象会被删除：

```bash
aws s3 sync ./dist/ s3://example-bucket/site/ --delete --dryrun
```

务必先保留 `--dryrun` 检查结果，再执行真正的删除同步。还要注意：S3 高级命令使用的是 `--dryrun`，而部分 EC2 API 使用的是 `--dry-run`，两者拼写不同。

# 查询 EC2 实例

直接执行 `describe-instances` 会返回大量嵌套 JSON：

```bash
aws ec2 describe-instances
```

更实用的方式是先用服务端 Filter 只请求运行中的实例，再用 `--query` 整理字段：

```bash
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].{Name:Tags[?Key==`Name`].Value | [0],ID:InstanceId,Type:InstanceType,AZ:Placement.AvailabilityZone}' \
  --output table
```

这里发生了两次过滤：

- `--filters` 由 EC2 服务端执行，减少返回的数据量。
- `--query` 由本地 AWS CLI 使用 JMESPath 表达式执行，负责挑选和重组字段。

如果只需要实例 ID，可输出为纯文本：

```bash
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text
```

停止实例属于有影响的操作。执行前先确认账号、Region 和实例 ID，并使用 EC2 支持的 `--dry-run` 检查权限与参数：

```bash
aws sts get-caller-identity
aws configure get region
aws ec2 stop-instances --instance-ids i-0123456789abcdef0 --dry-run
```

EC2 的 Dry Run 成功时通常会返回 `DryRunOperation` 错误，表示请求本来可以执行但被演练模式拦截；`UnauthorizedOperation` 则表示权限不足。确认无误后去掉 `--dry-run` 才会真正停止实例。

# 控制输出：output、query 与过滤

## 选择输出格式

常用输出格式包括：

- `json`：默认格式，结构稳定，适合程序处理。
- `yaml`：适合阅读层级较深的数据。
- `table`：适合人直接查看。
- `text`：以制表符分隔，适合配合 Shell 工具使用。
- `off`：不向标准输出写入结果，适合只检查退出码的脚本。

单次指定格式：

```bash
aws sts get-caller-identity --output table
```

为 Profile 设置默认格式：

```bash
aws configure set output json --profile company-dev
```

当脚本使用 `text` 时，建议始终搭配 `--query` 明确字段及其顺序，不要依赖服务返回对象的默认字段顺序。

## 使用 JMESPath 查询

`--query` 使用 JMESPath 语法。以下是几个实用例子：

```bash
# 只返回当前账号 ID
aws sts get-caller-identity --query Account --output text

# 提取所有 Bucket 名称
aws s3api list-buckets --query 'Buckets[].Name' --output text

# 将结果重组为表格
aws iam list-users \
  --query 'Users[].{User:UserName,Created:CreateDate,Arn:Arn}' \
  --output table
```

在 macOS 和 Linux Shell 中，通常用单引号包裹查询表达式，避免反引号等字符被 Shell 解释。PowerShell 和 Windows 命令提示符的引号规则不同，复杂表达式需要按对应终端调整。

# 理解两种“分页”

AWS CLI v2 中有两个容易混淆的概念。

## 终端翻页器

CLI v2 默认可能把输出交给 `less` 等翻页器。看到终端停在冒号或 `(END)` 时，按 `q` 退出即可。

只为一次命令关闭翻页器：

```bash
aws ec2 describe-instances --no-cli-pager
```

在当前 Shell 会话全部关闭：

```bash
export AWS_PAGER=""
```

## API 结果分页

许多 List 或 Describe API 每次只返回一页结果。AWS CLI 默认会自动请求后续页面并合并输出。

- `--page-size`：调整每次向服务请求的数据量，不代表最终只返回这么多条。
- `--max-items`：限制 CLI 最终返回的总条数。
- `--starting-token`：从上一次结果的 Token 继续读取。
- `--no-paginate`：关闭自动分页，只请求服务端第一页。

例如只查看前 50 个 IAM 用户：

```bash
aws iam list-users --max-items 50
```

自动化处理大量资源时，要明确自己需要“全部结果”还是“限制总数”，不要误把 `--page-size` 当作总数限制。

# 复杂参数放进文件

命令参数包含多层 JSON 时，直接写在 Shell 里很容易遇到转义问题。可以先生成输入模板：

```bash
aws ec2 run-instances --generate-cli-skeleton input > run-instances.json
```

编辑完成后从文件加载：

```bash
aws ec2 run-instances --cli-input-json file://run-instances.json --dry-run
```

文本参数通常使用 `file://`，必须按原始字节读取的二进制参数使用 `fileb://`。生成的 Skeleton 适合做当前 CLI 版本的起点，但其结构不保证跨版本稳定，团队自动化中应固定并审查实际输入文件。

# 在脚本中可靠地使用 AWS CLI

## 先验证运行上下文

执行写操作前，建议输出或校验账号与 Region：

```bash
aws sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output table
aws configure get region
```

这一步可以减少在错误账号或错误 Region 操作资源的风险。生产脚本还应显式传入预期 Profile 和 Region，而不是依赖操作者电脑上的 `default`。

## 检查退出码

AWS CLI 成功时退出码通常是 `0`，失败时为非零。Shell 脚本应根据退出码决定是否继续，而不是只匹配人类可读的错误文字。

```bash
if account_id=$(aws sts get-caller-identity --query Account --output text); then
  echo "Connected to AWS account: ${account_id}"
else
  echo "Unable to access AWS" >&2
  exit 1
fi
```

## 不把秘密放进命令行

命令行参数可能进入 Shell 历史或被本机进程查看。密码、Token 等敏感内容应通过专用的 Secret 服务、受保护的文件或安全的凭证提供程序传递，不要直接拼在命令中。

在 EC2、ECS、EKS 或 Lambda 上运行脚本时，应优先绑定 IAM Role，让 AWS CLI 自动获取临时凭证，不要把 Access Key 烘焙进镜像或写入环境配置文件。

# 常见错误与排查方法

## Unable to locate credentials

CLI 没有找到可用凭证。检查当前 Profile 和凭证来源：

```bash
aws configure list
aws configure list-profiles
```

如果使用 SSO，确认命令带了正确的 `--profile`，并重新执行 `aws sso login`。

## ExpiredToken

临时凭证已过期。SSO 用户重新登录；使用 STS 或 AssumeRole 的脚本则需要刷新上游凭证，而不是重复使用旧 Token。

## AccessDenied 或 UnauthorizedOperation

身份认证通常已经成功，但 IAM Policy、Permission Boundary、Service Control Policy 或资源策略没有授予相应操作。先运行 `aws sts get-caller-identity` 确认身份，再让管理员根据报错中的 Action 和 Resource 检查最小权限配置。

## Could not connect to the endpoint URL

常见原因包括 Region 写错、网络或代理不可用、DNS 解析失败。先检查：

```bash
aws configure list
aws ec2 describe-regions --region ap-southeast-1
```

## 参数复杂，不确定哪里有问题

先查看命令帮助，再增加 `--debug`：

```bash
aws ec2 describe-instances help
aws ec2 describe-instances --debug
```

Debug 日志可能包含账号、请求地址和其他敏感上下文，对外分享前必须脱敏。

# 一套推荐的日常工作流

最后把前面的内容整理成一个稳定流程：

1. 使用 IAM Identity Center、IAM Role 等临时凭证方案。
2. 为开发、测试和生产环境创建不同的命名 Profile。
3. 登录后先用 `sts get-caller-identity` 确认账号和角色。
4. 明确指定 Region，尤其是在生产脚本中。
5. 查询时先用服务端 Filter 缩小范围，再用 `--query` 整理输出。
6. 对删除、覆盖、停机等操作先使用服务支持的 Dry Run 或预览能力。
7. 自动化脚本检查退出码，并避免依赖面向人类的 `table` 输出。
8. 不在代码、镜像和 Git 仓库中保存长期 Access Key。

掌握这些习惯之后，AWS CLI 就不只是“控制台的命令行版本”，而会成为一套可审查、可复用、适合自动化的云资源操作接口。

# 参考资料

- [安装或更新 AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [配置 IAM Identity Center 认证](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
- [配置与凭证文件](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [过滤 AWS CLI 输出](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-filter.html)
- [设置输出格式](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-output-format.html)
- [分页选项](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-pagination.html)
- [IAM 安全最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
