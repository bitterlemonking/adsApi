"""
获取Google Ads客户ID
此脚本帮助您获取可用的Google Ads客户ID
"""

import sys
import logging
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """获取Google Ads客户ID"""
    print("=" * 80)
    print("Google Ads 客户ID 获取工具")
    print("=" * 80)
    print("\n此脚本将帮助您获取可用的Google Ads客户ID。")
    print("请确保您已经在config.py中配置了developer_token, client_id, client_secret和refresh_token。\n")
    
    try:
        # 从config.py导入配置
        import config
        
        # 检查必要的配置
        required_keys = ['developer_token', 'client_id', 'client_secret', 'refresh_token']
        for key in required_keys:
            if key not in config.GOOGLE_ADS or not config.GOOGLE_ADS[key] or config.GOOGLE_ADS[key] == f'YOUR_{key.upper()}':
                print(f"错误: 请先在config.py中配置{key}")
                return
        
        # 创建客户端配置
        client_config = {
            "developer_token": config.GOOGLE_ADS['developer_token'],
            "client_id": config.GOOGLE_ADS['client_id'],
            "client_secret": config.GOOGLE_ADS['client_secret'],
            "refresh_token": config.GOOGLE_ADS['refresh_token'],
            "use_proto_plus": config.GOOGLE_ADS.get('use_proto_plus', True),
        }
        
        # 初始化客户端
        client = GoogleAdsClient.load_from_dict(client_config)
        
        # 获取客户服务
        customer_service = client.get_service("CustomerService")
        
        # 获取可访问的客户账户
        accessible_customers = customer_service.list_accessible_customers()
        
        # 打印客户ID
        print(f"\n找到 {len(accessible_customers.resource_names)} 个可访问的客户账户:")
        print("-" * 80)
        
        for i, resource_name in enumerate(accessible_customers.resource_names, 1):
            # 从资源名称中提取客户ID
            customer_id = resource_name.split('/')[-1]
            print(f"{i}. 客户ID: {customer_id}")
            
            # 显示不带破折号的ID (用于config.py)
            customer_id_no_dashes = customer_id.replace("-", "")
            print(f"   配置文件中使用: {customer_id_no_dashes}")
            print("-" * 80)
        
        if accessible_customers.resource_names:
            # 提示用户选择客户ID
            selection = input("\n请选择要使用的客户ID编号 (默认为1): ")
            selection = int(selection) if selection.isdigit() and 1 <= int(selection) <= len(accessible_customers.resource_names) else 1
            
            # 获取选择的客户ID
            selected_resource_name = accessible_customers.resource_names[selection - 1]
            selected_customer_id = selected_resource_name.split('/')[-1]
            selected_customer_id_no_dashes = selected_customer_id.replace("-", "")
            
            print(f"\n您选择了客户ID: {selected_customer_id}")
            print(f"配置文件中使用: {selected_customer_id_no_dashes}")
            
            # 提示更新config.py
            update_config = input("\n是否自动更新config.py文件? (y/n): ").lower()
            if update_config == 'y':
                try:
                    with open('config.py', 'r', encoding='utf-8') as f:
                        config_content = f.read()
                    
                    # 替换login_customer_id
                    config_content = config_content.replace(
                        "'login_customer_id': 'YOUR_CUSTOMER_ID_WITHOUT_DASHES'", 
                        f"'login_customer_id': '{selected_customer_id_no_dashes}'"
                    )
                    
                    with open('config.py', 'w', encoding='utf-8') as f:
                        f.write(config_content)
                    
                    print("config.py文件已更新!")
                except Exception as e:
                    print(f"更新config.py时出错: {e}")
                    print("请手动更新config.py文件。")
        else:
            print("\n未找到可访问的客户账户。请确保您的账户有权限访问Google Ads API。")
        
    except ImportError:
        print("错误: 无法导入config.py，请确保该文件存在。")
    except GoogleAdsException as ex:
        print(f"Google Ads API错误: {ex}")
        for error in ex.failure.errors:
            print(f"\t{error.error_code.message}: {error.message}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    main() 