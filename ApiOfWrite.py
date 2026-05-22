# -*- coding: UTF-8 -*-
"""
E5 开发者写入模式 - 更自然的 Microsoft 365 写入操作
模拟开发者在日常工作中正常使用：发邮件、存文件、记笔记等
"""
import os
import requests as req
import json, time, random

# 环境变量
emailaddress = os.getenv('EMAIL')
app_num = os.getenv('APP_NUM')
if app_num == '' or app_num is None:
    app_num = '1'

city = os.getenv('CITY', 'Beijing')

# 配置 - 更自然的间隔
config = {
    'allstart': 1,
    'rounds': 1,
    'rounds_delay': [1, 30, 120],
    'api_delay': [1, 3, 10],
    'app_delay': [1, 60, 180],
}

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

def apiDelay():
    if config['api_delay'][0] == 1:
        time.sleep(random.randint(config['api_delay'][1], config['api_delay'][2]))

def apiReq(method, a, url, data='QAQ'):
    apiDelay()
    access_token = access_token_list[a-1]
    headers = {
        'Authorization': 'bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    try:
        if method == 'post':
            posttext = req.post(url, headers=headers, data=data, timeout=15)
        elif method == 'put':
            posttext = req.put(url, headers=headers, data=data, timeout=15)
        elif method == 'delete':
            posttext = req.delete(url, headers=headers, timeout=15)
        else:
            posttext = req.get(url, headers=headers, timeout=15)
        
        if posttext.status_code < 300:
            return posttext.text
        else:
            print(f'  ⚠️ 状态码: {posttext.status_code}')
            return posttext.text
    except Exception as e:
        print(f'  ❌ 请求失败: {e}')
        return None

# 自然的使用场景
def developer_workflow(a):
    """开发者日常工作流程"""
    print(f"  📝 开始开发者工作流程...")
    
    # 1. 查看云盘（开发者经常看）
    print("  📂 查看云盘...")
    url = r'https://graph.microsoft.com/v1.0/me/drive/root'
    apiReq('get', a, url)
    
    # 2. 查看最近文件
    url = r'https://graph.microsoft.com/v1.0/me/drive/recent'
    apiReq('get', a, url)
    
    # 3. 查看邮件（正常查看，不一定每封都回）
    print("  📧 检查邮件...")
    url = r'https://graph.microsoft.com/v1.0/me/messages?$top=5'
    apiReq('get', a, url)
    
    # 4. 查看日历（看看今天有啥安排）
    print("  📅 查看日历...")
    url = r'https://graph.microsoft.com/v1.0/me/calendar/events?$top=3'
    apiReq('get', a, url)
    
    # 5. 查看任务（工作待办）
    print("  ✅ 查看任务列表...")
    url = r'https://graph.microsoft.com/v1.0/me/todo/lists'
    apiReq('get', a, url)

def send_weather_email(a):
    """发送天气邮件 - 开发者检查天气很常见"""
    if not emailaddress:
        return
    print(f"  📤 发送天气邮件到 {emailaddress}...")
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
    apiReq('post', a, url, json.dumps(mailmessage))

def create_onenote_note(a):
    """创建 OneNote 笔记 - 开发者记录东西很正常"""
    print("  📓 创建工作笔记...")
    note_name = f'DevNotes_{random.randint(1000, 9999)}'
    url = r'https://graph.microsoft.com/v1.0/me/onenote/notebooks'
    data = json.dumps({"displayName": note_name})
    result = apiReq('post', a, url, data)
    
    if result and 'id' in json.loads(result):
        print(f"    ✅ 笔记 {note_name} 创建成功")
        # 不需要删除，自然使用就是要留痕迹

def update_presence(a):
    """更新在线状态 - 开发者经常设置"""
    print("  🟢 更新在线状态...")
    url = r'https://graph.microsoft.com/v1.0/me/presence/setPresence'
    data = json.dumps({
        "availability": random.choice(["Available", "Busy", "DoNotDisturb"]),
        "activity": random.choice(["InACall", "InAMeeting", "Presenting"])
    })
    apiReq('post', a, url, data)

def get_weather():
    """获取天气"""
    try:
        import requests
        resp = requests.get(f'https://wttr.in/{city}?format=4&m', timeout=5)
        if resp.status_code == 200:
            return resp.text.strip()
    except:
        pass
    return f"天气: {city} - 获取失败"

# 初始化
for a in range(1, int(app_num)+1):
    client_id = os.getenv(f'CLIENT_ID_{a}')
    client_secret = os.getenv(f'CLIENT_SECRET_{a}')
    ms_token = os.getenv(f'MS_TOKEN_{a}')
    if client_id and ms_token:
        access_token_list[a-1] = getmstoken(ms_token, a)

print(f"\n🚀 E5 开发者写入模式")
print(f"📊 共 {app_num} 个账号\n")

# 主循环
for r in range(1, config['rounds']+1):
    if config['rounds_delay'][0] == 1:
        delay = random.randint(config['rounds_delay'][1], config['rounds_delay'][2])
        print(f"⏳ 等待 {delay} 秒...")
        time.sleep(delay)
    
    print(f'\n📋 第 {r} 轮\n')
    
    for a in range(1, int(app_num)+1):
        if config['app_delay'][0] == 1:
            time.sleep(random.randint(config['app_delay'][1], config['app_delay'][2]))
        
        print(f'\n👤 账号 {a}:')
        
        # 开发者日常操作 - 随机选择几个
        actions = [
            lambda: developer_workflow(a),
            lambda: send_weather_email(a),
            lambda: create_onenote_note(a),
            lambda: update_presence(a),
        ]
        
        # 随机执行2-3个操作，更像真人
        num_actions = random.randint(2, 3)
        selected = random.sample(actions, num_actions)
        
        for action in selected:
            try:
                action()
            except Exception as e:
                print(f"  ❌ 操作失败: {e}")

print(f"\n✨ 开发者工作完成！")