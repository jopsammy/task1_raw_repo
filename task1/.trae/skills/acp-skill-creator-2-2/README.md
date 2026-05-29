
# Skill Creator

创建新技能、修改和改进现有技能，并测量技能性能。

## 目录结构

```
skill-creator/
├── SKILL.md              # 主技能文件
├── README.md             # 本文件
├── LICENSE.txt           # 许可证
├── agents/               # 专业评估子Agent
│   ├── grader.md         # 评测agent
│   ├── comparator.md     # 盲比较agent
│   └── analyzer.md       # 分析agent
├── assets/               # 辅助模板
│   └── eval_review.html  # 评估集编辑页面
├── config/               # 配置文件目录
│   ├── backend.json      # 后端配置（非Claude Code需要）
│   └── README.md         # 配置说明
├── eval-viewer/          # 可视化反馈界面
│   ├── generate_review.py
│   └── viewer.html
├── references/           # 参考文档
│   ├── tool-usage-guide.md  # 工具使用指南
│   ├── workflow-details.md  # 详细工作流程
│   ├── eval-layers.md       # 评测分层定义
│   └── schemas.md           # JSON结构定义
└── scripts/              # 核心自动化工具
    ├── quick_validate.py
    ├── model_runner.py
    ├── run_eval.py
    ├── run_loop.py
    ├── improve_description.py
    ├── package_skill.py
    ├── aggregate_benchmark.py
    ├── generate_report.py
    └── utils.py
```

## 首次使用

⚠️ **重要：** 如果是首次使用，应该手动在浏览器运行一次：
- `https://s.trae.com.cn/a/b0c83e?region=cn`
- 或 `https://s.trae.ai/a/a371fd?region=sg`

以确保存在并行智能体。

## LLM配置

如需修改LLM的url、key，请编辑 `config/backend.json` 文件。

Claude Code无需此配置。详见 `config/README.md`。

## 快速开始

### 创建新Skill

1. 理解用户需求并确认
2. 调研Github/skills.sh上的相关skill
3. 创建skill-canvas.md
4. 编写SKILL.md
5. 创建测试用例
6. 运行评测并迭代

### 修改现有Skill

1. 读取现有skill文件
2. 理解改进需求
3. 按上述流程迭代

## 参考文档

- `references/tool-usage-guide.md` - 工具使用指南
- `references/workflow-details.md` - 详细工作流程
- `references/eval-layers.md` - 评测分层定义
- `references/schemas.md` - JSON结构定义

