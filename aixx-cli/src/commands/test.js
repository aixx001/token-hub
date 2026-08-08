/**
 * AIXX CLI - test 命令
 * 测试AIXX是否可用
 */

import { DEFAULT_BASE_URL } from '../../bin/aixx.js';

export async function test(subArgs) {
  console.log('╔══════════════════════════════════════════╗');
  console.log('║      AIXX 连通性测试                       ║');
  console.log('╚══════════════════════════════════════════╝\n');

  const apiKey = process.env.AIXX_API_KEY;
  const baseUrl = process.env.AIXX_BASE_URL || DEFAULT_BASE_URL;

  if (!apiKey) {
    console.error('❌ AIXX_API_KEY 未配置');
    console.error('   运行 aixx install 配置，或手动设置环境变量');
    process.exit(1);
  }

  console.log(`测试地址: ${baseUrl}`);
  console.log(`使用Key: ${apiKey.slice(0, 8)}...${apiKey.slice(-4)}\n`);

  // 1. 测试状态接口
  console.log('1️⃣  测试状态接口...');
  try {
    const statusUrl = baseUrl.replace(/\/v1$/, '') + '/api/status';
    const resp = await fetch(statusUrl);
    if (resp.ok) {
      const data = await resp.json();
      console.log('   ✅ AIXX后端在线');
    } else {
      console.log(`   ⚠️  状态接口返回 ${resp.status}`);
    }
  } catch (err) {
    console.error(`   ❌ 连接失败: ${err.message}`);
    console.error('   请检查网络或AIXX_BASE_URL配置');
    process.exit(1);
  }

  // 2. 测试模型列表
  console.log('\n2️⃣  获取可用模型列表...');
  try {
    const resp = await fetch(`${baseUrl}/models`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    if (resp.ok) {
      const data = await resp.json();
      const models = data.data || data.models || [];
      console.log(`   ✅ 可用模型 (${models.length}个):`);
      models.slice(0, 10).forEach(m => {
        const id = typeof m === 'string' ? m : m.id;
        console.log(`      • ${id}`);
      });
      if (models.length > 10) console.log(`      ... 还有 ${models.length - 10} 个`);
    } else if (resp.status === 401) {
      console.error('   ❌ API Key 无效（401）');
      process.exit(1);
    } else {
      console.log(`   ⚠️  返回 ${resp.status}`);
    }
  } catch (err) {
    console.error(`   ❌ 失败: ${err.message}`);
  }

  // 3. 测试实际调用
  console.log('\n3️⃣  测试调用 deepseek-chat...');
  try {
    const resp = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{ role: 'user', content: '说"测试成功"三个字' }],
        max_tokens: 20
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      const reply = data.choices?.[0]?.message?.content || '(空回复)';
      const usage = data.usage || {};
      console.log(`   ✅ 调用成功！`);
      console.log(`   模型回复: ${reply}`);
      console.log(`   Token用量: ${usage.total_tokens || '?'}`);
    } else {
      const errData = await resp.json().catch(() => ({}));
      console.error(`   ❌ 调用失败 (${resp.status}): ${errData.error?.message || resp.statusText}`);
      if (resp.status === 402) console.error('   提示: 额度不足，请充值');
    }
  } catch (err) {
    console.error(`   ❌ 网络错误: ${err.message}`);
  }

  console.log('\n测试完成。\n');
}
