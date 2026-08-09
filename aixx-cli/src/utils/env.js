/**
 * 环境变量配置工具
 *
 * 把AIXX_API_KEY和AIXX_BASE_URL写入用户的shell配置
 * 支持 bash/zsh (Linux/macOS) 和 PowerShell (Windows)
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// ⚠️ 安全警告：当前用HTTP明文传输API Key（http://），存在凭据被嗅探风险。
// TODO（安全）：后端配置好HTTPS证书后，把下面的 URL 改为 'https://14.103.27.195:8080/v1'。
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

    // 检测当前用的shell（优先看$SHELL，比按文件存在猜更准）
    // Mac默认zsh，Linux多是bash。$SHELL是用户登录shell，最可靠。
    const currentShell = process.env.SHELL || '';
    let shellConfigs;
    if (currentShell.includes('zsh')) {
      // zsh用户：写.zshrc（Mac默认）
      shellConfigs = [join(home, '.zshrc')];
    } else if (currentShell.includes('bash')) {
      // bash用户：Linux写.bashrc，Mac写.bash_profile（Mac的bash读.bash_profile）
      shellConfigs = platform === 'darwin'
        ? [join(home, '.bash_profile'), join(home, '.bashrc')]
        : [join(home, '.bashrc'), join(home, '.bash_profile')];
    } else {
      // 检测不到（如fish等），按文件存在兜底
      shellConfigs = [
        join(home, '.zshrc'),
        join(home, '.bashrc'),
        join(home, '.bash_profile'),
      ];
    }

    let writtenFile = null;
    for (const conf of shellConfigs) {
      if (existsSync(conf)) {
        // 检查是否已配置过（避免重复）
        const existing = readFileSync(conf, 'utf-8');
        if (!existing.includes('AIXX_API_KEY')) {
          appendFileSync(conf, envLines);
          console.log(`   → 已写入 ${conf}`);
        } else {
          console.log(`   → ${conf} 已有AIXX配置，跳过`);
        }
        writtenFile = conf;
        break;
      }
    }

    if (!writtenFile) {
      // 没找到现成配置文件，按当前shell创建一个
      const fallback = currentShell.includes('zsh') ? join(home, '.zshrc') : join(home, '.bashrc');
      appendFileSync(fallback, envLines);
      console.log(`   → 已创建并写入 ${fallback}`);
      writtenFile = fallback;
    }

    const rcName = writtenFile.split(/[\\/]/).pop();
    console.log(`   ⚠️  请运行 source ~/${rcName} 让配置生效（或重开终端）`);
  } else {
    // Windows: 写入用户环境变量（用setx）
    console.log('   Windows用户请手动设置环境变量，或运行以下命令（PowerShell）：');
    console.log(`   [Environment]::SetEnvironmentVariable("AIXX_API_KEY", "${apiKey}", "User")`);
    console.log(`   [Environment]::SetEnvironmentVariable("AIXX_BASE_URL", "${baseUrl}", "User")`);
  }
}
