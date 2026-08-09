# AIXX CLI

> 让你的AI调用万物。一个命令，agent就能调用全世界的AI能力。

## 安装

```bash
npx aixxai install
```

带推荐码安装（推荐人获分润）：

```bash
npx aixxai install zhangsan
```

## 命令

| 命令 | 说明 |
|---|---|
| `aixx install [推荐码]` | 安装AIXX skill到本地agent |
| `aixx config` | 查看当前配置 |
| `aixx test` | 测试AIXX连通性+调用模型 |
| `aixx --version` | 查看版本 |
| `aixx --help` | 帮助 |

## 当前状态（1.0.0）

- ✅ CLI代码完成，本地测试通过
- ⏳ 待发布到npm（等注册）
- ✅ 后端已部署：http://14.103.27.195:8080
- ✅ 已接通：DeepSeek / GLM / Kimi

## 技术栈

- Node.js (>=18) + ES Modules
- 纯原生API，零运行时依赖
- skill文件内嵌在包里（templates/），网络挂了也能装

## 文档

完整文档：https://gitee.com/kk0803/token-hub

---
维护者：龙龙（AIXX PM）| 2026-08-08
