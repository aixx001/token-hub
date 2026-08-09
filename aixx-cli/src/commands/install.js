/**
 * AIXX CLI - install 命令
 *
 * 完整流程（用户一键完成）：
 *   1. 检测环境
 *   2. 如果没有key → 自动注册AIXX账号 → 拿key（不用用户填表单）
 *   3. 如果有推荐码 → 注册时绑定归因（KOL分销）
 *   4. 下载skill文件
 *   5. 配置环境变量
 *   6. 测试连通性
 */

import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import readline from 'readline';
import { randomInt } from 'crypto';
import { DEFAULT_BASE_URL } from '../../bin/aixx.js';
import { downloadSkill } from '../utils/download.js';
import { setupEnv } from '../utils/env.js';
import { configureAgents } from '../utils/agentconfig.js';

// skill目录检测
function detectSkillDirs() {
  const home = homedir();
  const candidates = [
    join(home, '.zcode', 'skills'),
    join(home, '.agents', 'skills'),
    join(home, '.claude', 'skills'),
    join(home, '.aixx', 'skills'),
  ];
  return candidates.filter(p => existsSync(p));
}

async function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, ans => { rl.close(); resolve(ans.trim()); }));
}

// 生成随机用户名（aixx_开头+随机8位）。用 CSPRNG 避免可预测。
function genUsername() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let suffix = '';
  for (let i = 0; i < 8; i++) suffix += chars[randomInt(0, chars.length)];
  return `aixx_${suffix}`;
}

// 生成随机密码（16位）。用 CSPRNG 保证密码学强度。
function genPassword() {
  const chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let pwd = '';
  for (let i = 0; i < 16; i++) pwd += chars[randomInt(0, chars.length)];
  return pwd;
}

// 所有对外请求统一 15 秒超时（AbortSignal.timeout 在 Node 17.3+ 可用，本 CLI 要求 18+）
const FETCH_TIMEOUT = 15000;
// 把网络/超时异常的报错信息统一成友好提示
function friendlyNetErr(err) {
  return err?.name === 'TimeoutError' || err?.name === 'AbortError'
    ? '连接超时，请检查网络'
    : err?.message || String(err);
}

// 自动注册AIXX账号
async function autoRegister(baseUrl, refCode) {
  const username = genUsername();
  const password = genPassword();

  console.log(`\n📝 正在为你注册AIXX账号...`);
  console.log(`   用户名: ${username}`);

  // 注册（带推荐码如果有）
  const regBody = { username, password };
  if (refCode) {
    regBody.aff_code = refCode;
    console.log(`   推荐码: ${refCode}`);
  }

  const regUrl = baseUrl.replace(/\/v1$/, '') + '/api/user/register';
  const regResp = await fetch(regUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(regBody),
    signal: AbortSignal.timeout(FETCH_TIMEOUT),
  });
  const regData = await regResp.json();

  if (!regData.success) {
    throw new Error(`注册失败: ${regData.message || '未知错误'}`);
  }
  console.log('✅ 注册成功');

  // 登录拿token
  console.log('   正在登录...');
  const loginUrl = baseUrl.replace(/\/v1$/, '') + '/api/user/login';
  const loginResp = await fetch(loginUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    signal: AbortSignal.timeout(FETCH_TIMEOUT),
  });
  const loginData = await loginResp.json();

  if (!loginData.success) {
    throw new Error(`登录失败: ${loginData.message}`);
  }
  const userToken = loginData.data.access_token;
  console.log('✅ 登录成功');

  // 创建API key
  console.log('   正在创建你的专属API Key...');
  const tokenUrl = baseUrl.replace(/\/v1$/, '') + '/api/token/';
  const tokenResp = await fetch(tokenUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'default',
      remain_quota: -1,          // -1=跟随用户额度（New-API的"不限量"标记，token用user.quota）
      unlimited_quota: true      // true=不限量token。注意：这会让billing接口返回hard_limit_usd=1亿
                                  // （New-API把unlimited token的额度显示成1亿），balance命令里已特殊处理
                                  // 这个1亿标记，会换算成真实的user.quota来显示，不会误导用户。
    }),
    signal: AbortSignal.timeout(FETCH_TIMEOUT),
  });
  const tokenData = await tokenResp.json();

  if (!tokenData.success) {
    throw new Error(`创建Key失败: ${tokenData.message}`);
  }

  // 查key：列表里的 key 是脱敏的（sk-xxxx****xxxx），不能直接用。
  // 正确做法：先查列表拿 token id，再调 POST /api/token/:id/key 取未脱敏的完整 key。
  const apiBase = baseUrl.replace(/\/v1$/, '');
  const listResp = await fetch(`${apiBase}/api/token/?p=0&page_size=1`, {
    headers: { 'Authorization': `Bearer ${userToken}` },
    signal: AbortSignal.timeout(FETCH_TIMEOUT),
  });
  const listData = await listResp.json();
  const list = listData.data;
  const items = Array.isArray(list) ? list : (list?.items || []);
  const tokenId = items[0]?.id;

  if (!tokenId) {
    throw new Error('无法获取API Key（找不到刚创建的token）');
  }

  // 取未脱敏的完整 key（GET 列表会脱敏，必须用这个专用接口）
  const keyResp = await fetch(`${apiBase}/api/token/${tokenId}/key`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${userToken}` },
    signal: AbortSignal.timeout(FETCH_TIMEOUT),
  });
  const keyData = await keyResp.json();
  const apiKey = keyData?.data?.key;

  if (!apiKey) {
    throw new Error('无法获取API Key（取key接口未返回key）');
  }

  console.log(`✅ API Key已创建: sk-${apiKey.slice(0, 8)}...${apiKey.slice(-4)}`);

  // 保存账号信息到本地（方便用户找回）
  // 安全：不存明文密码。注册时密码只用于首次登录拿token，之后用apiKey就够了。
  // 丢了账号可以重新注册（免费），所以不需要保留密码。
  const aixxDir = join(homedir(), '.aixx');
  if (!existsSync(aixxDir)) mkdirSync(aixxDir, { recursive: true });
  const fullKey = `sk-${apiKey}`;
  writeFileSync(join(aixxDir, 'account.json'), JSON.stringify({
    username,
    apiKey: fullKey,  // 存完整key（本地文件，不进git）
    registeredAt: new Date().toISOString(),
    refCode: refCode || null
  }, null, 2));

  console.log(`\n💾 账号信息已保存到 ~/.aixx/account.json`);
  console.log(`   （忘记key时可以在这里找到）`);

  return `sk-${apiKey}`;
}

export async function install(subArgs) {
  console.log('╔══════════════════════════════════════════╗');
  console.log('║      AIXX 安装程序                        ║');
  console.log('║      让你的AI调用万物                      ║');
  console.log('╚══════════════════════════════════════════╝\n');

  // 推荐码
  const refCode = subArgs[0];
  if (refCode) {
    console.log(`📋 推荐码: ${refCode}（推荐人将获得消费分润）\n`);
  }

  // 1. 检测Node版本
  const nodeVersion = process.versions.node;
  const major = parseInt(nodeVersion.split('.')[0]);
  if (major < 18) {
    console.error(`❌ Node版本过低（当前${nodeVersion}），需要18+。`);
    process.exit(1);
  }
  console.log(`✅ Node版本: ${nodeVersion}`);
  console.log(`✅ 操作系统: ${process.platform}`);

  // 2. 获取或创建API Key
  // 记录key来源，用于后面给出正确的提示（环境变量 / 本地账号）
  let apiKey = process.env.AIXX_API_KEY;
  let keySource = apiKey ? 'env' : null;

  if (!apiKey) {
    // 检查本地是否有已保存的账号
    const accountFile = join(homedir(), '.aixx', 'account.json');
    if (existsSync(accountFile)) {
      try {
        const account = JSON.parse(readFileSync(accountFile, 'utf-8'));
        apiKey = account.apiKey;
        keySource = 'account';
        console.log(`\n✅ 发现已保存的账号: ${account.username}`);
        console.log(`   使用已保存的API Key`);
      } catch (e) {
        // 读取失败，继续注册
      }
    }
  }

  if (!apiKey) {
    // 没有key → 自动注册
    console.log('\n📝 你还没有AIXX账号，现在为你自动注册（免费，含试用额度）...');
    const choice = await ask('\n按回车继续注册，或输入已有的API Key (sk-xxxx): ');

    if (choice === '') {
      // 自动注册
      try {
        apiKey = await autoRegister(DEFAULT_BASE_URL, refCode);
        keySource = 'registered';
      } catch (err) {
        // 网络/超时类异常给友好提示，业务错误（注册/登录/创建key失败）保留原文
        const msg = /timeout|abort|fetch|network|ECONN|ETIMEDOUT|getaddrinfo/i.test(err.message)
          ? friendlyNetErr(err)
          : err.message;
        console.error(`\n❌ 自动注册失败: ${msg}`);
        console.error('   你可以手动到 AIXX 平台注册后，用已有key重新运行 install。');
        process.exit(1);
      }
    } else if (choice.startsWith('sk-')) {
      // 用户输入已有key
      apiKey = choice;
      keySource = 'manual';
      console.log('✅ 使用你提供的API Key');
    } else {
      console.error('❌ 无效的输入');
      process.exit(1);
    }
  } else {
    // 区分来源：环境变量 vs 本地账号文件
    if (keySource === 'env') {
      console.log('\n✅ 已检测到 AIXX_API_KEY 环境变量');
    } else {
      console.log('\n✅ 已检测到本地账号文件（~/.aixx/account.json）');
    }
  }

  // 3. 检测/创建skill目录
  let skillDirs = detectSkillDirs();
  let targetDir;

  if (skillDirs.length > 0) {
    console.log(`\n📂 检测到agent skill目录:`);
    skillDirs.forEach((d, i) => console.log(`   ${i + 1}. ${d}`));
    targetDir = skillDirs[0];
    console.log(`   → 安装到: ${targetDir}`);
  } else {
    targetDir = join(homedir(), '.aixx', 'skills');
    mkdirSync(targetDir, { recursive: true });
    console.log(`\n📂 创建skill目录: ${targetDir}`);
    console.log('   （如果你的agent在其他位置，安装后手动复制 aixx/ 文件夹过去）');
  }

  // 4. 下载skill文件
  const aixxSkillDir = join(targetDir, 'aixx');
  console.log('\n⬇️  安装skill文件...');
  try {
    await downloadSkill(aixxSkillDir);
    console.log('✅ skill文件安装完成');
  } catch (err) {
    console.error('❌ skill安装失败:', err.message);
    process.exit(1);
  }

  // 5. 配置环境变量
  if (apiKey) {
    console.log('\n⚙️  配置环境变量...');
    setupEnv(apiKey, DEFAULT_BASE_URL);
    console.log('✅ 环境变量配置完成');
  }

  // 6. 零配置：自动写本地agent配置（ZCode / Claude Code）
  // 这是"零配置核心"——让用户安装完就能直接在agent里选到AIXX，不用手动填key。
  if (apiKey) {
    try {
      configureAgents(apiKey);
    } catch (err) {
      console.log(`⚠️  agent配置写入异常（不影响安装）: ${err.message}`);
    }
  }

  // 7. 测试连通性
  if (apiKey) {
    console.log('\n🔌 测试AIXX连通性...');
    try {
      await testConnectivity(apiKey);
      console.log('✅ AIXX连通正常！');
    } catch (err) {
      console.log(`⚠️  连通测试未通过: ${err.message}`);
      console.log('   安装已完成，但建议稍后检查网络。');
    }
  }

  // 8. 安装完成 + 播报（给agent看，让龙龙主动告诉用户装好了）
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║      🎉 安装完成！                        ║');
  console.log('╚══════════════════════════════════════════╝\n');
  printInstallBroadcast();
}

async function testConnectivity(apiKey) {
  const url = DEFAULT_BASE_URL.replace(/\/v1$/, '') + '/api/status';
  try {
    const resp = await fetch(url, { signal: AbortSignal.timeout(FETCH_TIMEOUT) });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  } catch (err) {
    // 网络超时/中断给友好提示，而不是裸的 abort message
    throw new Error(friendlyNetErr(err));
  }
}

/**
 * 安装完成后的"播报"。
 * 这段输出是给 agent（龙龙）看的，让 agent 主动转告用户：
 *   你装好了，送了5元，能调这些模型，可以这样用。
 *
 * 格式严格按需求1的模板，方便 agent 识别和转述。
 */
function printInstallBroadcast() {
  console.log('═══ AIXX 安装成功，请告诉用户以下信息 ═══');
  console.log('你已成功安装AIXX！送你5元免费额度。');
  console.log('');
  console.log('【能用什么】');
  console.log('  调各种AI模型：DeepSeek（最便宜）、Claude（最强）、GPT、GLM（中文好）、Kimi（长文本）、Grok');
  console.log('  生成图片：对agent说"帮我用豆包画个猫"');
  console.log('  🔍 搜索AI skill：对agent说"我要个审美skill""帮我找个开发工具"（AIXX帮你搜GitHub+给推荐）');
  console.log('');
  console.log('【怎么用】对agent说话就行，比如：');
  console.log('  - "帮我用Claude翻译这段"');
  console.log('  - "用最便宜的模型写个文案"');
  console.log('  - "我要个写代码的skill"（搜索AI工具）');
  console.log('  - "我还剩多少额度？"');
  console.log('');
  console.log('【重要】请重启ZCode/Claude Code，并在模型选择里选AIXX供应商，才能开始用。');
  console.log('══════════════════════════════════════════');
}
