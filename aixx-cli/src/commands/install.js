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
import { DEFAULT_BASE_URL } from '../../bin/aixx.js';
import { downloadSkill } from '../utils/download.js';
import { setupEnv } from '../utils/env.js';

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

// 生成随机用户名（aixx_开头+随机6位）
function genUsername() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let suffix = '';
  for (let i = 0; i < 6; i++) suffix += chars[Math.floor(Math.random() * chars.length)];
  return `aixx_${suffix}`;
}

// 生成随机密码
function genPassword() {
  const chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let pwd = '';
  for (let i = 0; i < 16; i++) pwd += chars[Math.floor(Math.random() * chars.length)];
  return pwd;
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
    regCode = refCode;
    regBody.aff_code = refCode;
    console.log(`   推荐码: ${refCode}`);
  }

  const regUrl = baseUrl.replace(/\/v1$/, '') + '/api/user/register';
  const regResp = await fetch(regUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(regBody)
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
    body: JSON.stringify({ username, password })
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
      remain_quota: -1,
      unlimited_quota: true
    })
  });
  const tokenData = await tokenResp.json();

  if (!tokenData.success) {
    throw new Error(`创建Key失败: ${tokenData.message}`);
  }

  // 查key
  const listResp = await fetch(`${baseUrl.replace(/\/v1$/, '')}/api/token/?p=0&page_size=1`, {
    headers: { 'Authorization': `Bearer ${userToken}` }
  });
  const listData = await listResp.json();
  const list = listData.data;
  const items = Array.isArray(list) ? list : (list?.items || []);
  const apiKey = items[0]?.key;

  if (!apiKey) {
    throw new Error('无法获取API Key');
  }

  console.log(`✅ API Key已创建: sk-${apiKey.slice(0, 8)}...${apiKey.slice(-4)}`);

  // 保存账号信息到本地（方便用户找回）
  const aixxDir = join(homedir(), '.aixx');
  if (!existsSync(aixxDir)) mkdirSync(aixxDir, { recursive: true });
  const fullKey = `sk-${apiKey}`;
  writeFileSync(join(aixxDir, 'account.json'), JSON.stringify({
    username,
    password,
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
  let apiKey = process.env.AIXX_API_KEY;

  if (!apiKey) {
    // 检查本地是否有已保存的账号
    const accountFile = join(homedir(), '.aixx', 'account.json');
    if (existsSync(accountFile)) {
      try {
        const account = JSON.parse(readFileSync(accountFile, 'utf-8'));
        apiKey = account.apiKey;
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
      } catch (err) {
        console.error(`\n❌ 自动注册失败: ${err.message}`);
        console.error('   你可以手动到 AIXX 平台注册后，用已有key重新运行 install。');
        process.exit(1);
      }
    } else if (choice.startsWith('sk-')) {
      // 用户输入已有key
      apiKey = choice;
      console.log('✅ 使用你提供的API Key');
    } else {
      console.error('❌ 无效的输入');
      process.exit(1);
    }
  } else {
    console.log('\n✅ 已检测到 AIXX_API_KEY 环境变量');
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

  // 6. 测试连通性
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

  // 完成
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║      🎉 安装完成！                        ║');
  console.log('╚══════════════════════════════════════════╝\n');
  console.log('现在你可以对自己的agent说：');
  console.log('  "帮我用deepseek-chat翻译：Hello World"\n');
  console.log('查询余额：');
  console.log('  "我AIXX还剩多少额度？"\n');
  console.log('文档：https://gitee.com/kk0803/token-hub\n');
}

async function testConnectivity(apiKey) {
  const url = DEFAULT_BASE_URL.replace(/\/v1$/, '') + '/api/status';
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
}
