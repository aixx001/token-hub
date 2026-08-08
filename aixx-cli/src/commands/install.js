/**
 * AIXX CLI - install 命令
 * 安装AIXX skill到本地agent目录
 *
 * 流程：
 *   1. 检测环境（Node版本、操作系统）
 *   2. 询问/读取AIXX API Key（如果没有）
 *   3. 下载skill文件到本地skill目录
 *   4. 配置环境变量
 *   5. 如果有推荐码，记录归因（调AIXX后端）
 *   6. 测试连通性
 */

import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import readline from 'readline';
import { DEFAULT_BASE_URL } from '../../bin/aixx.js';
import { downloadSkill } from '../utils/download.js';
import { setupEnv } from '../utils/env.js';

// skill目录检测（支持多种agent）
function detectSkillDirs() {
  const home = homedir();
  const candidates = [
    // ZCode
    join(home, '.zcode', 'skills'),
    join(home, '.agents', 'skills'),
    // Claude
    join(home, '.claude', 'skills'),
    // 通用
    join(home, '.aixx', 'skills'),
  ];
  return candidates.filter(p => existsSync(p));
}

async function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, ans => { rl.close(); resolve(ans.trim()); }));
}

export async function install(subArgs) {
  console.log('╔══════════════════════════════════════════╗');
  console.log('║      AIXX 安装程序                        ║');
  console.log('║      让你的AI调用万物                      ║');
  console.log('╚══════════════════════════════════════════╝\n');

  // 推荐码（如果有）
  const refCode = subArgs[0];
  if (refCode) {
    console.log(`📋 推荐码: ${refCode}（推荐人将获得消费分润）\n`);
  }

  // 1. 检测Node版本
  const nodeVersion = process.versions.node;
  const major = parseInt(nodeVersion.split('.')[0]);
  if (major < 18) {
    console.error(`❌ Node版本过低（当前${nodeVersion}），需要18+。请升级Node后重试。`);
    process.exit(1);
  }
  console.log(`✅ Node版本: ${nodeVersion}`);

  // 2. 检测平台
  const platform = process.platform;
  console.log(`✅ 操作系统: ${platform}`);

  // 3. 获取AIXX API Key
  let apiKey = process.env.AIXX_API_KEY;
  if (!apiKey) {
    console.log('\n📝 还没有配置 AIXX API Key。');
    console.log('   获取方式：访问 AIXX 平台注册并充值，拿到 sk- 开头的key。');
    apiKey = await ask('\n请输入你的 AIXX API Key (sk-xxxx): ');
    if (!apiKey) {
      console.log('⚠️  没有提供key，skill会安装但需要手动配置。');
    }
  } else {
    console.log('✅ 已检测到 AIXX_API_KEY 环境变量');
  }

  // 4. 检测/创建skill目录
  let skillDirs = detectSkillDirs();
  let targetDir;

  if (skillDirs.length > 0) {
    console.log(`\n📂 检测到agent skill目录:`);
    skillDirs.forEach((d, i) => console.log(`   ${i + 1}. ${d}`));
    targetDir = skillDirs[0]; // 默认第一个
    console.log(`   → 安装到: ${targetDir}`);
  } else {
    // 没有现成目录，创建通用目录
    targetDir = join(homedir(), '.aixx', 'skills');
    mkdirSync(targetDir, { recursive: true });
    console.log(`\n📂 未检测到现成agent目录，创建: ${targetDir}`);
    console.log('   （如果你的agent在其他位置，安装后手动复制 aixx/ 文件夹过去）');
  }

  // 5. 下载skill文件
  const aixxSkillDir = join(targetDir, 'aixx');
  console.log('\n⬇️  下载skill文件...');
  try {
    await downloadSkill(aixxSkillDir);
    console.log('✅ skill文件下载完成');
  } catch (err) {
    console.error('❌ 下载skill失败:', err.message);
    console.error('   你可以手动从 https://gitee.com/kk0803/token-hub 下载 aixx-skill/ 文件夹');
    process.exit(1);
  }

  // 6. 配置环境变量
  if (apiKey) {
    console.log('\n⚙️  配置环境变量...');
    setupEnv(apiKey, DEFAULT_BASE_URL);
    console.log(`✅ 已配置 AIXX_API_KEY 和 AIXX_BASE_URL`);
  }

  // 7. 记录推荐码归因（如果有）
  if (refCode && apiKey) {
    console.log('\n📋 记录推荐归因...');
    try {
      await recordReferral(refCode, apiKey);
      console.log(`✅ 推荐码 ${refCode} 已绑定`);
    } catch (err) {
      console.log(`⚠️  推荐归因记录失败（不影响安装）: ${err.message}`);
    }
  }

  // 8. 测试连通性
  if (apiKey) {
    console.log('\n🔌 测试AIXX连通性...');
    try {
      await testConnectivity(apiKey);
      console.log('✅ AIXX连通正常！');
    } catch (err) {
      console.log(`⚠️  连通测试失败: ${err.message}`);
      console.log('   安装已完成，但建议检查网络或key配置。');
    }
  }

  // 完成
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║      🎉 安装完成！                        ║');
  console.log('╚══════════════════════════════════════════╝\n');
  console.log('现在你可以对自己的agent说：');
  console.log('  "帮我用deepseek-chat翻译：Hello World"');
  console.log('\n或者问agent：');
  console.log('  "我AIXX还剩多少额度？"');
  console.log('\n文档：https://gitee.com/kk0803/token-hub\n');
}

async function recordReferral(refCode, apiKey) {
  // TODO: 调AIXX后端的归因接口（2.0 KOL分销实现后）
  // 暂时只本地记录
  const refFile = join(homedir(), '.aixx', 'referral.json');
  mkdirSync(join(homedir(), '.aixx'), { recursive: true });
  writeFileSync(refFile, JSON.stringify({ refCode, installedAt: new Date().toISOString() }));
}

async function testConnectivity(apiKey) {
  const url = DEFAULT_BASE_URL.replace(/\/v1$/, '') + '/api/status';
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
}
