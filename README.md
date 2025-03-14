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

- 后端：Python + Flask (轻量级Web框架)
- 前端：HTML + CSS + JavaScript (简单直接)
- API：Google Ads API

## 开发流程

1. **环境搭建**
   - 创建项目结构
   - 安装必要依赖 (Python, Flask, Google Ads API Client)
   - 配置Google Ads API认证

2. **API集成**
   - 实现Google Ads API认证流程
   - 开发关键词数据获取接口
   - 处理API响应数据

3. **前端开发**
   - 设计简洁的用户界面
   - 实现关键词输入功能
   - 展示分析结果

4. **数据处理**
   - 解析API返回的数据
   - 计算和分类关键词类型
   - 格式化展示数据

5. **测试与优化**
   - 功能测试
   - 性能优化
   - 用户体验改进

## 项目结构

```
adsApi/                    # 项目根目录
├── app.py                 # Flask应用入口
├── static/                # 静态文件
│   ├── css/               # 样式文件
│   └── js/                # JavaScript文件
├── templates/             # HTML模板
├── ads_api/               # Google Ads API相关代码
│   ├── __init__.py
│   ├── client.py          # API客户端
│   └── keyword_data.py    # 关键词数据处理
├── config.py              # 配置文件
├── requirements.txt       # 项目依赖
└── README.md              # 项目说明
```
