#!/usr/bin/env node

/**
 * AIXX CLI
 * 让你的AI调用万物。
 *
 * 用法：
 *   npx aixx-cli install [推荐码]    安装AIXX skill到本地agent
 *   npx aixx-cli config               配置/查看AIXX
 *   npx aixx-cli test                 测试AIXX是否可用
 *   npx aixx-cli --version            查看版本
 */

import { install } from '../src/commands/install.js';
import { config } from '../src/commands/config.js';
import { test } from '../src/commands/test.js';
import { showHelp, showVersion } from '../src/commands/help.js';

const VERSION = '0.1.0';

// 默认AIXX后端地址
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
