<<<<<<< HEAD
# AI Personalized Learning Multi-Agent System

一个基于 Flask + MySQL 的 AI 个性化学习多智能体系统，实现了学习画像、艾宾浩斯遗忘机制、多资源生成、学习路径规划、智能答疑和效果评估。

## 核心能力

- 7 维学习画像：知识基础、认知风格、学习目标、知识短板、学习节奏、兴趣方向、易错点
- 艾宾浩斯遗忘机制：按 1/3/7/14 天自动衰减权重并给出复习提醒
- 多智能体协同：画像分析、知识解析、资源生成、路径规划、答疑、评估
- 6 类学习资源：讲义文档、思维导图、题库、教学脚本、代码案例、PPT 课件
- Web 端交互：Bootstrap + Jinja2 页面，支持 Ajax 调用与流式问答
- 日志管理：控制台 + 文件双输出，自动切割归档

## 快速启动

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

- 开发环境可直接使用根目录下的 `.env`
- 如果你要切换到 MySQL，请将 `DATABASE_URL` 修改为：

```env
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/ai_learning_agent?charset=utf8mb4
```

3. 运行项目

```bash
python run.py
```

4. 打开浏览器

```text
http://127.0.0.1:5000
```

## 项目结构

```text
A3_source/
├── app/
│   ├── blueprints/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── static/
│   └── templates/
├── logs/
├── uploads/
├── logger_config.py
├── requirements.txt
└── run.py
```

## 说明

- 默认 `AI_PROVIDER=mock`，不依赖外部模型接口也可以完整演示业务流程
- 配置 `OPENAI_API_KEY` 后，`AIClient` 可以切换到兼容 OpenAI Chat Completions 的接口
- 默认数据库支持 SQLite 快速演示；按照需求文档可无缝切换到 MySQL 8.0
- 项目启动时会自动建表，方便直接体验

=======
# A3_source
基于大模型的个性化资源生成与学习多智能体系统开发
>>>>>>> 8fbfdc0143a4def81ea151ea6ed8cfd3cbf431d4
