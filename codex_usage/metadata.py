"""Allowlisted local metadata extraction. Never export raw config or JWTs."""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit, urlunsplit
from .safety import checked_local_path


def mapping(value: object) -> dict:
    return value if isinstance(value,dict) else {}


def text(value: object, limit: int = 1000) -> str | None:
    return value[:limit] if isinstance(value,str) and value else None


def read_json(path: Path) -> dict:
    with checked_local_path(path).open('r', encoding='utf-8-sig') as stream:
        value = json.load(stream)
    return value if isinstance(value, dict) else {}


def source(path: Path, kind: str, description: str) -> dict:
    path = checked_local_path(path)
    return {'path': str(path), 'uri': path.as_uri(), 'kind': kind, 'description': description, 'exists': path.exists()}


def mask(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return ('•' * 8 + value[-4:]) if len(value) > 8 else '•' * 8


def jwt_claims(token: object) -> dict:
    try:
        segment = str(token).split('.')[1]
        value = json.loads(base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4)))
        return value if isinstance(value, dict) else {}
    except (ValueError, IndexError, UnicodeError):
        return {}


def safe_url(value: object) -> str | None:
    if not isinstance(value, str): return None
    try:
        parts = urlsplit(value)
        host = parts.hostname or ''
        if parts.port: host += ':' + str(parts.port)
        # Credentials, query strings and fragments are never retained.
        return urlunsplit((parts.scheme, host, parts.path, '', ''))
    except ValueError:
        return '[无法解析的 URL，已隐藏]'


def scan_metadata(home: Path) -> dict:
    warnings: list[str] = []
    sources: list[dict] = []
    auth_path, config_path = home/'auth.json', home/'config.toml'
    sources += [source(auth_path, 'auth', '当前本地登录信息；JWT 只解码白名单声明，不联网验证，凭据不导出。'), source(config_path, 'config', '用户级配置；不会执行 notify、MCP、插件或认证命令。')]
    auth, config = {}, {}
    for kind, path in [('auth',auth_path),('config',config_path)]:
        try:
            if kind=='auth': auth=read_json(path)
            else: config=tomllib.loads(checked_local_path(path).read_text(encoding='utf-8-sig'))
        except (OSError, ValueError) as exc:
            warnings.append(f'{path.name} 无法读取（{type(exc).__name__}）；相关字段显示未知。')
    tokens = auth.get('tokens') if isinstance(auth.get('tokens'),dict) else {}
    claims = jwt_claims(tokens.get('id_token'))
    access = jwt_claims(tokens.get('access_token'))
    detail = claims.get('https://api.openai.com/auth') or access.get('https://api.openai.com/auth') or {}
    if not isinstance(detail,dict): detail={}
    profile_claims = access.get('https://api.openai.com/profile', {})
    if not isinstance(profile_claims,dict): profile_claims={}
    profile_name = text(config.get('profile'))
    active = dict(config)
    active.update(mapping(mapping(config.get('profiles')).get(profile_name)))
    provider_id = text(active.get('model_provider')) or 'openai'
    provider = mapping(mapping(config.get('model_providers')).get(provider_id))
    auth_mode=text(auth.get('auth_mode')) or ('chatgpt' if tokens else 'api_key' if auth.get('OPENAI_API_KEY') else 'unknown')
    env_key=text(provider.get('env_key'))
    raw_key=text(auth.get('OPENAI_API_KEY'),20000) or text(provider.get('experimental_bearer_token'),20000)
    key_origin='auth.json: OPENAI_API_KEY' if auth.get('OPENAI_API_KEY') else 'config.toml: experimental_bearer_token' if raw_key else None
    if env_key and os.environ.get(str(env_key)):
        raw_key=os.environ[str(env_key)]; key_origin=f'当前进程环境变量 {env_key}'
    elif not raw_key and provider_id=='openai' and os.environ.get('OPENAI_API_KEY'):
        raw_key=os.environ['OPENAI_API_KEY']; key_origin='当前进程环境变量 OPENAI_API_KEY'
    configured_base=safe_url(provider.get('base_url'))
    try: configured_host=urlsplit(configured_base or '').hostname
    except ValueError: configured_host=None
    provider_kind='OpenAI 默认提供商' if provider_id=='openai' and not configured_base else 'OpenAI API 地址（来自配置）' if configured_host=='api.openai.com' else '自定义 API / 代理地址（身份未验证）'
    if provider.get('requires_openai_auth') is True:
        auth_note='提供商配置要求 OpenAI 认证；认证文件中的登录声明见账号区。'
    elif provider_id!='openai':
        auth_note='模型请求配置为自定义提供商；账号区的 ChatGPT 登录缓存不代表该 API 的计费账号。' + (' 找到本机可读取的 API 凭据。' if raw_key else ' 未找到可直接读取的 API 凭据，实际认证状态未知。')
    else:
        auth_note='认证文件声明与当前进程环境变量只表示本地状态；未连接服务商验证。'
    account={
        'auth_mode':auth_mode,
        'login_method': 'OpenAI / ChatGPT 账号登录' if auth_mode=='chatgpt' else 'API Key 登录' if auth_mode in ('api_key','apikey') else str(auth_mode),
        'email':text(claims.get('email')) or text(profile_claims.get('email')), 'name':text(claims.get('name')),
        'account_id':text(tokens.get('account_id')) or text(detail.get('chatgpt_account_id')),
        'user_id':text(detail.get('chatgpt_user_id')) or text(claims.get('sub')),
        'plan_type':text(detail.get('chatgpt_plan_type')), 'last_refresh':text(auth.get('last_refresh')),
        'token_expires_at':datetime.fromtimestamp(claims['exp'], timezone.utc).isoformat() if isinstance(claims.get('exp'),(int,float)) and not isinstance(claims.get('exp'),bool) and 0<claims['exp']<32503680000 else None,
        'provider_id':provider_id, 'provider_name':text(provider.get('name')) or ('OpenAI' if provider_id=='openai' else provider_id),
        'base_url':configured_base,
        'api_key_masked':mask(raw_key), 'api_key_source':key_origin, 'env_key':env_key,
        'source':source(auth_path,'auth','登录来源'),
        'verification':'本地缓存声明，未联网验证；可能已过期。',
        'auth_provider':text(claims.get('auth_provider')),
        'subscription_active_start':text(detail.get('chatgpt_subscription_active_start')),
        'subscription_active_until':text(detail.get('chatgpt_subscription_active_until')),
        'subscription_last_checked':text(detail.get('chatgpt_subscription_last_checked')),
    }
    configuration={
        'codex_home':str(home),'model':text(active.get('model')),'reasoning_effort':text(active.get('model_reasoning_effort')),
        'profile':profile_name,'service_tier':text(active.get('service_tier')),'model_provider':provider_id,
        'provider_name':account['provider_name'],'base_url':account['base_url'], 'wire_api':text(provider.get('wire_api')),
        'requires_openai_auth':provider.get('requires_openai_auth') if isinstance(provider.get('requires_openai_auth'),bool) else None,'credential_store':text(config.get('cli_auth_credentials_store')) or 'file / 默认',
        'api_key_masked':account['api_key_masked'],'api_key_source':key_origin,
        'provider_kind':provider_kind,'authentication_note':auth_note,
        'openai_base_url_env':safe_url(os.environ.get('OPENAI_BASE_URL')),
        'source':source(config_path,'config','配置来源'),
        'note':'这里是用户级默认配置；项目配置、启动参数和单轮覆盖以会话日志为准。凭据库与命令型认证不执行。',
        'base_url_note':'配置未指定 Base URL，使用客户端内置默认地址。' if not provider.get('base_url') else '来自本机配置；服务商身份未联网验证。',
        'configured_providers':[
            {'id':pid,'name':text(item.get('name')) or pid,'base_url':safe_url(item.get('base_url')),'env_key':text(item.get('env_key')),'wire_api':text(item.get('wire_api')),'requires_openai_auth':item.get('requires_openai_auth') if isinstance(item.get('requires_openai_auth'),bool) else None}
            for pid,item in mapping(config.get('model_providers')).items() if isinstance(item,dict)
        ],
    }
    cache_path=home/'models_cache.json'
    models=[]; versions={'cache_client_version':None,'cache_fetched_at':None,'desktop_version':None,'desktop_path':None,'cli_version':None}
    try:
        cache=read_json(cache_path)
        versions.update(cache_client_version=text(cache.get('client_version')),cache_fetched_at=text(cache.get('fetched_at')))
        sources.append(source(cache_path,'models','本地模型目录；上下文窗口不是账户 Token 额度。'))
        for item in cache.get('models',[]) if isinstance(cache.get('models'),list) else []:
            if not isinstance(item,dict): continue
            model={k:text(item.get(k),3000) for k in ('slug','display_name','description','default_reasoning_level','visibility')}
            for k in ('context_window','max_context_window'):
                val=item.get(k)
                model[k]=int(val) if isinstance(val,(int,float)) and not isinstance(val,bool) and math.isfinite(val) and val>=0 else None
            model['supported_in_api']=item.get('supported_in_api') if isinstance(item.get('supported_in_api'),bool) else None
            model['supported_reasoning_levels']=[{'effort':text(level.get('effort')),'description':text(level.get('description'))} if isinstance(level,dict) else text(level) for level in item.get('supported_reasoning_levels',[]) if isinstance(level,dict) or text(level)] if isinstance(item.get('supported_reasoning_levels'),list) else []
            models.append(model)
    except (OSError,ValueError):
        warnings.append('本地模型缓存不可用，无法列出缓存中的模型能力。')
    versions.update(read_versions(sources))
    return {'account':account,'configuration':configuration,'versions':versions,'model_catalog':models,'sources':sources,'warnings':warnings}


def read_versions(sources: list[dict]) -> dict:
    result={}
    if os.name!='nt': return result
    # Read package manifests and PE version resources. Never run the Codex binary.
    import xml.etree.ElementTree as ET
    apps=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'WindowsApps'
    try:
        candidates=list(checked_local_path(apps).glob('OpenAI.Codex*/AppxManifest.xml'))
        manifests=[]
        for path in candidates:
            try:
                tree=ET.fromstring(checked_local_path(path).read_text(encoding='utf-8-sig'))
                identity=next((el for el in tree.iter() if el.tag.split('}')[-1]=='Identity'),None)
                if identity is not None: manifests.append((identity.attrib.get('Version',''),path))
            except (OSError,ValueError,ET.ParseError): continue
        if manifests:
            version,path=max(manifests,key=lambda pair:tuple(int(x) for x in pair[0].split('.') if x.isdigit()))
            result.update(desktop_version=version,desktop_path=str(path.parent),desktop_version_note='本地已安装包的最高版本；未检查更新。')
            sources.append(source(path,'version','Windows 安装包清单版本。'))
    except (OSError,ValueError): pass
    return result


def read_api_key(home: Path) -> tuple[str|None,str|None]:
    """Explicit terminal-only reveal; never included in HTML/JSON."""
    auth=read_json(home/'auth.json') if (home/'auth.json').is_file() else {}
    cfg=tomllib.loads(checked_local_path(home/'config.toml').read_text(encoding='utf-8-sig')) if (home/'config.toml').is_file() else {}
    profile=mapping(mapping(cfg.get('profiles')).get(text(cfg.get('profile'))))
    provider_id=text(profile.get('model_provider')) or text(cfg.get('model_provider')) or 'openai'
    provider=mapping(mapping(cfg.get('model_providers')).get(provider_id))
    env_key=text(provider.get('env_key')) or ('OPENAI_API_KEY' if provider_id=='openai' else None)
    if env_key and os.environ.get(env_key): return os.environ[env_key],f'环境变量 {env_key}'
    if text(auth.get('OPENAI_API_KEY')): return auth['OPENAI_API_KEY'],'auth.json'
    if text(provider.get('experimental_bearer_token')): return provider['experimental_bearer_token'],'config.toml'
    return None,None
