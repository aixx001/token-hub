/**
 * AIXX CLI - 帮助信息
 */

export function showHelp(version) {
  console.log(`
╔══════════════════════════════════════════╗
║         AIXX CLI v${version}                 ║
║      让你的AI调用万物                      ║
╚══════════════════════════════════════════╝

用法：
  aixx install [推荐码]    安装AIXX skill到本地agent（含零配置）
  aixx config              配置或查看AIXX设置
  aixx test                测试AIXX是否可用
  aixx balance             查询账户余额（还剩多少钱）
  aixx models              列出可用模型（国产/海外分组）
  aixx recharge [金额]     充值引导（默认$5）
  aixx --version           查看版本
  aixx --help              显示此帮助

安装示例：
  npx aixxai install              普通安装（自动注册，送¥5额度）
  npx aixxai install zhangsan     通过张三的推荐码安装（张三获分润）

账户示例：
  aixx balance                    查看余额
  aixx balance 20                 （金额参数对balance无效，仅recharge用）
  aixx models                     看有哪些模型可调
  aixx recharge 10                充 $10

关于AIXX：
  AIXX = "AI的谷歌"。装一个skill，agent就能调用全世界的AI能力。
  永远不用碰key、参数、文档，一切通过对话。

文档：https://gitee.com/kk0803/token-hub
`);
}

export function showVersion(version) {
  console.log(`AIXX CLI v${version}`);
}
