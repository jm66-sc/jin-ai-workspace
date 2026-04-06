# launchd 心跳安装说明

> 执行者：金龙
> 安装一次，永久生效（开机自启、崩溃自恢复）

---

## 安装步骤

### 1. 确认 claude 路径

```bash
which claude
```

如果路径不是 `/usr/local/bin/claude`，编辑两个 plist 文件中的 `ProgramArguments`，替换为实际路径。

### 2. 安装两个心跳进程

```bash
# 代理参谋长（每3小时）
cp ~/Desktop/jin-ai-workspace/tools/launchd/com.jinai.claude-deputy.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jinai.claude-deputy.plist

# 每日日报（22:30）
cp ~/Desktop/jin-ai-workspace/tools/launchd/com.jinai.claude-nightly.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jinai.claude-nightly.plist
```

### 3. 验证已加载

```bash
launchctl list | grep jinai
```

应看到两行输出。

---

## 手动触发测试

```bash
# 测试代理参谋长（立即运行一次）
launchctl start com.jinai.claude-deputy

# 查看日志
tail -f /tmp/claude-deputy.log
tail -f /tmp/claude-deputy-error.log
```

---

## 卸载

```bash
launchctl unload ~/Library/LaunchAgents/com.jinai.claude-deputy.plist
launchctl unload ~/Library/LaunchAgents/com.jinai.claude-nightly.plist
rm ~/Library/LaunchAgents/com.jinai.claude-deputy.plist
rm ~/Library/LaunchAgents/com.jinai.claude-nightly.plist
```

---

## 常见问题

**Q：触发了但没有 GitHub commit？**
检查 git 凭证是否有效：`git -C ~/Desktop/jin-ai-workspace push`

**Q：claude 命令找不到？**
编辑 plist 中的路径，或在 ProgramArguments 前加：
```xml
<string>export PATH=$PATH:/usr/local/bin;</string>
```

**Q：日志乱码？**
在 bash -c 命令前加 `export LANG=en_US.UTF-8 &&`
