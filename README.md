# PDF处理Claude技能集合

一套强大的PDF处理工具，专为Claude AI设计，提供从目录提取到文档分析的全方位PDF处理能力。

## 🚀 技能列表

### 1. PDF目录提取器 (pdf-toc-extractor)
从PDF文档中提取目录（书签/大纲）结构，支持文本和JSON格式输出。

**主要功能：**
- 📖 提取PDF目录/大纲结构
- 📝 支持文本格式输出
- 📊 支持JSON格式输出
- 🎯 处理嵌套目录层次
- 🖥️ 提供命令行接口
- 🔧 可作为Python模块使用

**使用方法：**
```bash
# 基本文本输出
python pdf-toc-extractor/scripts/extract_toc.py document.pdf

# JSON格式输出
python pdf-toc-extractor/scripts/extract_toc.py --json document.pdf

# 美化JSON输出
python pdf-toc-extractor/scripts/extract_toc.py --json --pretty document.pdf
```

## 📦 安装

### 快速安装
```bash
# 克隆仓库
git clone <repository-url>
cd pdf-skills

# 安装依赖
pip install -r pdf-toc-extractor/scripts/requirements.txt
```

### Claude Marketplace安装
1. 复制 `marketplace.json`
2. 在Claude中安装技能

## 🛠️ 技术要求

- Python 3.6+
- PyPDF2 >= 3.0.0
- reportlab（用于创建示例PDF）

## 📖 项目结构
```
pdf-skills/
├── README.md              # 本文件
├── marketplace.json       # 技能市场配置
├── pdf-toc-extractor/     # PDF目录提取技能
│   ├── SKILL.md          # 技能详细说明
│   ├── scripts/          # 核心脚本
│   │   ├── extract_toc.py      # 主要提取功能
│   │   ├── create_sample_pdf.py # 示例PDF生成器
│   │   ├── example.py          # 使用示例
│   │   └── test_syntax.py      # 语法检查工具
│   └── references/       # 参考文档
│       └── api_reference.md    # API详细文档
```

## 🔧 开发说明

每个技能都是独立的模块，包含：
- 核心功能脚本
- 示例代码
- 测试工具
- 详细的API文档
- 使用说明

## 🤝 贡献

欢迎提交问题和改进建议！请通过以下方式参与：
1. 提交GitHub Issue
2. 发起Pull Request
3. 分享您的使用经验

## 📄 许可证

MIT License - 详见各技能目录下的LICENSE文件

## 🆘 支持

如有问题，请查看各技能目录中的详细文档：
- `pdf-toc-extractor/SKILL.md` - PDF目录提取器详细说明
- `pdf-toc-extractor/references/api_reference.md` - API参考文档

---

**注意：** 这些技能专为Claude AI设计，但也可以作为独立的Python工具使用。