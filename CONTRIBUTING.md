# Contributing

感谢你愿意参与改进 `development-intent-anchor-point`！

## 如何贡献

1. 先开一个 [Issue](https://github.com/3264156243/development-intent-anchor-point/issues)
   描述你的想法或问题，避免重复劳动；
2. Fork 本仓库，在独立分支上修改；
3. 提交前请确认：
   - Python 脚本可以通过 `python -m py_compile scripts/*.py`；
   - 生成问卷的流程可以正常跑通（`generate_questionnaire.py --questions ... --open`）；
   - `plugin.json` 与 marketplace 条目保持名称一致；
4. 发起 Pull Request，说明改动目的和验证方式。

## 本地开发

```bash
codex plugin marketplace add <本仓库本地路径>
codex plugin add development-intent-anchor-point@development-intent-anchor-point
```

改动插件源码后，开一个新 Codex 任务即可加载最新内容。

## 行为准则

请保持友善、就事论事。所有讨论与代码均遵循 MIT 许可证。
