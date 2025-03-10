# Poe 机器人爬虫

一个用于爬取和收集 Poe 平台上 AI 机器人数据的工具，包括其详细信息和积分定价。

## 功能

1. 从 Poe 平台获取官方机器人列表并以 JSON 格式保存
2. 收集每个机器人的详细信息
3. 解析积分定价信息
4. 生成 HTML 仪表盘以可视化结果
5. 支持通过 GitHub Actions 进行自动化每日更新

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

1. 运行主程序：

```bash
# 如果已安装为包
poe-crawler

# 或直接运行脚本
python src/main.py
```

2. 查看结果：

   - 机器人列表保存在 `output/json/` 目录中
   - 机器人详情保存在 `output/bots/` 目录中
   - HTML 仪表盘保存在 `output/result/` 目录中

3. 在浏览器中查看 HTML 仪表盘：

```bash
# 如果已安装为包
view-html

# 或直接运行脚本
python view_html.py
```

## 自动化更新

本项目包含一个 GitHub Actions 工作流程，可以在每天 UTC 时间 4:00 自动运行爬虫。工作流程会：

1. 设置 Python 环境
2. 安装依赖
3. 使用存储的凭证运行爬虫
4. 提交并推送任何更改到仓库

设置自动化更新的步骤：

1. 将此仓库推送到 GitHub
2. 前往仓库设置 → Secrets and variables → Actions
3. 添加以下仓库密钥:
   - `POE_P_B`: 您的 Poe p-b cookie 值
   - `POE_P_LAT`: 您的 Poe p-lat cookie 值

GitHub Actions 工作流程将使用这些密钥向 Poe 进行身份验证并运行爬虫，而不会暴露您的凭证。

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
│   ├── html_generator.py # 生成 HTML 仪表盘的函数
│   └── utils.py          # 工具函数
├── beautify_html.py      # 美化 HTML 输出的脚本
├── view_html.py          # 在浏览器中查看结果的脚本
└── output/               # 输出目录
    ├── json/             # 包含机器人列表的 JSON 文件
    ├── bots/             # 包含机器人详情的 JSON 文件
    └── result/           # 生成的 HTML 仪表盘
```

## 开发

安装开发依赖：

```bash
uv pip install -e ".[dev]"
```

代码格式化和检查：

```bash
# 格式化代码
black src/ view_html.py

# 排序导入
isort src/ view_html.py

# 类型检查
mypy src/ view_html.py
```

## 日志

日志保存在 `logs/` 目录中，带有时间戳，提供有关爬虫执行的详细信息。

## 输出文件

爬虫生成以下几种输出文件：

1. `output/json/official_bots_list_YYYY-MM-DD.json` - 初始机器人列表
2. `output/json/official_bots_with_prices_YYYY-MM-DD.json` - 带有定价详情的机器人列表
3. `output/result/bots_YYYY-MM-DD.html` - 显示所有机器人及其详情的 HTML 仪表盘

## 许可证

MIT

## 贡献

欢迎贡献！请随时提交 Pull Request。
