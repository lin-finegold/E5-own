# -*- coding: UTF-8 -*-
"""
E5 开发者模式 - 更自然的 Microsoft 365 API 使用
模拟开发者在日常工作中正常使用 OneDrive、Outlook、Teams 等
"""
import os
import requests as req
import json, time, random

# 环境变量
app_num = os.getenv('APP_NUM')
if app_num == '' or app_num is None:
    app_num = '1'

# 配置
config = {
    'api_rand': 1,
    'rounds': 1,  # 减少测试轮数
    'rounds_delay': [0, 1, 3],  # 减少等待
    'api_delay': [0, 0, 1],     # 减少API间隔
    'app_delay': [0, 0, 1],     # 减少账号间隔
}

# 开发者的日常操作 - 更自然
api_list = [
    # 开发相关
    r'https://graph.microsoft.com/v1.0/me/',                                           # 获取用户资料
    r'https://graph.microsoft.com/v1.0/users',                                        # 查看用户目录
    r'https://graph.microsoft.com/v1.0/me/presence',                                   # 在线状态
    
    # OneDrive - 正常使用
    r'https://graph.microsoft.com/v1.0/me/drive',                                      # 我的云盘
    r'https://graph.microsoft.com/v1.0/me/drive/root',                                 # 根目录
    r'https://graph.microsoft.com/v1.0/me/drive/root/children',                        # 文件列表
    r'https://graph.microsoft.com/v1.0/me/drive/recent',                               # 最近文件
    r'https://graph.microsoft.com/v1.0/me/drive/sharedWithMe',                         # 共享文件
    
    # 邮件 - 正常查看
    r'https://graph.microsoft.com/v1.0/me/messages',                                   # 收件箱
    r'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages',                 # 收件箱邮件
    r'https://graph.microsoft.com/v1.0/me/mailFolders',                                # 邮件文件夹
    
    # 日历 - 正常查看
    r'https://graph.microsoft.com/v1.0/me/calendars',                                  # 日历列表
    r'https://graph.microsoft.com/v1.0/me/events',                                     # 日程事件
    
    # 联系人
    r'https://graph.microsoft.com/v1.0/me/contacts',                                   # 联系人
    r'https://graph.microsoft.com/v1.0/me/people',                                     # 常用联系人
    
    # 任务/待办
    r'https://graph.microsoft.com/v1.0/me/todo/lists',                                 # 任务列表
    
    # OneNote - 开发文档
    r'https://graph.microsoft.com/v1.0/me/onenote/notebooks',                          # 笔记本
    r'https://graph.microsoft.com/v1.0/me/onenote/sections',                           # 分区
    
    # Sites - 团队协作
    r'https://graph.microsoft.com/v1.0/sites/root',                                    # 根站点
    r'https://graph.microsoft.com/v1.0/sites/root/sites',                              # 子站点
    
    # Teams
    r'https://graph.microsoft.com/v1.0/me/joinedTeams',                                # 加入的团队
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
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',
                    data=data, headers=headers)
    jsontxt = json.loads(html.text)
    if 'refresh_token' in jsontxt:
        print(f'✅ 账号 {appnum} 登录成功')
    else:
        print(f'❌ 账号 {appnum} 登录失败: {jsontxt.get("error", "未知错误")}')
    return jsontxt.get('access_token')

def runapi(apilist, a):
    access_token = access_token_list[a-1]
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    for b in apilist:
        url = api_list[b]
        try:
            res = req.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                print(f'  ✅ {url.split("/v1.0/")[-1][:40]}')
            elif res.status_code == 401:
                print(f'  🔄 Token过期，需要刷新')
                break
            else:
                print(f'  ⚠️ {url.split("/v1.0/")[-1][:40]} - {res.status_code}')
        except Exception as e:
            print(f'  ❌ 请求失败: {e}')
        
        if config['api_delay'][0] == 1:
            time.sleep(random.randint(config['api_delay'][1], config['api_delay'][2]))

# 初始化
for a in range(1, int(app_num)+1):
    client_id = os.getenv(f'CLIENT_ID_{a}')
    client_secret = os.getenv(f'CLIENT_SECRET_{a}')
    ms_token = os.getenv(f'MS_TOKEN_{a}')
    if client_id and ms_token:
        access_token_list[a-1] = getmstoken(ms_token, a)

# 选择 API 组合 - 模拟开发者一天的工作
developer_apis = {
    'morning': [0, 1, 2, 3, 4, 11, 12],      # 早上：查看日程、邮件
    'work': [3, 4, 5, 6, 8, 13, 14, 16],     # 工作：文件操作
    'evening': [7, 9, 10, 15, 18, 19],        # 晚上：整理、查看
}

print(f"\n🚀 E5 开发者模式启动")
print(f"📊 共 {app_num} 个账号，每账号 {config['rounds']} 轮\n")

for r in range(1, config['rounds']+1):
    if config['rounds_delay'][0] == 1:
        delay = random.randint(config['rounds_delay'][1], config['rounds_delay'][2])
        print(f"⏳ 等待 {delay} 秒...")
        time.sleep(delay)
    
    for a in range(1, int(app_num)+1):
        if config['app_delay'][0] == 1:
            time.sleep(random.randint(config['app_delay'][1], config['app_delay'][2]))
        
        print(f'\n👤 账号 {a} - 第 {r} 轮')
        
        # 根据时间选择合适的API组合
        hour = time.localtime().tm_hour
        if 6 <= hour < 12:
            apilist = developer_apis['morning']
        elif 12 <= hour < 18:
            apilist = developer_apis['work']
        else:
            apilist = developer_apis['evening']
        
        if config['api_rand'] == 1:
            random.shuffle(apilist)
        
        runapi(apilist, a)

print(f"\n✨ 今日开发工作完成！")