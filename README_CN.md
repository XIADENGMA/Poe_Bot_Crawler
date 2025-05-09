# Poe 机器人爬虫

一个用于爬取和收集 Poe 平台上 AI 机器人数据的工具，包括其详细信息和积分定价。

## TODO

- [ ] 添加各种机器人价格解析（图片生成、视频生成等）

## 功能

1. 从 Poe 平台获取官方机器人列表并以 JSON 格式保存
2. 收集每个机器人的详细信息
3. 解析积分定价信息
4. 生成 HTML 仪表盘以可视化结果
5. 创建时间线可视化，以跟踪机器人定价和可用性的变化
6. 支持通过 GitHub Actions 进行自动化每日更新
7. 自动将 HTML 文件归档到历史目录
8. 将最新的 HTML 文件作为 index.html 和 timeline.html 维护
9. 通过清理 7 天以上的旧文件进行数据管理

## 系统要求

- Python 3.10 或更高版本
- `uv` 包管理器（推荐）或 pip

## 安装

本项目使用 `uv` 进行包管理：

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
# .venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -e .
```

## 配置

1. 在项目根目录创建一个 `.env` 文件，内容如下：

```
P_B=your_p-b_cookie
P_LAT=your_p-lat_cookie
```

> **注意**：您需要通过网页浏览器登录 Poe 账户并检查 cookies 来获取这些值。

## 使用方法

### 完整工作流程

该项目的典型工作流程包括三个主要步骤：

1. **数据爬取**：运行主爬虫程序从 Poe 获取机器人数据
2. **HTML 生成**：爬虫自动生成 HTML 仪表盘
3. **维护**：运行维护任务管理文件并保持仪表盘更新

#### 步骤 1：运行爬虫

```bash
# 直接运行爬虫脚本
python src/main.py
```

这将会：

- 从 Poe 获取官方机器人列表
- 收集每个机器人的详细信息
- 解析价格信息
- 在 `output/result/history/` 目录中生成 HTML 仪表盘
- 创建时间线可视化，以跟踪机器人和定价的变化
- 将仪表盘复制到 `output/result/index.html` 和 `output/result/timeline.html`
- 清理超过 7 天的旧文件
- 输出生成文件的路径

#### 步骤 2：查看结果

导航到输出目录并在浏览器中打开 HTML 文件：

```bash
# Linux/macOS
open output/result/index.html
open output/result/timeline.html

# Windows
start output/result/index.html
start output/result/timeline.html
```

或者，您可以直接在您喜欢的网页浏览器中打开这些文件。

#### 步骤 3：手动维护（如需要）

如果您需要手动更新 index.html 文件或清理旧文件：

```bash
# 运行所有维护任务
python src/maintenance.py

# 或运行特定任务
python src/maintenance.py --update-index
python src/maintenance.py --clean-old-files
python src/maintenance.py --clean-old-files --days 14
```

### 查看结果

- 机器人列表保存在 `output/json/` 目录中
- 机器人详情保存在 `output/bots/` 目录中
- HTML 仪表盘保存在 `output/result/history/` 目录中
- 时间线可视化保存在 `output/result/timeline/` 目录中
- 最新的 HTML 仪表盘可通过 `output/result/index.html` 访问
- 最新的时间线可视化可通过 `output/result/timeline.html` 访问

## 自动化更新

本项目包含一个 GitHub Actions 工作流程，可以在每天 UTC 时间 4:00 自动运行爬虫。工作流程会：

1. 设置 Python 环境
2. 安装依赖
3. 使用存储的凭证运行爬虫
4. 提交并推送任何更改到仓库
5. 上传构建产物，可以从 GitHub Actions 界面下载

设置自动化更新的步骤：

1. 将此仓库推送到 GitHub
2. 前往仓库设置 → Secrets and variables → Actions
3. 添加以下仓库密钥:
   - `P_B`: 您的 Poe p-b cookie 值
   - `P_LAT`: 您的 Poe p-lat cookie 值

GitHub Actions 工作流程将使用这些密钥向 Poe 进行身份验证并运行爬虫，而不会暴露您的凭证。每次工作流运行还会生成包含输出文件和日志的可下载构建产物，这些产物会保留 30 天。

## 项目结构

```
Poe_crawler/
├── README.md             # 项目文档（英文）
├── README_CN.md          # 项目文档（中文）
├── pyproject.toml        # 项目配置和依赖
├── .env                  # 环境变量（不包含在版本控制中）
├── src/                  # 源代码目录
│   ├── __init__.py       # 包初始化文件
│   ├── main.py           # 主程序入口
│   ├── bot_list.py       # 获取机器人列表的函数
│   ├── bot_details.py    # 获取机器人详情的函数
│   ├── bot_info_generator.py # 生成 HTML 仪表盘的函数
│   ├── timeline_generator.py # 生成时间线可视化的函数
│   ├── maintenance.py    # 维护工具
│   └── utils.py          # 工具函数
└── output/               # 输出目录
    ├── json/             # 包含机器人列表的 JSON 文件
    ├── bots/             # 包含机器人详情的 JSON 文件
    └── result/           # 生成的 HTML 仪表盘
        ├── index.html    # 最新的 HTML 仪表盘
        ├── timeline.html # 最新的时间线可视化
        ├── timeline/     # 历史时间线文件存档
        └── history/      # 历史 HTML 文件存档
```

## 开发

安装开发依赖：

```bash
uv pip install -e ".[dev]"
```

代码格式化和检查：

```bash
# 格式化代码
black src/

# 排序导入
isort src/

# 类型检查
mypy src/
```

## 日志

日志保存在 `logs/` 目录中，带有时间戳，提供有关爬虫执行的详细信息。

## 输出文件

爬虫生成以下几种输出文件：

1. `output/json/official_bots_list_YYYY-MM-DD.json` - 初始机器人列表
2. `output/json/official_bots_with_prices_YYYY-MM-DD.json` - 带有定价详情的机器人列表
3. `output/result/history/bots_YYYY-MM-DD.html` - 显示所有机器人及其详情的 HTML 仪表盘
4. `output/result/timeline/timeline_YYYY-MM-DD.html` - 显示机器人和定价变化的时间线可视化
5. `output/result/index.html` - 最新 HTML 仪表盘的副本
6. `output/result/timeline.html` - 最新时间线可视化的副本

## 许可证

MIT

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 数据管理

爬虫自动管理历史数据：

1. HTML 文件保存到 `output/result/history/` 目录
2. 时间线文件保存到 `output/result/timeline/` 目录
3. 最新的 HTML 文件会被复制为 `output/result/index.html`
4. 最新的时间线文件会被复制为 `output/result/timeline.html`
5. 超过 7 天的文件会从以下目录自动清理：
   - `output/json/`
   - `output/result/history/`
   - `output/result/timeline/`
   - `output/bots/`
   - `logs/`

您可以使用维护脚本手动管理数据：

```bash
python src/maintenance.py
```
