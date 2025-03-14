"""
获取Google Ads API的refresh_token
运行此脚本，按照提示在浏览器中授权，获取refresh_token
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import os

# 定义OAuth2的范围
SCOPES = ['https://www.googleapis.com/auth/adwords']

# 从config.py读取客户端配置
try:
    import config
    client_id = config.GOOGLE_ADS['client_id']
    client_secret = config.GOOGLE_ADS['client_secret']
except (ImportError, KeyError):
    # 如果无法从config.py读取，则使用环境变量或默认值
    client_id = os.environ.get('GOOGLE_ADS_CLIENT_ID', 'YOUR_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', 'YOUR_CLIENT_SECRET')

# 客户端配置
CLIENT_CONFIG = {
    'installed': {
        'client_id': client_id,
        'client_secret': client_secret,
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob']
    }
}

def main():
    """运行OAuth2流程并获取refresh_token"""
    print("=" * 80)
    print("Google Ads API Refresh Token 获取工具")
    print("=" * 80)
    print("\n此脚本将帮助您获取Google Ads API所需的refresh_token。")
    print("将会打开浏览器窗口，请按照提示登录您的Google账户并授权。\n")
    
    try:
        # 创建流程
        flow = InstalledAppFlow.from_client_config(
            CLIENT_CONFIG, SCOPES)
        
        # 使用控制台方式获取授权码
        flow.run_console()
        credentials = flow.credentials
        
        # 打印refresh token
        print("\n" + "=" * 80)
        print("成功获取refresh_token!")
        print("=" * 80)
        print(f"\nRefresh Token: {credentials.refresh_token}")
        print("\n请将此token复制到config.py文件中的'refresh_token'字段。")
        
        # 提示更新config.py
        update_config = input("\n是否自动更新config.py文件? (y/n): ").lower()
        if update_config == 'y':
            try:
                with open('config.py', 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # 替换refresh_token
                config_content = config_content.replace(
                    "'refresh_token': 'YOUR_REFRESH_TOKEN'", 
                    f"'refresh_token': '{credentials.refresh_token}'"
                )
                
                with open('config.py', 'w', encoding='utf-8') as f:
                    f.write(config_content)
                
                print("config.py文件已更新!")
            except Exception as e:
                print(f"更新config.py时出错: {e}")
                print("请手动更新config.py文件。")
        
    except Exception as e:
        print(f"获取refresh_token时出错: {e}")
        print("请确保您已正确配置client_id和client_secret。")

if __name__ == '__main__':
    main() 