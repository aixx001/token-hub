# AIXX 踩坑记录（LESSONS_LEARNED）

> 踩到坑了再查。每踩一个坑记一条。
> 维护者：龙龙 | 2026-08-08 建立

---

## 🔴 坑1：强改ZCode的setting.json导致ZCode崩溃+数据丢失（重大事故）

**时间**：2026-08-09 会话7
**严重度**：🔴 重大（ZCode左侧任务/项目全丢，需找客服恢复）

### 事故经过
龙龙为了让agent"换底座"到AIXX，手动修改了ZCode的 `~/.zcode/v2/setting.json`：
- `providerFamilyDomain` 从 `"zai"` 改成 `"aixx"`
- 加了 `modelProviderFamilyModes.aixx` 和 `modelProviderFamilySelectedKeys.aixx`

**结果**：ZCode重启后，`"aixx"` 是非法的家族名（ZCode只认内置的 `zai`/`bigmodel`），导致：
1. ZCode配置解析异常
2. 左侧任务栏、项目列表全部丢失
3. K哥找ZCode客服导日志才恢复

### 根因
1. **龙龙在没确认ZCode配置规范的情况下，强改闭源软件的配置文件**
2. ZCode的 `providerFamilyDomain` 只接受内置家族名（zai/bigmodel），不支持自定义供应商做家族
3. 自定义供应商（UUID key）只能在UI里手动选中，不能用配置文件切换

### 正确做法
**绝对不要改 `setting.json` 的以下字段**：
- ❌ `providerFamilyDomain`（只认zai/bigmodel）
- ❌ `modelProviderFamilyModes`（只加内置家族）
- ❌ `modelProviderFamilySelectedKeys`（格式是preset:builtin:xxx，不支持custom:）

**安全的做法**：
- ✅ 改 `config.json` 的 `provider` 字典（加AIXX供应商）——这个是安全的
- ✅ 让用户在ZCode UI里手动选AIXX供应商——install后提示用户
- ❌ 不要试图用配置文件自动切换"当前选中"的供应商

### 教训
1. **强改闭源软件配置=玩火**。ZCode的配置规则随时变，强改一次没事不代表下次没事
2. **"换底座"在ZCode上做不到全自动**。只能install时配好供应商，让用户手动切一次
3. **install.js必须去掉setting.json的修改逻辑**（当前代码里可能还有残留，要清理）
4. **任何修改用户配置的操作，必须先备份+提示用户+验证不崩溃**

### 相关文件
- 出事代码：龙龙在会话7手动执行的node脚本（改setting.json）
- 备份：C:\Users\Administrator\.zcode\v2\setting.json.bak.aixx / .bak.aixx2
- ZCode客服反馈：`providerFamilyDomain: aixx` 是非法字段

---

## 坑2：（暂无，待积累）
