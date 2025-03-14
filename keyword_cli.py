#!/usr/bin/env python
"""
Google Ads 关键词分析工具 - 命令行版本
直接在终端中运行并获取关键词数据
"""

import sys
import argparse
import json
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
    parser = argparse.ArgumentParser(description='Google Ads 关键词分析工具 - 命令行版本')
    parser.add_argument('keyword', nargs='?', help='要分析的关键词')
    parser.add_argument('-l', '--language', default='1000', help='语言ID (默认: 1000 - 英语)')
    parser.add_argument('-c', '--country', default='2840', help='国家ID (默认: 2840 - 美国)')
    parser.add_argument('-j', '--json', action='store_true', help='以JSON格式输出结果')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('-d', '--debug', action='store_true', help='显示调试级别的日志（比verbose更详细）')
    return parser

def format_output(keyword_data, json_output=False):
    """格式化输出结果"""
    if json_output:
        return json.dumps(keyword_data, ensure_ascii=False, indent=2)
    
    if not keyword_data:
        return "未找到关键词数据"
    
    # 格式化为易读的文本
    output = []
    output.append(f"\n关键词: {keyword_data.get('keyword', 'N/A')}")
    output.append("-" * 50)
    output.append(f"搜索量 (美国): {keyword_data.get('volume_us', 'N/A'):,}")
    output.append(f"搜索量 (全球): {keyword_data.get('volume_global', 'N/A'):,}")
    output.append(f"关键词难度 (KD): {keyword_data.get('kd', 'N/A')}")
    
    # 处理CPC显示
    cpc = keyword_data.get('cpc')
    if cpc is None:
        cpc_display = "数据不可用"
    elif cpc == 0:
        cpc_display = "$0.00"
    else:
        cpc_display = f"${cpc:.2f}"
    output.append(f"CPC: {cpc_display}")
    
    # 关键词类型
    keyword_type = keyword_data.get('type', 'I')
    type_map = {'I': '信息型', 'C': '商业型', 'T': '交易型'}
    output.append(f"关键词类型: {type_map.get(keyword_type, '未知')} ({keyword_type})")
    
    # 竞争度
    competition = keyword_data.get('competition', 'UNSPECIFIED')
    competition_map = {
        'UNSPECIFIED': '未指定',
        'UNKNOWN': '未知',
        'LOW': '低',
        'MEDIUM': '中',
        'HIGH': '高'
    }
    output.append(f"竞争度: {competition_map.get(competition, competition)}")
    output.append(f"竞争指数: {keyword_data.get('competition_index', 'N/A')}")
    
    # 添加原始数据提示
    if keyword_data.get('_debug_info'):
        output.append("\n调试信息:")
        for key, value in keyword_data.get('_debug_info', {}).items():
            output.append(f"  {key}: {value}")
    
    return "\n".join(output)

def interactive_mode():
    """交互模式"""
    print("\n=== Google Ads 关键词分析工具 - 交互模式 ===")
    print("输入关键词进行分析，输入 'q' 或 'exit' 退出\n")
    
    # 初始化Google Ads客户端
    try:
        ads_client = GoogleAdsClient(config.GOOGLE_ADS)
        customer_id = config.GOOGLE_ADS.get('login_customer_id', '')
        
        while True:
            keyword = input("\n请输入关键词 (q 退出): ").strip()
            
            if keyword.lower() in ('q', 'exit', 'quit'):
                print("再见!")
                break
                
            if not keyword:
                continue
                
            print(f"\n正在分析关键词: {keyword}...")
            
            try:
                keyword_data = get_keyword_data(
                    ads_client, 
                    customer_id, 
                    keyword
                )
                
                if keyword_data:
                    print(format_output(keyword_data))
                else:
                    print("未找到关键词数据")
                    
            except Exception as e:
                print(f"分析关键词时出错: {e}")
                
    except Exception as e:
        print(f"初始化Google Ads客户端时出错: {e}")
        return 1
        
    return 0

def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        # 设置ads_api包的日志级别为DEBUG
        logging.getLogger('ads_api').setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    # 如果没有提供关键词，进入交互模式
    if not args.keyword:
        return interactive_mode()
    
    # 初始化Google Ads客户端
    try:
        ads_client = GoogleAdsClient(config.GOOGLE_ADS)
        customer_id = config.GOOGLE_ADS.get('login_customer_id', '')
        
        if not customer_id:
            logger.error("未配置客户ID (login_customer_id)")
            return 1
            
        # 获取关键词数据
        logger.info(f"开始获取关键词数据: {args.keyword}")
        keyword_data = get_keyword_data(
            ads_client, 
            customer_id, 
            args.keyword,
            language_id=args.language,
            location_id=args.country
        )
        
        if keyword_data:
            print(format_output(keyword_data, args.json))
        else:
            print("未找到关键词数据")
            return 1
            
    except Exception as e:
        logger.error(f"分析关键词时出错: {e}")
        if args.verbose or args.debug:
            import traceback
            traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 