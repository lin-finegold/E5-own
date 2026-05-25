# -*- coding: UTF-8 -*-
"""
E5 开发者模式 - Token 自动更新
刷新 Microsoft 365 refresh_token 并上传到 GitHub Secrets
"""
import requests as req
import json
import os
import logging
from base64 import b64encode
from nacl import encoding, public

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('E5Token')

# 环境变量
app_num = os.getenv('APP_NUM')
if app_num == '' or app_num is None:
    app_num = '1'

gh_token = os.getenv('GH_TOKEN')
gh_repo = os.getenv('GH_REPO')

if not gh_token or not gh_repo:
    logger.error('❌ 缺少 GH_TOKEN 或 GH_REPO 环境变量，无法继续')
    exit(1)

# 认证头部
Auth = f'token {gh_token}'
# 获取公钥的 URL
geturl = f'https://api.github.com/repos/{gh_repo}/actions/secrets/public-key'

# 全局变量
key_id = ''


def getpublickey(auth, url):
    """获取仓库公钥用于加密 Secret"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': auth
    }
    try:
        html = req.get(url, headers=headers, timeout=15)
        if html.status_code != 200:
            logger.error(f'❌ 获取公钥失败 (HTTP {html.status_code}): {html.text}')
            return None
        jsontxt = json.loads(html.text)
        if 'key' not in jsontxt:
            logger.error('❌ 公钥获取失败，请检查 GH_TOKEN 权限与 GH_REPO 设置')
            return None
        logger.info('✅ 公钥获取成功')
        global key_id
        key_id = jsontxt['key_id']
        return jsontxt['key']
    except Exception as e:
        logger.error(f'❌ 获取公钥请求失败: {e}')
        return None


def getmstoken(ms_token, appnum):
    """刷新 Microsoft refresh_token"""
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
            logger.info(f'✅ 账号/应用 {appnum} 的微软密钥获取成功')
            return jsontxt['refresh_token']
        else:
            error_desc = jsontxt.get('error_description', jsontxt.get('error', '未知错误'))
            logger.error(f'❌ 账号/应用 {appnum} 的微软密钥获取失败: {error_desc}')
            logger.error('   请检查 CLIENT_ID, CLIENT_SECRET, MS_TOKEN 格式与内容是否正确')
            return None
    except Exception as e:
        logger.error(f'❌ 账号/应用 {appnum} 的微软密钥请求失败: {e}')
        return None


def createsecret(public_key, secret_value):
    """使用公钥加密 Secret 值"""
    public_key_obj = public.PublicKey(
        public_key.encode("utf-8"), encoding.Base64Encoder()
    )
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def setsecret(encrypted_value, kid, puturl, appnum):
    """上传加密后的 Secret 到 GitHub"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': Auth
    }
    # 使用 json.dumps 代替手动拼接，避免格式错误
    data = json.dumps({
        'encrypted_value': encrypted_value,
        'key_id': kid
    })
    try:
        putstatus = req.put(puturl, headers=headers, data=data, timeout=15)
        if putstatus.status_code >= 300:
            logger.error(f'❌ 账号/应用 {appnum} 的微软密钥上传失败 '
                         f'(HTTP {putstatus.status_code})')
            logger.error('   请检查 GH_TOKEN 权限是否包含 repo 和 workflow')
        else:
            logger.info(f'✅ 账号/应用 {appnum} 的微软密钥上传成功')
        return putstatus
    except Exception as e:
        logger.error(f'❌ 账号/应用 {appnum} 的微软密钥上传请求失败: {e}')
        return None


# ── 主流程 ──────────────────────────────────────────────

public_key = getpublickey(Auth, geturl)
if not public_key:
    logger.error('❌ 无法获取公钥，终止')
    exit(1)

for a in range(1, int(app_num) + 1):
    client_id = os.getenv(f'CLIENT_ID_{a}')
    client_secret = os.getenv(f'CLIENT_SECRET_{a}')
    ms_token = os.getenv(f'MS_TOKEN_{a}')

    if not (client_id and client_secret and ms_token):
        logger.warning(f'⚠️ 账号/应用 {a} 缺少必要环境变量，跳过')
        continue

    if a == 1:
        puturl = f'https://api.github.com/repos/{gh_repo}/actions/secrets/MS_TOKEN'
    else:
        puturl = f'https://api.github.com/repos/{gh_repo}/actions/secrets/MS_TOKEN_{a}'

    refresh_token = getmstoken(ms_token, a)
    if refresh_token:
        encrypted_value = createsecret(public_key, refresh_token)
        setsecret(encrypted_value, key_id, puturl, a)
    else:
        logger.warning(f'⚠️ 账号/应用 {a} token 刷新失败，跳过上传')

logger.info('\n✨ Token 更新完成！')
