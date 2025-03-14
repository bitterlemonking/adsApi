"""
Google Ads API 客户端
处理与Google Ads API的认证和连接
"""

import os
from google.ads.googleads.client import GoogleAdsClient as Client
from google.ads.googleads.errors import GoogleAdsException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleAdsClient:
    """Google Ads API客户端封装类"""
    
    def __init__(self, config):
        """
        初始化Google Ads API客户端
        
        Args:
            config: 包含API凭据的配置字典
        """
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化Google Ads API客户端"""
        try:
            # 创建客户端配置字典
            client_config = {
                "developer_token": self.config['developer_token'],
                "client_id": self.config['client_id'],
                "client_secret": self.config['client_secret'],
                "refresh_token": self.config['refresh_token'],
                "use_proto_plus": self.config.get('use_proto_plus', True),
                "version": "v17",  # 明确指定使用v17版本的API
            }
            
            # 如果提供了login_customer_id，则添加到配置中
            if 'login_customer_id' in self.config and self.config['login_customer_id']:
                client_config["login_customer_id"] = self.config['login_customer_id']
            
            # 初始化客户端
            self.client = Client.load_from_dict(client_config)
            logger.info("Google Ads API客户端初始化成功")
            
        except Exception as e:
            logger.error(f"初始化Google Ads API客户端时出错: {e}")
            raise
    
    def get_client(self):
        """
        获取Google Ads API客户端实例
        
        Returns:
            google.ads.googleads.client.GoogleAdsClient: Google Ads API客户端实例
        """
        if not self.client:
            self._initialize_client()
        return self.client
    
    def get_service(self, service_name):
        """
        获取指定的Google Ads API服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            指定的Google Ads API服务
        """
        return self.get_client().get_service(service_name)
    
    def get_type(self, type_name):
        """
        获取指定的Google Ads API类型
        
        Args:
            type_name: 类型名称
            
        Returns:
            指定的Google Ads API类型
        """
        return self.get_client().get_type(type_name)
    
    def execute_query(self, customer_id, query):
        """
        执行GAQL查询
        
        Args:
            customer_id: 客户ID
            query: GAQL查询字符串
            
        Returns:
            查询结果
            
        Raises:
            GoogleAdsException: 如果查询执行失败
        """
        try:
            ga_service = self.get_service("GoogleAdsService")
            search_request = self.get_type("SearchGoogleAdsRequest")
            
            # 设置请求参数
            request = search_request(
                customer_id=customer_id,
                query=query,
            )
            
            # 执行查询
            response = ga_service.search(request=request)
            return response
            
        except GoogleAdsException as ex:
            logger.error(f"执行查询时出错: {ex}")
            for error in ex.failure.errors:
                logger.error(f"\t{error.error_code.message}: {error.message}")
            raise
