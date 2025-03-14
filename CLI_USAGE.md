# Google Ads 关键词分析工具 - 命令行使用指南

本文档介绍如何使用命令行版本的 Google Ads 关键词分析工具。

## 单个关键词分析工具 (keyword_cli.py)

这个工具允许你直接在命令行中分析单个关键词，或者进入交互模式连续分析多个关键词。

### 基本用法

```bash
# 分析单个关键词
python keyword_cli.py "digital marketing"

# 使用交互模式
python keyword_cli.py
```

### 高级选项

```bash
# 显示帮助信息
python keyword_cli.py -h

# 指定语言和国家
python keyword_cli.py -l 1000 -c 2840 "digital marketing"

# 以JSON格式输出结果
python keyword_cli.py -j "digital marketing"

# 显示详细日志
python keyword_cli.py -v "digital marketing"
```

### 参数说明

- `keyword`: 要分析的关键词
- `-l, --language`: 语言ID (默认: 1000 - 英语)
- `-c, --country`: 国家ID (默认: 2840 - 美国)
- `-j, --json`: 以JSON格式输出结果
- `-v, --verbose`: 显示详细日志

## 批量关键词分析工具 (batch_keywords.py)

这个工具允许你从文件中读取关键词列表，批量获取数据并输出到CSV文件。

### 基本用法

```bash
# 批量处理关键词列表
python batch_keywords.py keywords.txt

# 指定输出文件
python batch_keywords.py -o results.csv keywords.txt
```

### 高级选项

```bash
# 显示帮助信息
python batch_keywords.py -h

# 指定语言和国家
python batch_keywords.py -l 1000 -c 2840 keywords.txt

# 设置请求延迟
python batch_keywords.py -d 2.0 keywords.txt

# 显示详细日志
python batch_keywords.py -v keywords.txt
```

### 参数说明

- `input_file`: 包含关键词列表的输入文件 (每行一个关键词)
- `-o, --output`: 输出CSV文件路径 (默认: keywords_results.csv)
- `-l, --language`: 语言ID (默认: 1000 - 英语)
- `-c, --country`: 国家ID (默认: 2840 - 美国)
- `-d, --delay`: 每个请求之间的延迟秒数 (默认: 1.0)
- `-v, --verbose`: 显示详细日志

## 关键词文件格式

关键词文件是一个简单的文本文件，每行包含一个关键词。以 `#` 开头的行将被视为注释并忽略。

示例 (keywords.txt):
```
# 这是一个注释
digital marketing
seo tools
content writing
```

## 常见问题

### 如何获取不同语言和国家的数据？

Google Ads API 使用数字ID来表示语言和国家。以下是一些常用的ID:

**语言ID:**
- 1000: 英语
- 1002: 法语
- 1003: 德语
- 1004: 意大利语
- 1005: 西班牙语
- 1008: 中文
- 1009: 日语

**国家ID:**
- 2840: 美国
- 2826: 英国
- 2124: 加拿大
- 2036: 澳大利亚
- 2156: 中国
- 2392: 日本
- 2276: 德国
- 2250: 法国

### 如何处理API限制？

Google Ads API 有请求限制。如果你遇到限制问题，可以尝试:

1. 增加请求之间的延迟 (`-d` 参数)
2. 减少批量请求的关键词数量
3. 在不同时间运行批处理 