# Google Ads API 配置指南

本文档提供了配置Google Ads API所需的步骤和说明。

## 配置步骤

### 1. 获取开发者令牌 (Developer Token)

1. 登录您的[Google Ads账户](https://ads.google.com/)
2. 确保您有管理员权限
3. 访问API中心：右上角工具图标 → 设置 → API中心
4. 申请开发者令牌
5. 将获得的令牌填入`config.py`的`developer_token`字段

### 2. 创建OAuth凭据 (Client ID 和 Client Secret)

1. 访问[Google Cloud Console](https://console.cloud.google.com/)
2. 创建一个新项目或选择现有项目
3. 启用Google Ads API：API和服务 → 库 → 搜索"Google Ads API" → 启用
4. 配置OAuth同意屏幕：API和服务 → OAuth同意屏幕
   - 用户类型：外部
   - 填写应用信息
   - 添加范围：`.../auth/adwords`
   - 添加测试用户
5. 创建OAuth客户端ID：API和服务 → 凭据 → 创建凭据 → OAuth客户端ID
   - 应用类型：Web应用或桌面应用
   - 名称：自定义名称
   - 重定向URI：`http://localhost:8080`（如果是Web应用）
6. 记下客户端ID和客户端密钥
7. 将这些值填入`config.py`的`client_id`和`client_secret`字段

### 3. 获取刷新令牌 (Refresh Token)

1. 确保已安装必要的Python库：
   ```
   pip install google-auth-oauthlib
   ```

2. 运行提供的脚本获取refresh_token：
   ```
   python get_refresh_token.py
   ```

3. 按照提示在浏览器中授权
4. 将获得的refresh_token填入`config.py`的`refresh_token`字段

### 4. 获取客户ID (Customer ID)

1. 确保已完成前三步并正确配置
2. 运行提供的脚本获取客户ID：
   ```
   python get_customer_id.py
   ```

3. 选择要使用的客户ID
4. 将不带破折号的客户ID填入`config.py`的`login_customer_id`字段

## 配置文件示例

```python
# Google Ads API配置
GOOGLE_ADS = {
    'developer_token': 'YOUR_DEVELOPER_TOKEN',
    'client_id': 'YOUR_CLIENT_ID.apps.googleusercontent.com',
    'client_secret': 'YOUR_CLIENT_SECRET',
    'refresh_token': 'YOUR_REFRESH_TOKEN',
    'login_customer_id': 'YOUR_CUSTOMER_ID_WITHOUT_DASHES',
    'use_proto_plus': True
}
```

## 常见问题

### 无法获取开发者令牌

- 确保您的Google Ads账户有管理员权限
- 如果是新账户，可能需要等待一段时间或达到一定的广告支出
- 考虑使用测试令牌进行开发测试

### 授权失败

- 检查OAuth同意屏幕配置
- 确保添加了正确的范围
- 验证重定向URI是否正确

### 找不到客户ID

- 确保您的账户有权限访问Google Ads API
- 检查refresh_token是否正确
- 确认developer_token是否有效

## 参考资料

- [Google Ads API 文档](https://developers.google.com/google-ads/api/docs/start)
- [OAuth 2.0 认证](https://developers.google.com/identity/protocols/oauth2)
- [Google Ads API 客户端库 (Python)](https://developers.google.com/google-ads/api/docs/client-libs/python) 