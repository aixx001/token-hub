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
  aixx install [推荐码]    安装AIXX skill到本地agent
  aixx config              配置或查看AIXX设置
  aixx test                测试AIXX是否可用
  aixx --version           查看版本
  aixx --help              显示此帮助

安装示例：
  npx aixxai install              普通安装
  npx aixxai install zhangsan     通过张三的推荐码安装（张三获分润）

关于AIXX：
  AIXX = "AI的谷歌"。装一个skill，agent就能调用全世界的AI能力。
  永远不用碰key、参数、文档，一切通过对话。

文档：https://gitee.com/kk0803/token-hub
`);
}

export function showVersion(version) {
  console.log(`AIXX CLI v${version}`);
}
