"""
Google Ads 关键词分析工具
Flask应用入口文件
"""

from flask import Flask, render_template, request, jsonify
import logging
import os
import traceback
from ads_api import GoogleAdsClient, get_keyword_data
import config

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config)

# 初始化Google Ads客户端
ads_client = None

def init_ads_client():
    """初始化Google Ads客户端"""
    global ads_client
    try:
        logger.info("开始初始化Google Ads客户端")
        ads_client = GoogleAdsClient(config.GOOGLE_ADS)
        logger.info("Google Ads客户端初始化成功")
        return True
    except Exception as e:
        logger.error(f"初始化Google Ads客户端失败: {e}")
        logger.error(traceback.format_exc())
        return False

@app.route('/')
def index():
    """首页路由"""
    logger.info("访问首页")
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析关键词路由"""
    logger.info("收到分析关键词请求")
    
    # 获取表单数据
    keyword = request.form.get('keyword', '')
    logger.info(f"分析关键词: {keyword}")
    
    if not keyword:
        logger.warning("未提供关键词")
        return jsonify({
            'success': False,
            'error': '请输入关键词'
        })
    
    # 确保Google Ads客户端已初始化
    global ads_client
    if not ads_client:
        logger.info("Google Ads客户端未初始化，尝试初始化")
        success = init_ads_client()
        if not success:
            logger.error("Google Ads客户端初始化失败")
            return jsonify({
                'success': False,
                'error': 'Google Ads API客户端初始化失败，请检查配置'
            })
    
    try:
        # 获取关键词数据
        customer_id = config.GOOGLE_ADS.get('login_customer_id', '')
        logger.info(f"使用客户ID: {customer_id}")
        
        if not customer_id:
            logger.error("未配置客户ID")
            return jsonify({
                'success': False,
                'error': '未配置客户ID (login_customer_id)'
            })
        
        # 获取关键词数据
        logger.info(f"开始获取关键词数据: {keyword}")
        keyword_data = get_keyword_data(
            ads_client, 
            customer_id, 
            keyword
        )
        logger.info(f"成功获取关键词数据: {keyword_data}")
        
        if not keyword_data:
            logger.warning("未找到关键词数据")
            return jsonify({
                'success': False,
                'error': '未找到关键词数据'
            })
        
        # 返回结果
        logger.info("返回关键词数据")
        return jsonify({
            'success': True,
            'data': keyword_data
        })
        
    except Exception as e:
        logger.error(f"分析关键词时出错: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'分析关键词时出错: {str(e)}'
        })

@app.route('/api/keyword', methods=['GET'])
def api_keyword():
    """API路由，用于获取关键词数据"""
    logger.info("收到API关键词请求")
    
    # 获取查询参数
    keyword = request.args.get('q', '')
    logger.info(f"API查询关键词: {keyword}")
    
    if not keyword:
        logger.warning("API请求未提供关键词")
        return jsonify({
            'success': False,
            'error': '请提供关键词参数 (q)'
        })
    
    # 确保Google Ads客户端已初始化
    global ads_client
    if not ads_client:
        logger.info("API请求: Google Ads客户端未初始化，尝试初始化")
        success = init_ads_client()
        if not success:
            logger.error("API请求: Google Ads客户端初始化失败")
            return jsonify({
                'success': False,
                'error': 'Google Ads API客户端初始化失败，请检查配置'
            })
    
    try:
        # 获取关键词数据
        customer_id = config.GOOGLE_ADS.get('login_customer_id', '')
        logger.info(f"API请求使用客户ID: {customer_id}")
        
        if not customer_id:
            logger.error("API请求: 未配置客户ID")
            return jsonify({
                'success': False,
                'error': '未配置客户ID (login_customer_id)'
            })
        
        # 获取关键词数据
        logger.info(f"API请求: 开始获取关键词数据: {keyword}")
        keyword_data = get_keyword_data(
            ads_client, 
            customer_id, 
            keyword
        )
        logger.info(f"API请求: 成功获取关键词数据: {keyword_data}")
        
        if not keyword_data:
            logger.warning("API请求: 未找到关键词数据")
            return jsonify({
                'success': False,
                'error': '未找到关键词数据'
            })
        
        # 返回结果
        logger.info("API请求: 返回关键词数据")
        return jsonify({
            'success': True,
            'data': keyword_data
        })
        
    except Exception as e:
        logger.error(f"API请求: 获取关键词数据时出错: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'获取关键词数据时出错: {str(e)}'
        })

if __name__ == '__main__':
    # 初始化Google Ads客户端
    init_ads_client()
    
    # 运行Flask应用
    app.run(host='0.0.0.0', port=5001, debug=config.DEBUG)
