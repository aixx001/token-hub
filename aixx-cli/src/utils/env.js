/**
 * 环境变量配置工具
 *
 * 把AIXX_API_KEY和AIXX_BASE_URL写入用户的shell配置
 * 支持 bash/zsh (Linux/macOS) 和 PowerShell (Windows)
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const DEFAULT_BASE_URL = 'http://14.103.27.195:8080/v1';

export function setupEnv(apiKey, baseUrl = DEFAULT_BASE_URL) {
  const platform = process.platform;
  const home = homedir();

  // 1. 写入AIXX本地配置文件（所有平台通用）
  const aixxDir = join(home, '.aixx');
  if (!existsSync(aixxDir)) mkdirSync(aixxDir, { recursive: true });
  const configFile = join(aixxDir, 'config.json');
  writeFileSync(configFile, JSON.stringify({
    AIXX_API_KEY: apiKey,
    AIXX_BASE_URL: baseUrl,
    configuredAt: new Date().toISOString()
  }, null, 2));

  // 2. 写入shell配置（Linux/macOS）
  if (platform !== 'win32') {
    const envLines = [
      ``,
      `# AIXX 配置 (由 aixx-cli 添加)`,
      `export AIXX_API_KEY="${apiKey}"`,
      `export AIXX_BASE_URL="${baseUrl}"`,
    ].join('\n');

    // 检测shell类型
    const shellConfigs = [
      join(home, '.zshrc'),
      join(home, '.bashrc'),
      join(home, '.bash_profile'),
    ];

    let written = false;
    for (const conf of shellConfigs) {
      if (existsSync(conf)) {
        // 检查是否已配置过（避免重复）
        const existing = readFileSync(conf, 'utf-8');
        if (!existing.includes('AIXX_API_KEY')) {
          appendFileSync(conf, envLines);
          console.log(`   → 已写入 ${conf}`);
        }
        written = true;
        break;
      }
    }

    if (!written) {
      // 没找到现成配置文件，写.bashrc
      const bashrc = join(home, '.bashrc');
      appendFileSync(bashrc, envLines);
      console.log(`   → 已写入 ${bashrc}`);
    }

    console.log('   ⚠️  请运行 source ~/.bashrc 或 source ~/.zshrc 让配置生效');
  } else {
    // Windows: 写入用户环境变量（用setx）
    console.log('   Windows用户请手动设置环境变量，或运行以下命令（PowerShell）：');
    console.log(`   [Environment]::SetEnvironmentVariable("AIXX_API_KEY", "${apiKey}", "User")`);
    console.log(`   [Environment]::SetEnvironmentVariable("AIXX_BASE_URL", "${baseUrl}", "User")`);
  }
}
