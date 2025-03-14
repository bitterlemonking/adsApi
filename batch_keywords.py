#!/usr/bin/env python
"""
Google Ads 关键词分析工具 - 批量处理版本
从文件中读取关键词列表，批量获取数据并输出到CSV文件
"""

import sys
import os
import csv
import time
import argparse
import logging
from ads_api import GoogleAdsClient, get_keyword_data
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_argparse():
    """设置命令行参数解析"""
    parser = argparse.ArgumentParser(description='Google Ads 关键词分析工具 - 批量处理版本')
    parser.add_argument('input_file', help='包含关键词列表的输入文件 (每行一个关键词)')
    parser.add_argument('-o', '--output', help='输出CSV文件路径 (默认: keywords_results.csv)')
    parser.add_argument('-l', '--language', default='1000', help='语言ID (默认: 1000 - 英语)')
    parser.add_argument('-c', '--country', default='2840', help='国家ID (默认: 2840 - 美国)')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='每个请求之间的延迟秒数 (默认: 1.0)')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    return parser

def read_keywords(file_path):
    """从文件中读取关键词列表"""
    keywords = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                keyword = line.strip()
                if keyword and not keyword.startswith('#'):
                    keywords.append(keyword)
        return keywords
    except Exception as e:
        logger.error(f"读取关键词文件时出错: {e}")
        return []

def write_csv_header(file_path):
    """写入CSV文件头"""
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                '关键词',
                '搜索量(美国)',
                '搜索量(全球)',
                '关键词难度(KD)',
                'CPC($)',
                '关键词类型',
                '竞争度',
                '竞争指数'
            ])
        return True
    except Exception as e:
        logger.error(f"创建CSV文件时出错: {e}")
        return False

def append_to_csv(file_path, keyword_data):
    """将关键词数据追加到CSV文件"""
    try:
        # 关键词类型映射
        type_map = {'I': '信息型', 'C': '商业型', 'T': '交易型'}
        
        # 竞争度映射
        competition_map = {
            'UNSPECIFIED': '未指定',
            'UNKNOWN': '未知',
            'LOW': '低',
            'MEDIUM': '中',
            'HIGH': '高'
        }
        
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                keyword_data.get('keyword', 'N/A'),
                keyword_data.get('volume_us', 'N/A'),
                keyword_data.get('volume_global', 'N/A'),
                keyword_data.get('kd', 'N/A'),
                f"{keyword_data.get('cpc', 0):.2f}",
                f"{type_map.get(keyword_data.get('type', 'I'), '未知')}",
                f"{competition_map.get(keyword_data.get('competition', 'UNKNOWN'), '未知')}",
                keyword_data.get('competition_index', 'N/A')
            ])
        return True
    except Exception as e:
        logger.error(f"写入CSV文件时出错: {e}")
        return False

def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # 检查输入文件
    if not os.path.exists(args.input_file):
        logger.error(f"输入文件不存在: {args.input_file}")
        return 1
    
    # 设置输出文件
    output_file = args.output or 'keywords_results.csv'
    
    # 读取关键词列表
    keywords = read_keywords(args.input_file)
    if not keywords:
        logger.error("没有找到有效的关键词")
        return 1
    
    logger.info(f"读取了 {len(keywords)} 个关键词")
    
    # 初始化Google Ads客户端
    try:
        ads_client = GoogleAdsClient(config.GOOGLE_ADS)
        customer_id = config.GOOGLE_ADS.get('login_customer_id', '')
        
        if not customer_id:
            logger.error("未配置客户ID (login_customer_id)")
            return 1
        
        # 创建CSV文件并写入表头
        if not write_csv_header(output_file):
            return 1
        
        # 处理每个关键词
        success_count = 0
        for i, keyword in enumerate(keywords):
            logger.info(f"处理关键词 [{i+1}/{len(keywords)}]: {keyword}")
            
            try:
                # 获取关键词数据
                keyword_data = get_keyword_data(
                    ads_client, 
                    customer_id, 
                    keyword,
                    language_id=args.language,
                    location_id=args.country
                )
                
                if keyword_data:
                    # 将数据写入CSV
                    if append_to_csv(output_file, keyword_data):
                        success_count += 1
                        logger.info(f"成功获取关键词数据: {keyword}")
                    else:
                        logger.warning(f"写入CSV失败: {keyword}")
                else:
                    logger.warning(f"未找到关键词数据: {keyword}")
                
                # 添加延迟，避免请求过快
                if i < len(keywords) - 1 and args.delay > 0:
                    time.sleep(args.delay)
                    
            except Exception as e:
                logger.error(f"处理关键词时出错: {keyword} - {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
        
        logger.info(f"批量处理完成。成功: {success_count}/{len(keywords)}")
        logger.info(f"结果已保存到: {output_file}")
        
    except Exception as e:
        logger.error(f"初始化Google Ads客户端时出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 