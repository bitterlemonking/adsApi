"""
关键词数据处理模块
处理关键词数据的获取和分析
"""

import logging
import traceback
import math
import re
from .client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from config import GOOGLE_ADS

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_keyword_data(client, customer_id, keyword, language_id="1000", location_id="2840"):
    """
    获取关键词数据
    
    Args:
        client: GoogleAdsClient实例
        customer_id: 客户ID
        keyword: 要查询的关键词
        language_id: 语言ID (默认为1000，英语)
        location_id: 位置ID (默认为2840，美国)
        
    Returns:
        dict: 包含关键词数据的字典
    """
    try:
        logger.info(f"开始获取关键词数据: {keyword}, 客户ID: {customer_id}")
        
        # 获取关键词规划服务
        logger.debug("获取关键词规划服务")
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        logger.debug(f"成功获取关键词规划服务: {keyword_plan_idea_service.__class__.__name__}")
        
        # 获取枚举类型
        logger.debug("获取枚举类型")
        keyword_plan_network = client.get_client().enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
        logger.debug(f"成功获取枚举类型: {keyword_plan_network}")
        
        # 创建资源名称
        logger.debug("创建资源名称")
        google_ads_service = client.get_service("GoogleAdsService")
        language_resource_name = google_ads_service.language_constant_path(language_id)
        logger.debug(f"语言资源名称: {language_resource_name}")
        
        geo_target_constant_service = client.get_service("GeoTargetConstantService")
        location_resource_name = geo_target_constant_service.geo_target_constant_path(location_id)
        logger.debug(f"位置资源名称: {location_resource_name}")
        
        # 创建请求 - 特定国家（美国）
        logger.debug("创建美国地区请求")
        us_request = client.get_type("GenerateKeywordIdeasRequest")
        us_request.customer_id = customer_id
        us_request.language = language_resource_name
        us_request.geo_target_constants = [location_resource_name]
        us_request.include_adult_keywords = False
        us_request.keyword_plan_network = keyword_plan_network
        
        # 设置关键词种子
        logger.debug(f"设置关键词种子: {keyword}")
        us_request.keyword_seed.keywords.append(keyword)
        logger.debug(f"成功设置关键词种子")
        
        # 发送美国地区请求
        logger.info("发送美国地区关键词规划请求")
        try:
            logger.debug("调用generate_keyword_ideas方法 (美国)")
            
            # 获取管理者账户ID
            manager_id = GOOGLE_ADS.get('manager_customer_id')
            
            # 创建元数据，添加管理者账户ID作为login-customer-id
            metadata = [
                ("login-customer-id", manager_id)
            ]
            
            logger.debug(f"使用管理者账户ID: {manager_id} 作为login-customer-id")
            logger.debug(f"请求的客户账户ID: {customer_id}")
            
            # 使用元数据发送请求
            us_response = keyword_plan_idea_service.generate_keyword_ideas(
                request=us_request,
                metadata=metadata
            )
            
            logger.info("成功获取美国地区关键词规划数据")
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API错误 (美国请求): {ex}")
            for error in ex.failure.errors:
                logger.error(f"\t{error.error_code}: {error.message}")
            raise
        except Exception as e:
            logger.error(f"调用generate_keyword_ideas方法失败 (美国请求): {e}")
            logger.error(traceback.format_exc())
            raise
        
        # 创建全球请求 - 不指定地理位置
        logger.debug("创建全球请求")
        global_request = client.get_type("GenerateKeywordIdeasRequest")
        global_request.customer_id = customer_id
        global_request.language = language_resource_name
        # 不设置geo_target_constants，以获取全球数据
        global_request.include_adult_keywords = False
        global_request.keyword_plan_network = keyword_plan_network
        global_request.keyword_seed.keywords.append(keyword)
        
        # 发送全球请求
        logger.info("发送全球关键词规划请求")
        try:
            global_response = keyword_plan_idea_service.generate_keyword_ideas(
                request=global_request,
                metadata=metadata
            )
            logger.info("成功获取全球关键词规划数据")
        except Exception as e:
            logger.error(f"获取全球数据失败: {e}")
            logger.warning("将使用美国数据作为全球数据的替代")
            global_response = None
        
        # 处理结果
        keyword_data = {}
        logger.debug(f"处理美国响应结果")
        
        # 处理美国数据
        us_keyword_data = process_response(us_response, keyword)
        
        if us_keyword_data:
            keyword_data = us_keyword_data
            keyword_data['volume_us'] = keyword_data.pop('volume', 0)
            
            # 处理全球数据
            if global_response:
                logger.debug(f"处理全球响应结果")
                global_keyword_data = process_response(global_response, keyword)
                if global_keyword_data:
                    keyword_data['volume_global'] = global_keyword_data.get('volume', 0)
                else:
                    logger.warning("未找到全球数据，使用美国数据作为替代")
                    keyword_data['volume_global'] = keyword_data['volume_us']
            else:
                logger.warning("全球请求失败，使用美国数据作为替代")
                keyword_data['volume_global'] = keyword_data['volume_us']
            
            # 计算关键词难度 (KD)
            if 'competition_index' in keyword_data:
                logger.debug("计算关键词难度")
                keyword_data['kd'] = calculate_keyword_difficulty(
                    keyword_data['competition_index'],
                    keyword_data['volume_us'],
                    keyword_data.get('cpc', 0)
                )
        else:
            logger.warning(f"未找到关键词 '{keyword}' 的数据")
        
        logger.info(f"成功获取关键词数据: {keyword_data}")
        return keyword_data
        
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API错误: {ex}")
        for error in ex.failure.errors:
            logger.error(f"\t{error.error_code}: {error.message}")
        raise
    except Exception as e:
        logger.error(f"获取关键词数据时出错: {e}")
        logger.error(traceback.format_exc())
        raise

def process_response(response, target_keyword):
    """
    处理API响应，提取关键词数据
    
    Args:
        response: API响应
        target_keyword: 目标关键词
        
    Returns:
        dict: 包含关键词数据的字典
    """
    keyword_data = {}
    
    for result in response:
        logger.debug(f"处理结果: {result.text}")
        
        # 添加详细日志，输出API返回的原始数据
        logger.debug(f"API返回的原始数据:")
        logger.debug(f"  - 关键词: {result.text}")
        logger.debug(f"  - 搜索量: {result.keyword_idea_metrics.avg_monthly_searches}")
        
        # 记录CPC相关的详细信息
        logger.debug(f"  - CPC相关数据:")
        logger.debug(f"    - average_cpc_micros: {result.keyword_idea_metrics.average_cpc_micros}")
        logger.debug(f"    - 转换后的CPC(美元): {result.keyword_idea_metrics.average_cpc_micros / 1000000 if result.keyword_idea_metrics.average_cpc_micros else 0}")
        
        # 记录竞争度相关的详细信息
        logger.debug(f"  - 竞争度相关数据:")
        logger.debug(f"    - competition: {result.keyword_idea_metrics.competition.name}")
        logger.debug(f"    - competition_index: {result.keyword_idea_metrics.competition_index}")
        
        if result.text.lower() == target_keyword.lower():
            # 提取数据
            logger.info(f"找到精确匹配的关键词: {result.text}")
            
            # 处理CPC数据
            cpc_micros = result.keyword_idea_metrics.average_cpc_micros
            if cpc_micros and cpc_micros > 0:
                cpc = cpc_micros / 1000000  # 转换为美元
            else:
                cpc = None  # 使用None表示CPC数据不可用
                logger.debug(f"CPC数据不可用 (average_cpc_micros = {cpc_micros})")
            
            keyword_data = {
                'keyword': result.text,
                'volume': result.keyword_idea_metrics.avg_monthly_searches,
                'competition': result.keyword_idea_metrics.competition.name,
                'competition_index': result.keyword_idea_metrics.competition_index,
                'cpc': cpc,
                'type': analyze_keyword_type(result.text)
            }
            break
    
    # 如果没有找到精确匹配的关键词，使用第一个结果
    if not keyword_data and response:
        try:
            result = list(response)[0]
            logger.info(f"未找到精确匹配，使用第一个结果: {result.text}")
            
            # 处理CPC数据
            cpc_micros = result.keyword_idea_metrics.average_cpc_micros
            if cpc_micros and cpc_micros > 0:
                cpc = cpc_micros / 1000000  # 转换为美元
            else:
                cpc = None  # 使用None表示CPC数据不可用
                logger.debug(f"CPC数据不可用 (average_cpc_micros = {cpc_micros})")
            
            keyword_data = {
                'keyword': result.text,
                'volume': result.keyword_idea_metrics.avg_monthly_searches,
                'competition': result.keyword_idea_metrics.competition.name,
                'competition_index': result.keyword_idea_metrics.competition_index,
                'cpc': cpc,
                'type': analyze_keyword_type(result.text)
            }
        except Exception as e:
            logger.error(f"处理第一个结果时出错: {e}")
    
    return keyword_data

def calculate_keyword_difficulty(competition_index, search_volume, cpc):
    """
    计算关键词难度 (KD)
    
    Args:
        competition_index: 竞争指数 (0-100)
        search_volume: 搜索量
        cpc: 每次点击成本
        
    Returns:
        float: 关键词难度 (0-100)
    """
    try:
        logger.debug(f"计算KD: 竞争指数={competition_index}, 搜索量={search_volume}, CPC={cpc}")
        
        # 简单算法：竞争指数 * 0.7 + 搜索量因子 * 0.2 + CPC因子 * 0.1
        
        # 搜索量因子 (0-100)
        volume_factor = min(100, search_volume / 100) if search_volume else 0
        
        # CPC因子 (0-100)
        cpc_factor = min(100, cpc * 20) if cpc else 0
        
        # 计算KD
        kd = (competition_index * 0.7) + (volume_factor * 0.2) + (cpc_factor * 0.1)
        
        logger.debug(f"计算的KD值: {kd}")
        return round(kd, 1)
    except Exception as e:
        logger.error(f"计算关键词难度时出错: {e}")
        return 0

def analyze_keyword_type(keyword):
    """
    分析关键词类型 (信息型/商业型/交易型)
    
    Args:
        keyword: 关键词
        
    Returns:
        str: 关键词类型 (I/C/T)
    """
    try:
        logger.debug(f"分析关键词类型: {keyword}")
        
        # 信息型关键词特征
        informational_indicators = [
            'what', 'how', 'why', 'when', 'where', 'who', 'which', 
            '是什么', '怎么', '为什么', '如何', '教程', '指南', 'guide', 'tutorial'
        ]
        
        # 商业型关键词特征
        commercial_indicators = [
            'best', 'top', 'review', 'compare', 'vs', 'versus', 
            '最好', '推荐', '评测', '对比', '排名', 'ranking'
        ]
        
        # 交易型关键词特征
        transactional_indicators = [
            'buy', 'price', 'cheap', 'discount', 'deal', 'coupon', 'purchase', 'shop', 'order',
            '购买', '价格', '优惠', '折扣', '订购', '下单', '商店'
        ]
        
        # 转换为小写进行比较
        keyword_lower = keyword.lower()
        
        # 检查关键词类型
        for indicator in transactional_indicators:
            if indicator in keyword_lower:
                logger.debug(f"关键词 '{keyword}' 被识别为交易型 (T)")
                return 'T'  # 交易型
                
        for indicator in commercial_indicators:
            if indicator in keyword_lower:
                logger.debug(f"关键词 '{keyword}' 被识别为商业型 (C)")
                return 'C'  # 商业型
                
        for indicator in informational_indicators:
            if indicator in keyword_lower:
                logger.debug(f"关键词 '{keyword}' 被识别为信息型 (I)")
                return 'I'  # 信息型
        
        # 默认为信息型
        logger.debug(f"关键词 '{keyword}' 默认识别为信息型 (I)")
        return 'I'
    except Exception as e:
        logger.error(f"分析关键词类型时出错: {e}")
        return 'I'  # 默认为信息型
