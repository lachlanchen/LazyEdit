<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p>
  <b>Languages:</b>
  <a href="../README.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# LazyEdit

LazyEdit 是一款 AI 驱动的自动视频剪辑工具，可为视频自动生成专业级字幕、重点高亮、单词卡和元数据，利用先进 AI 技术简化繁琐的编辑流程。

## 功能特色

- **自动转录**：使用 AI 自动转录视频音频
- **自动画面描述**：为视频内容生成描述性字幕
- **自动字幕**：直接生成并烧录字幕
- **自动高亮**：识别并高亮播放中的关键词
- **自动元数据**：从视频内容提取并生成元数据
- **单词卡**：添加用于语言学习的单词卡
- **预告片生成**：通过重复关键片段生成精华预告
- **多语言支持**：支持多种语言（含英文与中文）
- **封面生成**：提取最佳封面并添加文字叠加

## 安装

### 先决条件

- Python 3.10 或更高
- FFmpeg
- 支持 CUDA 的 GPU（用于转录加速）
- Conda 环境管理器

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. 运行安装脚本：
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

安装脚本将：
- 安装所需系统包（ffmpeg、tmux）
- 创建并配置名为 "lazyedit" 的 conda 环境
- 设置 systemd 服务以自动启动
- 配置必要权限

## 使用方式

LazyEdit 以 Web 应用运行，可在 http://localhost:8081 访问。

### 处理视频

1. 通过 Web 界面上传视频
2. LazyEdit 将自动：
   - 转录并生成画面描述
   - 生成元数据与学习内容
   - 生成识别语言的字幕
   - 高亮重要词汇
   - 生成预告片
   - 生成封面图
   - 打包并返回处理结果

### 命令行使用

也可直接运行 LazyEdit：

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## 项目结构

- `app.py` - 主应用入口
- `lazyedit/` - 核心模块目录
  - `autocut_processor.py` - 视频分段与转录
  - `subtitle_metadata.py` - 由字幕生成元数据
  - `subtitle_translate.py` - 字幕翻译
  - `video_captioner.py` - 生成视频画面描述
  - `words_card.py` - 生成单词卡
  - `utils.py` - 工具函数
  - `openai_version_check.py` - OpenAI API 兼容层

## 配置

systemd 服务配置位于 `/etc/systemd/system/lazyedit.service`。

LazyEdit 使用名为 "lazyedit" 的 tmux 会话运行，便于在后台持续运行。

## 服务管理

- 启动服务：`sudo systemctl start lazyedit.service`
- 停止服务：`sudo systemctl stop lazyedit.service`
- 查看状态：`sudo systemctl status lazyedit.service`
- 查看日志：`sudo journalctl -u lazyedit.service`

## 高级使用

LazyEdit 支持以下定制：
- 预告片长度与位置
- 单词高亮样式
- 字幕字体与位置
- 输出目录结构
- GPU 选择

## 故障排查

- 如果应用无法启动，请检查 systemd 状态和日志
- 如果视频处理失败，请确认 FFmpeg 正确安装
- GPU 相关问题请确认 CUDA 与 GPU 可用
- 确认 conda 环境已正确激活

## 许可证

[请在此填写许可证]

## 致谢

LazyEdit 使用以下开源库与工具：
- FFmpeg 用于视频处理
- OpenAI 模型提供 AI 能力
- Tornado Web 框架
- MoviePy 视频编辑
- CJKWrap 多语言排版
