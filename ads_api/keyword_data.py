"""
关键词数据处理模块
处理关键词数据的获取和分析
"""

import logging
import traceback
from .client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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
        keyword_plan_network_enum = client.get_type("KeywordPlanNetworkEnum")
        keyword_plan_network = keyword_plan_network_enum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS
        logger.debug(f"成功获取枚举类型: {keyword_plan_network}")
        
        # 创建关键词种子
        logger.debug(f"创建关键词种子: {keyword}")
        keyword_seed = client.get_type("KeywordSeed")
        keyword_seed.keywords.append(keyword)
        logger.debug(f"成功创建关键词种子: {keyword_seed}")
        
        # 创建请求
        logger.debug("创建请求")
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = language_id
        request.geo_target_constants.append(location_id)
        request.include_adult_keywords = False
        request.keyword_plan_network = keyword_plan_network
        request.keyword_seed = keyword_seed
        logger.debug(f"成功创建请求: {request}")
        
        # 发送请求
        logger.info("发送关键词规划请求")
        try:
            # 在v17版本中，generate_keyword_ideas方法的参数可能有所不同
            # 尝试直接传递请求对象
            logger.debug("尝试调用generate_keyword_ideas方法")
            response = keyword_plan_idea_service.generate_keyword_ideas(request)
            logger.info("成功接收关键词规划响应")
        except TypeError as e:
            # 如果参数不匹配，尝试使用命名参数
            logger.warning(f"使用请求对象调用失败: {e}，尝试使用命名参数")
            response = keyword_plan_idea_service.generate_keyword_ideas(
                customer_id=customer_id,
                language=language_id,
                geo_target_constants=[location_id],
                include_adult_keywords=False,
                keyword_plan_network=keyword_plan_network,
                keyword_seed=keyword_seed
            )
            logger.info("使用命名参数成功接收关键词规划响应")
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API错误: {ex}")
            for error in ex.failure.errors:
                logger.error(f"\t{error.error_code.message}: {error.message}")
            raise
        
        # 处理结果
        keyword_data = {}
        logger.debug(f"处理响应结果，结果数量: {len(list(response.results))}")
        
        for result in response.results:
            logger.debug(f"处理结果: {result.text}")
            if result.text.lower() == keyword.lower():
                # 提取数据
                logger.info(f"找到精确匹配的关键词: {result.text}")
                keyword_data = {
                    'keyword': result.text,
                    'volume_us': result.keyword_idea_metrics.avg_monthly_searches,
                    'volume_global': result.keyword_idea_metrics.avg_monthly_searches,  # 需要另一个请求获取全球数据
                    'competition': result.keyword_idea_metrics.competition.name,
                    'competition_index': result.keyword_idea_metrics.competition_index,
                    'cpc': result.keyword_idea_metrics.average_cpc_micros / 1000000,  # 转换为美元
                    'type': analyze_keyword_type(result.text)
                }
                break
        
        # 如果没有找到精确匹配的关键词，使用第一个结果
        if not keyword_data and response.results:
            result = response.results[0]
            logger.info(f"未找到精确匹配，使用第一个结果: {result.text}")
            keyword_data = {
                'keyword': result.text,
                'volume_us': result.keyword_idea_metrics.avg_monthly_searches,
                'volume_global': result.keyword_idea_metrics.avg_monthly_searches,
                'competition': result.keyword_idea_metrics.competition.name,
                'competition_index': result.keyword_idea_metrics.competition_index,
                'cpc': result.keyword_idea_metrics.average_cpc_micros / 1000000,
                'type': analyze_keyword_type(result.text)
            }
        
        # 计算关键词难度 (KD)
        if 'competition_index' in keyword_data:
            logger.debug("计算关键词难度")
            keyword_data['kd'] = calculate_keyword_difficulty(
                keyword_data['competition_index'],
                keyword_data['volume_us'],
                keyword_data['cpc']
            )
        
        logger.info(f"成功获取关键词数据: {keyword_data}")
        return keyword_data
        
    except GoogleAdsException as ex:
        logger.error(f"Google Ads API错误: {ex}")
        for error in ex.failure.errors:
            logger.error(f"\t{error.error_code.message}: {error.message}")
        raise
    except Exception as e:
        logger.error(f"获取关键词数据时出错: {e}")
        logger.error(traceback.format_exc())
        raise

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
