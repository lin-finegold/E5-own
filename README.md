# OFFICE365 E5 开发者模式

## 说明
* E5 自动续期程序 - **开发者模式**
* 模拟真实开发者的日常使用习惯，更自然，不容易被检测为机器人
* 周六日(UTC时间)不启动，周1-5每6小时自动启动一次

## 开发模式特点

### ApiOfRead.py - 开发者查询模式
- 模拟开发者的日常工作：查看邮件、日历、文档、任务、分析
- 更自然的随机间隔（5-30秒），10%概率出现较长停顿（模拟分心）
- 根据时间段选择不同的 API 组合：
  - 早上(6-12点)：日程、邮件、待办
  - 下午(12-18点)：文件操作、协作、分析
  - 晚上(18-24点)：整理、查看、趋势
- **新增 API**：未读邮件搜索、Planner任务、Insights分析、Teams聊天
- 失败重试、限流自动等待（429响应）、超时处理
- 修复 shuffle 导致全局列表被永久修改的 bug

### ApiOfWrite.py - 开发者写入模式
- 模拟开发者的自然操作（按场景分组）：
  - 场景1：日常查看 + 上传文件到 OneDrive
  - 场景2：查看 + 发天气邮件 + 创建待办任务
  - 场景3：查看 + 创建日历事件 + OneNote笔记
  - 场景4：发邮件 + 上传文件 + 创建待办
- **新增功能**：
  - 上传文件到 OneDrive
  - 创建待办任务（Todo）
  - 创建日历事件（Calendar）
  - 资源自动清理（删除创建的任务、事件、文件）
- 移除 `setPresence` API（需要 Application 权限，委托权限无法调用）
- 更自然的延时分布，10%概率停顿更久

### UpdateToken.py - Token 自动更新
- 修复第1行和第5行的乱码字符
- 使用 `json.dumps` 代替手动拼接 JSON（避免格式错误）
- 增加错误处理和输入验证
- 添加 logging 模块替代 print 输出

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
   - `GH_TOKEN`: 你的 GitHub Token（需要 repo 和 workflow 权限）
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

# Token 更新（需额外依赖）
pip install PyNaCl
python UpdateToken.py
```

## 定时任务

建议使用 GitHub Actions 或 cron 定时运行：
- ApiOfRead: 每6小时运行一次（周一-周五UTC）
- ApiOfWrite: 每天运行一次
- UpdateToken: 每周一、四、六运行
- 周末不运行

## 优化日志

- ✅ 修复 shuffle 导致全局列表被永久修改的 bug
- ✅ 移除 setPresence API（委托权限无法调用）
- ✅ 修复 UpdateToken.py 乱码字符
- ✅ 使用 json.dumps 代替手动拼接 JSON
- ✅ 增加失败重试、限流处理、超时处理
- ✅ 增加新 API（Planner、Insights、Teams、搜索）
- ✅ 增加新写入功能（上传文件、创建任务、创建事件）
- ✅ 资源自动清理避免无限堆积
- ✅ 更自然的延时分布（human_delay 函数）
- ✅ 添加 logging 模块替代 print