# -*- coding: UTF-8 -*-
"""
E5 开发者写入模式 - 更自然的 Microsoft 365 写入操作
模拟开发者在日常工作中正常使用：发邮件、存文件、记笔记等
"""
import os
import requests as req
import json
import time
import random
import logging

# 环境变量
emailaddress = os.getenv('EMAIL')
app_num = os.getenv('APP_NUM')
if app_num == '' or app_num is None:
    app_num = '1'

city = os.getenv('CITY', 'Beijing')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('E5Write')

# 配置 - 更自然的间隔
config = {
    'allstart': 1,
    'rounds': 1,
    'rounds_delay': [1, 60, 300],   # 轮次间1-5分钟
    'api_delay': [1, 5, 20],        # API间5-20秒
    'app_delay': [1, 120, 360],     # 账号间2-6分钟
    'max_retries': 2,
    'retry_delay': [5, 15],
    'cleanup_created': True,        # 清理创建的资源
}

# 用于跟踪创建的资源（后续清理）
created_resources = []

access_token_list = ['placeholder'] * int(app_num)


def getmstoken(ms_token, appnum):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': ms_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:53682/'
    }
    try:
        html = req.post(
            'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            data=data, headers=headers, timeout=30
        )
        jsontxt = json.loads(html.text)
        if 'refresh_token' in jsontxt:
            logger.info(f'✅ 账号 {appnum} 登录成功')
        else:
            error_desc = jsontxt.get('error_description', jsontxt.get('error', '未知错误'))
            logger.error(f'❌ 账号 {appnum} 登录失败: {error_desc}')
        return jsontxt.get('access_token'), jsontxt.get('refresh_token')
    except Exception as e:
        logger.error(f'❌ 账号 {appnum} 登录请求失败: {e}')
        return None, None


def human_delay(min_sec, max_sec):
    """更自然的延时：偶尔有较长停顿"""
    if random.random() < 0.1:
        return random.randint(max_sec, int(max_sec * 1.5))
    return random.randint(min_sec, max_sec)


def apiDelay():
    if config['api_delay'][0] == 1:
        time.sleep(human_delay(config['api_delay'][1], config['api_delay'][2]))


def apiReq(method, a, url, data='QAQ'):
    """统一的 API 请求方法，带重试和限流处理"""
    apiDelay()
    access_token = access_token_list[a - 1]
    if not access_token or access_token == 'placeholder':
        logger.warning(f'  ⚠️ 账号 {a} 无有效 token，跳过')
        return None

    headers = {
        'Authorization': 'bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    for attempt in range(config['max_retries'] + 1):
        try:
            if method == 'post':
                posttext = req.post(url, headers=headers, data=data, timeout=15)
            elif method == 'put':
                posttext = req.put(url, headers=headers, data=data, timeout=15)
            elif method == 'patch':
                posttext = req.patch(url, headers=headers, data=data, timeout=15)
            elif method == 'delete':
                posttext = req.delete(url, headers=headers, timeout=15)
            else:
                posttext = req.get(url, headers=headers, timeout=15)

            if posttext.status_code < 300:
                return posttext.text
            elif posttext.status_code == 401:
                logger.warning(f'  🔄 Token过期，需要刷新')
                return None
            elif posttext.status_code == 429:
                retry_after = int(posttext.headers.get('Retry-After', 60))
                logger.warning(f'  ⏳ 被限流，等待 {retry_after}s...')
                time.sleep(retry_after)
                continue
            elif posttext.status_code >= 500:
                if attempt < config['max_retries']:
                    delay = random.randint(*config['retry_delay'])
                    logger.warning(f'  ⚠️ 服务端错误 {posttext.status_code}，{delay}s 后重试')
                    time.sleep(delay)
                    continue
                else:
                    logger.warning(f'  ❌ 请求失败 {posttext.status_code}（重试耗尽）')
                    return posttext.text
            else:
                logger.warning(f'  ⚠️ 状态码: {posttext.status_code}')
                return posttext.text
        except req.exceptions.Timeout:
            if attempt < config['max_retries']:
                delay = random.randint(*config['retry_delay'])
                logger.warning(f'  ⏱️ 请求超时，{delay}s 后重试')
                time.sleep(delay)
                continue
            logger.error(f'  ❌ 请求超时（重试耗尽）')
            return None
        except Exception as e:
            logger.error(f'  ❌ 请求失败: {e}')
            return None
    return None


# ── 自然的使用场景 ──────────────────────────────────────

def developer_workflow(a):
    """开发者日常工作流程 — 查看类"""
    logger.info("  📝 开始开发者工作流程...")

    # 1. 查看云盘
    logger.info("  📂 查看云盘...")
    apiReq('get', a, r'https://graph.microsoft.com/v1.0/me/drive/root')

    # 2. 查看最近文件
    apiReq('get', a, r'https://graph.microsoft.com/v1.0/me/drive/recent')

    # 3. 查看邮件
    logger.info("  📧 检查邮件...")
    apiReq('get', a, r'https://graph.microsoft.com/v1.0/me/messages?$top=5')

    # 4. 查看日历
    logger.info("  📅 查看日历...")
    apiReq('get', a, r'https://graph.microsoft.com/v1.0/me/calendar/events?$top=3')

    # 5. 查看任务
    logger.info("  ✅ 查看任务列表...")
    apiReq('get', a, r'https://graph.microsoft.com/v1.0/me/todo/lists')


def send_weather_email(a):
    """发送天气邮件 — 开发者查看天气很常见"""
    if not emailaddress:
        return
    logger.info(f"  📤 发送天气邮件到 {emailaddress}...")
    url = r'https://graph.microsoft.com/v1.0/me/sendMail'

    weather_data = get_weather()
    mailmessage = {
        'message': {
            'subject': f'天气提醒 - {time.strftime("%Y-%m-%d")}',
            'body': {'contentType': 'Text', 'content': weather_data},
            'toRecipients': [{'emailAddress': {'address': emailaddress}}],
        },
        'saveToSentItems': 'true'
    }
    result = apiReq('post', a, url, json.dumps(mailmessage))
    if result is not None:
        logger.info("  ✅ 天气邮件发送成功")


def create_and_cleanup_onenote(a):
    """创建 OneNote 笔记并清理 — 避免无限堆积"""
    logger.info("  📓 创建工作笔记...")
    note_name = f'DevNotes_{random.randint(1000, 9999)}'
    url = r'https://graph.microsoft.com/v1.0/me/onenote/notebooks'
    data = json.dumps({"displayName": note_name})
    result = apiReq('post', a, url, data)

    if result:
        try:
            nb_info = json.loads(result)
            if 'id' in nb_info:
                logger.info(f"    ✅ 笔记 {note_name} 创建成功")
                created_resources.append(('onenote', nb_info['id'], a))
        except (json.JSONDecodeError, TypeError):
            pass


def upload_small_file(a):
    """上传小型文本文件到 OneDrive — 开发者常做的事"""
    logger.info("  📤 上传文件到 OneDrive...")
    filename = f'dev_note_{random.randint(1000, 9999)}.txt'
    content = f"Dev log - {time.strftime('%Y-%m-%d %H:%M')}\nAuto generated by E5 developer mode."
    url = (f'https://graph.microsoft.com/v1.0/me/drive/root:/{filename}'
           f':/content')
    result = apiReq('put', a, url, content)
    if result:
        try:
            file_info = json.loads(result)
            if 'id' in file_info:
                logger.info(f"    ✅ 文件 {filename} 上传成功")
                created_resources.append(('drive', file_info['id'], a))
        except (json.JSONDecodeError, TypeError):
            pass


def create_todo_task(a):
    """创建待办任务 — 开发者规划工作"""
    logger.info("  📋 创建待办事项...")
    # 先获取任务列表
    result = apiReq('get', a, r'https://graph.microsoft.com/v1.0/me/todo/lists')
    if not result:
        return

    try:
        lists = json.loads(result)
        task_list_id = None
        for lst in lists.get('value', []):
            if lst.get('isDefaultList'):
                task_list_id = lst.get('id')
                break
        if not task_list_id and lists.get('value'):
            task_list_id = lists['value'][0].get('id')

        if task_list_id:
            tasks = [
                "Review PR #{}".format(random.randint(100, 999)),
                "Update dependencies",
                "Write unit tests",
                "Fix API timeout issue",
                "Refactor auth module",
            ]
            task_data = json.dumps({
                "title": random.choice(tasks),
                "importance": random.choice(["low", "normal", "high"]),
            })
            url = (f'https://graph.microsoft.com/v1.0/me/todo/lists/'
                   f'{task_list_id}/tasks')
            result = apiReq('post', a, url, task_data)
            if result:
                try:
                    task_info = json.loads(result)
                    if 'id' in task_info:
                        logger.info("    ✅ 待办任务创建成功")
                        created_resources.append(('todo', (task_list_id, task_info['id']), a))
                except (json.JSONDecodeError, TypeError):
                    pass
    except (json.JSONDecodeError, TypeError):
        pass


def create_calendar_event(a):
    """创建日历事件 — 开发者安排会议"""
    logger.info("  📅 创建日历事件...")
    tomorrow = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400))
    start_hour = random.randint(9, 17)
    subject = random.choice([
        "Team standup",
        "Code review meeting",
        "Sprint planning",
        "Architecture discussion",
        "1:1 with manager",
    ])
    event_data = json.dumps({
        "subject": subject,
        "start": {
            "dateTime": f"{tomorrow}T{start_hour:02d}:00:00",
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": f"{tomorrow}T{start_hour + 1:02d}:00:00",
            "timeZone": "UTC"
        },
        "body": {
            "contentType": "Text",
            "content": "Auto-created by E5 developer mode"
        }
    })
    url = r'https://graph.microsoft.com/v1.0/me/events'
    result = apiReq('post', a, url, event_data)
    if result:
        try:
            event_info = json.loads(result)
            if 'id' in event_info:
                logger.info(f"    ✅ 日历事件「{subject}」创建成功")
                created_resources.append(('event', event_info['id'], a))
        except (json.JSONDecodeError, TypeError):
            pass


def get_weather():
    """获取天气"""
    try:
        resp = req.get(f'https://wttr.in/{city}?format=4&m', timeout=5)
        if resp.status_code == 200:
            return resp.text.strip()
    except req.exceptions.RequestException:
        pass
    return f"天气: {city} - 获取失败"


def cleanup_resources():
    """清理创建的资源，避免无限堆积"""
    if not config['cleanup_created']:
        return

    if not created_resources:
        return

    logger.info("\n🧹 清理创建的资源...")
    for res_type, res_id, a in created_resources:
        try:
            if res_type == 'todo':
                list_id, task_id = res_id
                url = (f'https://graph.microsoft.com/v1.0/me/todo/lists/'
                       f'{list_id}/tasks/{task_id}')
                apiReq('delete', a, url)
            elif res_type == 'event':
                url = f'https://graph.microsoft.com/v1.0/me/events/{res_id}'
                apiReq('delete', a, url)
            elif res_type == 'drive':
                url = f'https://graph.microsoft.com/v1.0/me/drive/items/{res_id}'
                apiReq('delete', a, url)
            # OneNote 笔记本不能通过 API 删除，跳过
        except Exception as e:
            logger.warning(f"  ⚠️ 清理失败: {e}")

    logger.info("  ✅ 资源清理完成")


# ── 初始化 ──────────────────────────────────────────────

for a in range(1, int(app_num) + 1):
    client_id = os.getenv(f'CLIENT_ID_{a}')
    client_secret = os.getenv(f'CLIENT_SECRET_{a}')
    ms_token = os.getenv(f'MS_TOKEN_{a}')
    if client_id and ms_token:
        access_token, _ = getmstoken(ms_token, a)
        access_token_list[a - 1] = access_token or 'placeholder'
    else:
        logger.warning(f'⚠️ 账号 {a} 缺少 CLIENT_ID 或 MS_TOKEN，跳过')

logger.info(f"\n🚀 E5 开发者写入模式")
logger.info(f"📊 共 {app_num} 个账号\n")

# ── 主循环 ──────────────────────────────────────────────

for r in range(1, config['rounds'] + 1):
    if config['rounds_delay'][0] == 1:
        delay = human_delay(config['rounds_delay'][1], config['rounds_delay'][2])
        logger.info(f"⏳ 等待 {delay} 秒...")
        time.sleep(delay)

    logger.info(f'\n📋 第 {r} 轮\n')

    for a in range(1, int(app_num) + 1):
        if config['app_delay'][0] == 1:
            time.sleep(human_delay(config['app_delay'][1], config['app_delay'][2]))

        logger.info(f'\n👤 账号 {a}:')

        # 开发者日常操作 — 按场景分组
        scenarios = [
            # 场景1: 日常查看 + 上传文件
            [developer_workflow, upload_small_file],
            # 场景2: 查看 + 发邮件 + 创建待办
            [developer_workflow, send_weather_email, create_todo_task],
            # 场景3: 查看 + 创建日历事件 + OneNote笔记
            [developer_workflow, create_calendar_event, create_and_cleanup_onenote],
            # 场景4: 全套 — 写入模式
            [send_weather_email, upload_small_file, create_todo_task],
        ]

        # 随机选择一个场景
        scenario = random.choice(scenarios)

        for action in scenario:
            try:
                action(a)
            except Exception as e:
                logger.error(f"  ❌ 操作失败: {e}")

# 清理创建的资源
cleanup_resources()

logger.info(f"\n✨ 开发者工作完成！")