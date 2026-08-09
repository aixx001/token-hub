#!/usr/bin/env node

/**
 * AIXX CLI
 * 让你的AI调用万物。
 *
 * 用法：
 *   npx aixxai install [推荐码]    安装AIXX skill到本地agent（含零配置）
 *   npx aixxai config               配置/查看AIXX
 *   npx aixxai test                 测试AIXX是否可用
 *   npx aixxai balance              查询账户余额
 *   npx aixxai models               列出可用模型（分组）
 *   npx aixxai recharge [金额]      充值引导
 *   npx aixxai --version            查看版本
 */

import { install } from '../src/commands/install.js';
import { config } from '../src/commands/config.js';
import { test } from '../src/commands/test.js';
import { balance } from '../src/commands/balance.js';
import { models } from '../src/commands/models.js';
import { recharge } from '../src/commands/recharge.js';
import { showHelp, showVersion } from '../src/commands/help.js';

const VERSION = '0.1.0';

// 默认AIXX后端地址
// ⚠️ 安全警告：当前用HTTP明文传输API Key（http://），存在凭据被嗅探风险。
// TODO（安全）：后端配置好HTTPS证书后，把下面的 URL 改为 'https://14.103.27.195:8080/v1'。
// 改完后请全局搜索 "安全警告" 同步更新 env.js 与 templates/QUICKSTART.md 中的同名地址。
export const DEFAULT_BASE_URL = 'http://14.103.27.195:8080/v1';

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const subArgs = args.slice(1);

  switch (command) {
    case 'install':
    case 'i':
      await install(subArgs);
      break;
    case 'config':
    case 'c':
      await config(subArgs);
      break;
    case 'test':
    case 't':
      await test(subArgs);
      break;
    case 'balance':
    case 'b':
      await balance(subArgs);
      break;
    case 'models':
    case 'm':
      await models(subArgs);
      break;
    case 'recharge':
    case 'r':
      await recharge(subArgs);
      break;
    case '--version':
    case '-v':
      showVersion(VERSION);
      break;
    case '--help':
    case '-h':
    case 'help':
    case undefined:
      showHelp(VERSION);
      break;
    default:
      console.error(`未知命令: ${command}`);
      console.error('运行 aixx --help 查看可用命令');
      process.exit(1);
  }
}

main().catch(err => {
  console.error('❌ 发生错误:', err.message);
  process.exit(1);
});
