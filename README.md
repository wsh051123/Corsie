
## 项目简介

Corsie 是一个基于 PyQt6 开发的现代化 AI 对话应用程序，提供简洁直观的用户界面和强大的 AI 对话功能。该应用支持多种主流 AI 服务提供商，包括 DeepSeek 和 OpenRouter，能够满足不同用户的 AI 对话需求。

## 核心特性

### 界面设计
- 现代化的用户界面设计，采用现代化设计语言风格
- 响应式布局，支持窗口大小调整
- 自定义主题系统，提供统一的视觉体验
- 优雅的消息气泡设计，区分用户和 AI 消息

### AI 服务支持
- **DeepSeek API 集成**：支持 deepseek-chat 和 deepseek-reasoner 模型
- **OpenRouter API 集成**：支持多种主流模型，包括 Claude、GPT、Gemini 等
- 流式响应支持，实时显示 AI 回复内容
- 智能错误处理和重试机制

### 会话管理
- 多会话并行管理，支持无限数量的对话会话
- 自动会话标题生成，基于对话内容智能命名
- 会话历史持久化存储，数据安全可靠
- 会话导出功能，支持 Markdown 格式导出

### 用户体验
- 实时消息渲染，支持 Markdown 格式显示
- 代码高亮显示，支持多种编程语言
- 消息时间戳显示，便于查看对话历史
- 智能输入框状态管理，防止重复发送

## 技术架构

### 项目结构
```
Corsie/
├── main.py                 # 应用程序主入口
├── requirements.txt        # 项目依赖声明
├── README.md              # 项目文档
├── core/                  # 核心业务逻辑
│   ├── __init__.py
│   ├── ai_client.py       # AI 客户端抽象层
│   ├── config_manager.py  # 配置管理器
│   ├── database.py        # 数据库操作层
│   └── session_manager.py # 会话管理器
├── gui/                   # 图形用户界面
│   ├── __init__.py
│   ├── main_window.py     # 主窗口
│   ├── chat_widget.py     # 聊天界面组件
│   ├── session_panel.py   # 会话面板组件
│   ├── settings_dialog.py # 设置对话框
│   ├── styles/            # 样式主题
│   │   ├── __init__.py
│   │   └── modern_theme.py
│   └── widgets/           # 自定义组件
│       ├── __init__.py
│       └── message_bubble.py
└── icon/                  # 应用程序图标
    └── ...
```

### 技术栈
- **GUI 框架**：PyQt6 - 跨平台桌面应用程序开发
- **Markdown 渲染**：QMarkdownWidget - 富文本消息显示
- **HTTP 客户端**：requests, openai - API 通信
- **数据存储**：SQLite - 轻量级数据库
- **配置管理**：YAML, python-dotenv - 配置文件处理
- **加密支持**：cryptography - 敏感数据保护

## 系统要求

### 最低系统要求
- **操作系统**：Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python 版本**：Python 3.8 或更高版本
- **内存**：4GB RAM 推荐
- **存储空间**：200MB 可用磁盘空间

### 依赖软件
- Python 3.8+
- pip 包管理器

## 安装指南

### 1. 环境准备
确保系统已安装 Python 3.8 或更高版本：
```bash
python --version
```

### 2. 克隆项目
```bash
git clone https://github.com/wsh051123/Corsie.git
cd Corsie
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置 API 密钥
在首次运行应用程序后，通过设置菜单配置您的 AI 服务 API 密钥：
- DeepSeek API 密钥：从 [DeepSeek 官网](https://platform.deepseek.com/api_keys) 获取
- OpenRouter API 密钥：从 [OpenRouter 官网](https://openrouter.ai/settings/keys) 获取

### 5. 启动应用
```bash
python main.py
```

## 使用说明

### 基本操作

#### 开始新对话
1. 启动应用程序后，系统会自动创建一个新的对话会话
2. 在输入框中输入您的问题或指令
3. 按 Ctrl+Enter 键或点击发送按钮发送消息
4. AI 将实时返回回复内容

#### 管理会话
- **创建新会话**：点击左侧面板的"新建对话"按钮
- **切换会话**：点击左侧会话列表中的任意会话
- **重命名会话**：右键点击会话，选择"重命名"
- **删除会话**：右键点击会话，选择"删除"
- **导出会话**：右键点击会话，选择"导出为 Markdown"

#### 设置配置
1. 点击菜单栏的"设置"按钮
2. 在 API 设置页面配置您的 API 密钥
3. 点击"确定"保存设置

### 高级功能

#### 模型切换
- 使用主窗口顶部的模型选择下拉菜单
- 支持的模型包括：
  - DeepSeek Chat / DeepSeek Reasoner
  - Claude Sonnet 4 / Claude 3.7 Sonnet
  - GPT-4o Latest
  - Gemini 2.5 Pro Preview
  - Grok 3

#### Markdown 支持
应用程序完整支持 Markdown 语法渲染，包括：
- 标题和段落格式
- 粗体、斜体、删除线
- 代码块和行内代码
- 列表和表格
- 链接和图片引用

#### 快捷键
- **Ctrl+N**：创建新会话
- **Ctrl+,**：打开设置
- **Ctrl+B**: 切换侧边栏
- **Enter**：发送消息
- **Esc**: 中断AI回复

## 配置说明

### 配置文件位置
- **Windows**：`%APPDATA%\Corsie\config.yaml`
- **macOS**：`~/Library/Application Support/Corsie/config.yaml`
- **Linux**：`~/.config/Corsie/config.yaml`

### 配置文件结构
```yaml
api_keys:
  deepseek: "your-deepseek-api-key"
  openrouter: "your-openrouter-api-key"

ai_settings:
  default_model: "deepseek/deepseek-chat"
  temperature: 0.7
  max_tokens: 2048
  stream_response: true

session_settings:
  auto_save: true
  auto_rename: true
```

## 故障排除

### 常见问题

#### 1. 无法连接到 AI 服务
**问题**：显示连接错误或网络超时
**解决方案**：
- 检查网络连接状态
- 验证 API 密钥是否正确配置
- 确认 API 服务状态是否正常

#### 2. 消息发送失败
**问题**：点击发送按钮后没有反应
**解决方案**：
- 确保已正确配置 API 密钥
- 检查输入内容是否为空
- 查看是否有其他对话正在进行中

#### 3. 界面显示异常
**问题**：界面布局错乱或组件显示不正常
**解决方案**：
- 重启应用程序
- 检查 PyQt6 是否正确安装
- 更新显卡驱动程序

### 错误日志
应用程序运行时的错误信息会显示在控制台中。如需详细调试信息，请使用以下命令启动：
```bash
python main.py --debug
```

## 许可证

本项目采用 MIT 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

## 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请联系我。
