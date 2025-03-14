# Google Ads 关键词分析工具

一个简单实用的关键词分析工具，通过调用Google Ads API获取关键词的核心数据。

## 功能描述

用户输入一个关键词，系统返回以下数据：
- 搜索量（美国和全球）
- 关键词难度(KD)
- 每次点击成本(CPC)
- 关键词类型(I/C/T - 信息型/商业型/交易型)
- 其他相关数据

## 技术栈

- 核心功能：Python + Google Ads API
- 命令行工具：支持单个关键词查询和批量处理

## 使用方法

### 单个关键词查询

```bash
# 交互式模式
python keyword_cli.py

# 直接查询特定关键词
python keyword_cli.py "digital marketing"

# 显示详细日志
python keyword_cli.py -d "seo tools"
```

### 批量关键词处理

```bash
# 处理关键词列表文件
python batch_keywords.py keywords.txt

# 指定输出文件
python batch_keywords.py -o results.csv keywords.txt
```

详细使用说明请参考 [CLI_USAGE.md](CLI_USAGE.md)。

## 开发流程

1. **环境搭建**
   - 创建项目结构
   - 安装必要依赖 (Python, Google Ads API Client)
   - 配置Google Ads API认证

2. **API集成**
   - 实现Google Ads API认证流程
   - 开发关键词数据获取接口
   - 处理API响应数据

3. **数据处理**
   - 解析API返回的数据
   - 计算和分类关键词类型
   - 格式化展示数据

4. **命令行工具开发**
   - 单个关键词查询工具
   - 批量处理工具
   - 结果导出功能

## 安装与配置

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 复制配置文件模板并填写API凭据：
   ```
   cp config.example.py config.py
   ```

3. 编辑`config.py`文件，填入你的Google Ads API凭据。

API设置指南请参考 [API_SETUP.md](API_SETUP.md)。

