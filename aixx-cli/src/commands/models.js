/**
 * AIXX CLI - models 命令
 *
 * 列出AIXX支持的所有模型，按"国产/海外"分组展示。
 *
 * 数据来源：GET /v1/models
 * 后端返回的模型列表是动态的，但分组规则是固定的（按模型名前缀分类）。
 */

import { existsSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { DEFAULT_BASE_URL } from '../../bin/aixx.js';

// 所有对外请求统一 15 秒超时
const FETCH_TIMEOUT = 15000;
// 网络/超时异常统一成友好提示
function friendlyNetErr(err) {
  return err?.name === 'TimeoutError' || err?.name === 'AbortError'
    ? '连接超时，请检查网络'
    : err?.message || String(err);
}

/**
 * 从环境变量或本地账号文件读取 apiKey。
 */
function loadApiKey() {
  if (process.env.AIXX_API_KEY) return process.env.AIXX_API_KEY;
  const accountFile = join(homedir(), '.aixx', 'account.json');
  if (existsSync(accountFile)) {
    try {
      const acc = JSON.parse(readFileSync(accountFile, 'utf-8'));
      if (acc.apiKey) return acc.apiKey;
    } catch (e) {}
  }
  return null;
}

// 给每个模型加一句人话说明，让用户知道怎么选
const MODEL_DESC = {
  'deepseek-chat': '最便宜，¥0.001/千token，日常首选',
  'deepseek-reasoner': '推理增强（带思考过程）',
  'glm-4-flash': '智谱免费档，速度快',
  'glm-4-plus': '中文写作强',
  'glm-4': '智谱通用',
  'moonshot-v1-8k': 'Kimi，短上下文',
  'moonshot-v1-32k': 'Kimi，中等上下文',
  'moonshot-v1-128k': 'Kimi，超长文本（读整本书）',
  'claude-sonnet-4-20250514': '日常主力，平衡性价比',
  'claude-haiku-4-5-20251001': '便宜快速，简单任务',
  'claude-opus-4-8': '最强，复杂任务',
  'claude-3-5-sonnet': 'Claude 3.5 经典款',
  'gpt-4o': 'OpenAI通用旗舰',
  'gpt-4o-mini': 'OpenAI便宜款',
  'gpt-4': 'GPT-4 经典',
  'gpt-3.5-turbo': 'GPT-3.5，老牌便宜',
  'grok-2-latest': 'xAI Grok，最新版',
  'grok-beta': 'xAI Grok 测试版',
};

// 模型分组规则：返回 'cn'（国产）或 'overseas'（海外）
function classifyModel(id) {
  const domestic = ['deepseek', 'glm', 'moonshot', 'qwen', 'ernie', 'spark', 'hunyuan', 'baichuan', 'yi-', 'step'];
  const lower = id.toLowerCase();
  if (domestic.some((p) => lower.startsWith(p))) return 'cn';
  return 'overseas';
}

function descOf(id) {
  return MODEL_DESC[id] || '';
}

export async function models(subArgs) {
  console.log('╔══════════════════════════════════════════╗');
  console.log('║      AIXX 可用模型                         ║');
  console.log('╚══════════════════════════════════════════╝\n');

  const apiKey = loadApiKey();
  const baseUrl = process.env.AIXX_BASE_URL || DEFAULT_BASE_URL;

  if (!apiKey) {
    console.error('❌ 未找到AIXX API Key');
    console.error('   请先运行 aixx install，或设置环境变量 AIXX_API_KEY');
    process.exit(1);
  }

  // 拉模型列表
  let modelIds = [];
  try {
    const resp = await fetch(`${baseUrl}/models`, {
      headers: { Authorization: `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(FETCH_TIMEOUT),
    });
    if (!resp.ok) {
      if (resp.status === 401) {
        console.error('❌ API Key 无效（401），请重新 install 或检查 key');
        process.exit(1);
      }
      console.error(`❌ 获取模型列表失败: HTTP ${resp.status}`);
      process.exit(1);
    }
    const data = await resp.json();
    const arr = data.data || data.models || [];
    modelIds = arr
      .map((m) => (typeof m === 'string' ? m : m.id))
      .filter(Boolean)
      .sort();
  } catch (err) {
    console.error(`❌ ${friendlyNetErr(err)}`);
    process.exit(1);
  }

  if (modelIds.length === 0) {
    console.log('⚠️  后端未返回任何模型，可能是账户没有可用模型权限。');
    return;
  }

  // 分组
  const cn = modelIds.filter((id) => classifyModel(id) === 'cn');
  const overseas = modelIds.filter((id) => classifyModel(id) === 'overseas');

  // 国产组
  console.log('🇨🇳 国产模型（便宜）：');
  if (cn.length > 0) {
    cn.forEach((id) => {
      const desc = descOf(id);
      console.log(`   • ${id}${desc ? '  —— ' + desc : ''}`);
    });
  } else {
    console.log('   （暂无）');
  }

  // 海外组
  console.log('\n🚀 海外模型（强）：');
  if (overseas.length > 0) {
    overseas.forEach((id) => {
      const desc = descOf(id);
      console.log(`   • ${id}${desc ? '  —— ' + desc : ''}`);
    });
  } else {
    console.log('   （暂无）');
  }

  console.log(`\n📊 共 ${modelIds.length} 个模型\n`);

  console.log('💡 选模型小抄：');
  console.log('   - 最便宜日常任务 → deepseek-chat');
  console.log('   - 写中文文案/邮件 → glm-4-plus');
  console.log('   - 读超长文档/书籍 → moonshot-v1-128k');
  console.log('   - 复杂推理/代码 → deepseek-reasoner 或 claude-opus-4-8');
  console.log('   - 通用旗舰 → gpt-4o 或 claude-sonnet-4\n');
}
