# OFFICE365 E5 开发者模式

## 说明
* E5 自动续期程序 - **开发者模式**
* 模拟真实开发者的日常使用习惯，更自然，不容易被检测为机器人
* 周六日(UTC时间)不启动，周1-5每6小时自动启动一次

## 开发模式特点

### ApiOfRead.py - 开发者查询模式
- 模拟开发者的日常工作：查看邮件、日历、文档
- 更长的随机间隔（30秒-3分钟）
- 根据时间段选择不同的 API 组合：
  - 早上(6-12点)：日程、邮件
  - 下午(12-18点)：文件操作
  - 晚上(18-24点)：整理、查看
- 随机延时，模拟人类操作节奏

### ApiOfWrite.py - 开发者写入模式
- 模拟开发者的自然操作：
  - 查看云盘和最近文件
  - 检查邮件
  - 查看日历和任务
  - 偶尔发送邮件（天气提醒）
  - 创建工作笔记
  - 更新在线状态
- 更长的间隔，更像真实使用

## 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `APP_NUM` | 账号数量 | 是 |
| `CLIENT_ID_1` | 账号1的 CLIENT_ID | 是 |
| `CLIENT_SECRET_1` | 账号1的 CLIENT_SECRET | 是 |
| `MS_TOKEN_1` | 账号1的 refresh_token | 是 |
| `CLIENT_ID_2` | 账号2的 CLIENT_ID | 如果APP_NUM>1 |
| `CLIENT_SECRET_2` | 账号2的 CLIENT_SECRET | 如果APP_NUM>1 |
| `MS_TOKEN_2` | 账号2的 refresh_token | 如果APP_NUM>1 |
| `EMAIL` | 接收天气/状态邮件的邮箱 | 可选 |
| `CITY` | 天气城市（如Beijing） | 可选 |

## 配置 GitHub Secrets

1. 在 GitHub 仓库设置中添加 secrets：
   - `GH_TOKEN`: 你的 GitHub Token
   - `GH_REPO`: `用户名/仓库名`
   - `APP_NUM`: 账号数量
   - `CLIENT_ID_1`, `CLIENT_SECRET_1`, `MS_TOKEN_1`
   - 如有多账号，添加 `CLIENT_ID_2` 等

2. 使用 UpdateToken.py 更新 Token 到 secrets

## 运行方式

```bash
# 安装依赖
pip install requests

# 查询模式（保持活跃）
python ApiOfRead.py

# 写入模式（更活跃）
python ApiOfWrite.py
```

## 定时任务

建议使用 GitHub Actions 或 cron 定时运行：
- 每6小时运行一次
- 周末不运行