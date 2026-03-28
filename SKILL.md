---
name: tencent-git
description: 腾讯工蜂(Tencent Git) API 操作工具。用于创建议题(Issue)、回复议题、关闭议题、列出项目等操作。使用场景：(1) 需要在工蜂项目中创建议题跟踪 Bug 或需求 (2) 回复议题添加评论 (3) 关闭已解决的议题 (4) 列出用户可访问的项目。支持通过项目路径(group/repo)或数字ID操作。注意：工蜂 API 使用全局 Issue ID，脚本会自动处理 IID 到全局 ID 的转换。
---

# 腾讯工蜂 Git 操作工具

用于与腾讯工蜂 Git 平台进行交互，管理议题(Issue)和项目。

## 前置要求

- 有效的工蜂 Access Token
- Token 需要有 `api` 权限
- 对目标项目有相应操作权限

## 配置

Token 可以从以下方式获取：
1. 直接提供
2. 环境变量：`TENCENT_GIT_TOKEN`

## 核心操作

### 1. 列出项目

```bash
python3 scripts/tencent_git.py --token TOKEN list-projects
```

### 2. 创建议题

```bash
python3 scripts/tencent_git.py --token TOKEN create-issue \
  --project "group/repo" \
  --title "议题标题" \
  --labels "bug" \
  --description "详细描述"
```

### 3. 回复议题

```bash
python3 scripts/tencent_git.py --token TOKEN add-note \
  --project "group/repo" \
  --iid 1 \
  --body "评论内容"
```

### 4. 关闭议题

```bash
python3 scripts/tencent_git.py --token TOKEN close-issue \
  --project "group/repo" \
  --iid 1
```

### 5. 列出议题

```bash
python3 scripts/tencent_git.py --token TOKEN list-issues \
  --project "group/repo" \
  --state opened
```

## Issue ID 说明

工蜂 API 使用**全局 Issue ID**（跨项目唯一）而非项目内 IID。脚本会自动处理 IID 到全局 ID 的转换。

## API 端点

- 基础 URL: `https://git.code.tencent.com/api/v3`
- 认证头: `PRIVATE-TOKEN: <token>`

## 返回值

```json
{
  "success": true/false,
  "data": { ... },
  "error": "错误信息"
}
```

## 错误码

- 401: Token 无效
- 403: 权限不足
- 404: 资源不存在
- 409: 资源冲突
