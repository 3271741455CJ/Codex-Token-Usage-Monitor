"""Remove private originals before HTML embedding or JSON/CSV export.

Aliases are report-local ordinal labels, not hashes or reversible encodings.
The lookup tables exist only in memory; source files remain untouched.
"""
from __future__ import annotations

import re

LOCAL_GUIDE = ('请自行打开本次采集所选的 Codex 数据目录；默认位置为用户主目录中的 .codex。'
               '敏感原文仅在本地源文件中查看，不要复制到聊天、截图或外部网站。')
GUIDES = {
    'auth': '身份与登录凭据请自行查看 auth.json；系统凭据库中的内容请通过官方客户端管理。',
    'config': '私人配置请自行查看 config.toml；环境变量请在系统设置中自行查看。',
    'models': '模型缓存请自行查看 models_cache.json。',
    'session': '会话原文请自行查阅 sessions 或 archived_sessions 中的 JSONL 文件，可按记录时间与行号核对。',
    'session_index': '会话名称请自行查看 session_index.jsonl。',
    'sqlite': '索引原文请自行复制 state_*.sqlite 及其 WAL/SHM 后只读查看副本。',
    'sqlite-sidecar': '数据库附属文件只与本地数据库副本一并查看。',
    'version': '安装路径请在系统应用设置中自行查看。',
}
PRIVATE_KEYS = {
    'email', 'account_email', 'user_id', 'creator_account_id', 'creator_user_id',
    'access_token', 'refresh_token', 'id_token', 'accessToken', 'refreshToken',
    'idToken', 'authorization', 'api_key', 'api_key_masked', 'api_key_source',
    'OPENAI_API_KEY', 'experimental_bearer_token', 'password', 'client_secret',
    'env_key', 'base_url', 'openai_base_url_env', 'configured_providers',
    'provider_id', 'provider_name', 'model_provider', 'profile', 'codex_home',
    'desktop_path', 'rollout_path', 'cwd', 'path', 'uri', 'key', 'description',
    'raw', 'raw_claims', 'content', 'message', 'tool_arguments', 'tool_output',
    'subscription_active_start', 'subscription_active_until',
    'subscription_last_checked', 'last_refresh', 'token_expires_at', 'auth_provider',
}
TOP_LEVEL = {
    'schema_version', 'generated_at', 'local_timezone', 'totals', 'sessions',
    'turns', 'rate_limits', 'sources', 'warnings', 'coverage',
    'database_only_sessions', 'models', 'projects', 'daily', 'official_usage',
    'account', 'configuration', 'versions', 'model_catalog',
}
# New parser fields must be explicitly reviewed before they can reach an export.
PUBLIC_FIELDS = TOP_LEVEL | set('''
id title project project_id project_name name session_id root_session_id
parent_thread_id root_turn_id account_id limit_id limit_name source usage_sources
created_at updated_at started_at ended_at timestamp model reasoning_effort
root_session_id_recorded root_turn_id_recorded thread_source cli_version
attribution attribution_basis turn_count request_count usage_record_count
is_subagent child_session_count child_turn_count inclusive_tokens accounting_method
input_tokens cached_input_tokens cache_write_input_tokens output_tokens
reasoning_output_tokens total_tokens database_tokens_used tokens_used
session_count project_count recorded_response_count turns_without_usage
matched_creator unknown_creator other_creator model_segments status
primary secondary credits used_percent window_minutes resets_at has_credits
unlimited balance spend_control_reached individual_limit plan_type
date tokens cache_client_version cache_fetched_at desktop_version
observed_cli_versions desktop_version_note slug display_name
default_reasoning_level visibility context_window max_context_window
supported_in_api supported_reasoning_levels effort summary fetched_at
usage_status limits_status usage_fetched_at limits_fetched_at
lifetimeTokens peakDailyTokens longestRunningTurnSec currentStreakDays
longestStreakDays label usedPercent windowDurationMins resetsAt hasCredits
files_discovered files_read lines_read bytes_read unreadable_files
lines_appended_during_scan malformed_lines malformed_index_lines
inherited_history_lines_skipped invalid_usage_records duplicate_response_records
conflicting_response_records snapshots_without_cumulative_usage duplicate_snapshots
unchanged_snapshots counter_resets_or_replays baseline_snapshots_with_prior_usage
unallocated_initial_snapshots modern_records_below_legacy_deltas
legacy_snapshots_superseded subagent_turns_without_verified_root_turn
subagent_sessions_without_verified_root_session modern_response_count
legacy_usage_delta_count sessions_with_creator_account sessions_without_creator_account
database_sessions parsed_sessions database_only_tokens_used database_only_unknown_tokens
account_attribution
'''.split())


def protect_report(report: dict) -> dict:
    aliases: dict[str, dict] = {}

    def alias(kind, value):
        if value is None or value == '':
            return None
        group = aliases.setdefault(kind, {})
        key = str(value)
        if key not in group:
            group[key] = f'{kind}-{len(group) + 1}'
        return group[key]

    def source(value):
        value = value if isinstance(value, dict) else {'path': value}
        kind = value.get('kind')
        if kind not in GUIDES:
            kind = 'sqlite' if value.get('table') in ('threads', 'projects') else 'session'
        result = {'kind': kind, 'path': alias('source', value.get('path')) or '本地来源',
                  'private_reference': True, 'description': GUIDES[kind] + LOCAL_GUIDE}
        if isinstance(value.get('line'), int) and not isinstance(value['line'], bool):
            result['line'] = value['line']
        if isinstance(value.get('exists'), bool):
            result['exists'] = value['exists']
        if value.get('table') in ('threads', 'projects', 'project_roots'):
            result['table'] = value['table']
        return result

    def visit(value, context=''):
        if isinstance(value, list):
            return [visit(item, context) for item in value]
        if not isinstance(value, dict):
            return value
        result = {}
        for key, item in value.items():
            if key in PRIVATE_KEYS or key not in PUBLIC_FIELDS:
                continue
            if key == 'source':
                result[key] = source(item)
            elif key in ('sources', 'usage_sources'):
                result[key] = [source(s) for s in item] if isinstance(item, list) else []
            elif key == 'account_id':
                # Retain separation between quota pools for different creators.
                result[key] = alias('account', item)
            elif key in ('session_id', 'root_session_id', 'parent_thread_id'):
                result[key] = alias('session', item)
            elif key == 'root_turn_id':
                result[key] = alias('turn', (value.get('root_session_id') or value.get('session_id'), item)) if item else None
            elif key == 'id' and context == 'turns':
                result[key] = alias('turn', (value.get('session_id'), item))
            elif key == 'id' and context in ('sessions', 'database_only_sessions'):
                result[key] = alias('session', item)
            elif key in ('project', 'project_id') or key == 'id' and context == 'projects':
                result[key] = alias('project', item)
            elif key == 'project_name' or key == 'name' and context == 'projects':
                result[key] = alias('project', value.get('project_id') or (value.get('id') if context == 'projects' else None) or value.get('project') or item)
            elif key == 'title':
                result[key] = alias('session', value.get('session_id') or value.get('id')) or '本地记录'
            elif key in ('name', 'id'):
                continue
            elif key in ('limit_id', 'limit_name'):
                result[key] = 'codex' if item == 'codex' else alias('limit', item)
            elif key == 'thread_source':
                result[key] = item if item in ('cli', 'vscode', 'exec', 'appServer', 'subagent', 'unknown') else 'unknown'
            else:
                result[key] = visit(item, key)
        return result

    safe = visit({k: v for k, v in report.items() if k in TOP_LEVEL})
    safe['account'] = {'privacy_note': GUIDES['auth'] + LOCAL_GUIDE}
    config = report.get('configuration') or {}
    safe['configuration'] = {k: config[k] for k in ('model', 'reasoning_effort', 'service_tier') if k in config}
    safe['configuration']['privacy_note'] = GUIDES['config'] + LOCAL_GUIDE
    # Warning text is generated by the collector, but some errors embed paths.
    safe['warnings'] = [
        '部分诊断细节已隐藏，请在本机检查来源文件。' if re.search(r'[A-Za-z]:[\\/]|\\|(?:https?|file)://|(?<!\w)/\S+|@', message) else message
        for message in report.get('warnings', []) if isinstance(message, str)
    ]
    safe['privacy'] = {'protected': True, 'note': LOCAL_GUIDE}
    from .exports import FILES
    safe['export_formats'] = [name for name in report.get('export_formats', []) if name in FILES]
    return safe
