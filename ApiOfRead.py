# -*- coding: UTF-8 -*-
"""
E5 开发者模式 - 更自然的 Microsoft 365 API 使用
模拟开发者在日常工作中正常使用 OneDrive、Outlook、Teams 等
"""
import os
import requests as req
import json
import time
import random
import logging

# 环境变量
app_num = os.getenv('APP_NUM')
if app_num == '' or app_num is None:
    app_num = '1'

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('E5Read')

# 配置 - 更自然的节奏
config = {
    'api_rand': 1,
    'rounds': 1,
    'rounds_delay': [1, 60, 300],   # 轮次间等待1-5分钟
    'api_delay': [1, 5, 30],        # API间等待5-30秒，模拟阅读/思考
    'app_delay': [1, 120, 360],     # 账号间等待2-6分钟
    'max_retries': 2,               # 失败重试次数
    'retry_delay': [5, 15],         # 重试等待5-15秒
}


def human_delay(min_sec, max_sec):
    """更自然的延时：混合均匀分布和偶尔的长停顿"""
    if random.random() < 0.1:
        # 10% 概率停顿较久（模拟分心/处理其他事）
        return random.randint(max_sec, max_sec * 2)
    return random.randint(min_sec, max_sec)


# 开发者的日常操作 - 更全面的 API 覆盖
api_list = [
    # 用户信息
    r'https://graph.microsoft.com/v1.0/me/',                                           # 获取用户资料
    r'https://graph.microsoft.com/v1.0/me?$select=displayName,mail,jobTitle',          # 简要资料
    r'https://graph.microsoft.com/v1.0/users',                                         # 查看用户目录

    # OneDrive - 文件浏览（高频使用）
    r'https://graph.microsoft.com/v1.0/me/drive',                                      # 我的云盘
    r'https://graph.microsoft.com/v1.0/me/drive/root',                                 # 根目录
    r'https://graph.microsoft.com/v1.0/me/drive/root/children',                        # 文件列表
    r'https://graph.microsoft.com/v1.0/me/drive/recent',                               # 最近文件
    r'https://graph.microsoft.com/v1.0/me/drive/sharedWithMe',                         # 共享文件
    r'https://graph.microsoft.com/v1.0/me/drive/root/search(q=\'project\')',           # 搜索文件

    # 邮件 - Outlook 日常查看
    r'https://graph.microsoft.com/v1.0/me/messages?$top=10&$orderby=receivedDateTime desc',  # 最新邮件
    r'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top=5',         # 收件箱
    r'https://graph.microsoft.com/v1.0/me/mailFolders',                                # 邮件文件夹
    r'https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false',           # 未读邮件
    r'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messageRules',            # 收件箱规则

    # 日历 - 日常查看安排
    r'https://graph.microsoft.com/v1.0/me/calendars',                                  # 日历列表
    r'https://graph.microsoft.com/v1.0/me/events?$top=10',                            # 近期日程
    r'https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={today}&endDateTime={next7d}',  # 日历视图

    # 联系人
    r'https://graph.microsoft.com/v1.0/me/contacts?$top=10',                           # 联系人
    r'https://graph.microsoft.com/v1.0/me/people',                                     # 常用联系人

    # 任务/待办
    r'https://graph.microsoft.com/v1.0/me/todo/lists',                                 # 任务列表
    r'https://graph.microsoft.com/v1.0/me/todo/lists/tasks?$top=10',                   # 任务项

    # OneNote - 开发文档
    r'https://graph.microsoft.com/v1.0/me/onenote/notebooks',                          # 笔记本
    r'https://graph.microsoft.com/v1.0/me/onenote/sections',                           # 分区

    # Teams - 协作沟通
    r'https://graph.microsoft.com/v1.0/me/joinedTeams',                                # 加入的团队
    r'https://graph.microsoft.com/v1.0/me/chats?$top=10',                              # 聊天列表

    # SharePoint - 团队站点
    r'https://graph.microsoft.com/v1.0/sites/root',                                    # 根站点
    r'https://graph.microsoft.com/v1.0/sites/root/sites',                              # 子站点

    # Planner - 项目管理
    r'https://graph.microsoft.com/v1.0/me/planner/tasks',                              # 我的任务

    # 分析/使用情况
    r'https://graph.microsoft.com/v1.0/me/insights/used',                              # 最近使用
    r'https://graph.microsoft.com/v1.0/me/insights/shared',                            # 与我共享
    r'https://graph.microsoft.com/v1.0/me/insights/trending',                          # 热门内容
]

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
        return jsontxt.get('access_token')
    except Exception as e:
        logger.error(f'❌ 账号 {appnum} 登录请求失败: {e}')
        return None


def runapi(apilist, a):
    access_token = access_token_list[a - 1]
    if not access_token or access_token == 'placeholder':
        logger.warning(f'  ⚠️ 账号 {a} 无有效 token，跳过')
        return

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    # 修复日期占位符
    today = time.strftime('%Y-%m-%dT00:00:00')
    next7d = time.strftime('%Y-%m-%dT23:59:59',
                           time.localtime(time.time() + 7 * 86400))

    success_count = 0
    fail_count = 0

    for b in apilist:
        url = api_list[b]
        # 替换日期占位符
        url = url.replace('{today}', today).replace('{next7d}', next7d)

        for attempt in range(config['max_retries'] + 1):
            try:
                res = req.get(url, headers=headers, timeout=15)
                if res.status_code == 200:
                    short_url = url.split("/v1.0/")[-1][:50]
                    logger.info(f'  ✅ {short_url}')
                    success_count += 1
                    break
                elif res.status_code == 401:
                    logger.warning(f'  🔄 Token过期，需要刷新')
                    return  # 直接退出，token已失效
                elif res.status_code == 429:
                    # 限流：等待 Retry-After 秒
                    retry_after = int(res.headers.get('Retry-After', 60))
                    logger.warning(f'  ⏳ 被限流，等待 {retry_after}s...')
                    time.sleep(retry_after)
                    continue
                elif res.status_code >= 500:
                    if attempt < config['max_retries']:
                        delay = random.randint(*config['retry_delay'])
                        logger.warning(f'  ⚠️ 服务端错误 {res.status_code}，{delay}s 后重试')
                        time.sleep(delay)
                        continue
                    else:
                        logger.warning(f'  ❌ {url.split("/v1.0/")[-1][:40]} - {res.status_code} (重试耗尽)')
                        fail_count += 1
                else:
                    short_url = url.split("/v1.0/")[-1][:40]
                    logger.warning(f'  ⚠️ {short_url} - {res.status_code}')
                    fail_count += 1
                    break
            except req.exceptions.Timeout:
                if attempt < config['max_retries']:
                    delay = random.randint(*config['retry_delay'])
                    logger.warning(f'  ⏱️ 请求超时，{delay}s 后重试')
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f'  ❌ 请求超时（重试耗尽）: {url.split("/v1.0/")[-1][:40]}')
                    fail_count += 1
            except Exception as e:
                logger.error(f'  ❌ 请求失败: {e}')
                fail_count += 1
                break

        if config['api_delay'][0] == 1:
            time.sleep(human_delay(config['api_delay'][1], config['api_delay'][2]))

    logger.info(f'  📊 账号 {a} 本轮: ✅{success_count} ⚠️{fail_count}')


# 初始化
for a in range(1, int(app_num) + 1):
    client_id = os.getenv(f'CLIENT_ID_{a}')
    client_secret = os.getenv(f'CLIENT_SECRET_{a}')
    ms_token = os.getenv(f'MS_TOKEN_{a}')
    if client_id and ms_token:
        access_token_list[a - 1] = getmstoken(ms_token, a) or 'placeholder'
    else:
        logger.warning(f'⚠️ 账号 {a} 缺少 CLIENT_ID 或 MS_TOKEN，跳过')

# 选择 API 组合 - 模拟开发者一天的工作
developer_apis = {
    'morning': [0, 1, 2, 3, 4, 11, 12, 16, 17, 23],    # 早上：查看日程、邮件、待办
    'work': [3, 4, 5, 6, 8, 9, 13, 14, 22, 26, 27],    # 工作：文件操作、协作、分析
    'evening': [7, 10, 15, 18, 19, 24, 25, 28],          # 晚上：整理、查看、趋势
}

logger.info(f"🚀 E5 开发者模式启动")
logger.info(f"📊 共 {app_num} 个账号，每账号 {config['rounds']} 轮\n")

for r in range(1, config['rounds'] + 1):
    if config['rounds_delay'][0] == 1:
        delay = human_delay(config['rounds_delay'][1], config['rounds_delay'][2])
        logger.info(f"⏳ 等待 {delay} 秒...")
        time.sleep(delay)

    for a in range(1, int(app_num) + 1):
        if config['app_delay'][0] == 1:
            time.sleep(human_delay(config['app_delay'][1], config['app_delay'][2]))

        logger.info(f'👤 账号 {a} - 第 {r} 轮')

        # 根据时间选择合适的 API 组合（复制列表避免修改原数据）
        hour = time.localtime().tm_hour
        if 6 <= hour < 12:
            apilist = list(developer_apis['morning'])
        elif 12 <= hour < 18:
            apilist = list(developer_apis['work'])
        else:
            apilist = list(developer_apis['evening'])

        if config['api_rand'] == 1:
            random.shuffle(apilist)

        runapi(apilist, a)

logger.info(f"✨ 今日开发工作完成！")
