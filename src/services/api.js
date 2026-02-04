// API服务配置
const API_BASE_URL = '/api'; // 假设API基础路径为/api

/**
 * 验证JWT令牌是否有效
 * @param {string} token - JWT令牌
 * @returns {boolean} 是否有效
 */
const isTokenValid = (token) => {
  if (!token) return false;
  
  try {
    // 解析JWT令牌，检查是否过期
    const payload = JSON.parse(atob(token.split('.')[1]));
    const now = Math.floor(Date.now() / 1000);
    // 提前1分钟提醒过期，避免时间差问题
    return payload.exp > (now + 60);
  } catch (e) {
    console.error('令牌验证错误:', e);
    return false;
  }
};

/**
 * 处理HTTP请求的基础函数
 * @param {string} endpoint - API端点
 * @param {string} method - HTTP方法
 * @param {object} data - 请求数据
 * @returns {Promise} 返回处理后的响应
 */
export const request = async (endpoint, method = 'GET', data = null) => {
  try {
    let token = localStorage.getItem('access_token');
    
    // 如果令牌无效，清除它
    if (token && !isTokenValid(token)) {
      console.warn('令牌已过期，正在清除');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      token = null;
      // 触发全局登出事件
      window.dispatchEvent(new Event('logout'));
      throw new Error('登录已过期，请重新登录');
    }
    
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include' // 包含cookie，用于会话管理
    };

    // 如果存在访问令牌，则添加到请求头
    if (token) {
      options.headers['Authorization'] = `Bearer ${token}`;
      console.log('API请求发送，包含认证令牌'); // 调试信息
    } else {
      console.warn(`API请求警告: 访问令牌未找到或已过期，端点: ${endpoint}`);
    }

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    console.log(`API请求 ${method} ${API_BASE_URL}${endpoint} 响应状态:`, response.status);
    console.log(`认证令牌:`, token ? '存在' : '不存在');
    
    // 检查响应是否为空
    if (response.status === 204) {
      // No Content 状态码
      return {};
    }
    
    // 检查响应是否包含内容
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.error(`响应不是JSON格式 (${endpoint}):`, response);
      // 尝试读取响应文本以获取更多信息
      const responseText = await response.text();
      console.error(`响应内容 (${endpoint}):`, responseText);
      
      // 尝试解析响应文本
      if (responseText.trim().startsWith('{') || responseText.trim().startsWith('[')) {
        try {
          return JSON.parse(responseText);
        } catch (e) {
          console.error(`尝试解析可能的JSON响应失败:`, e);
        }
      }
      
      throw new Error(`服务器响应不是JSON格式，请检查后端API实现: ${responseText}`);
    }
    
    let result;
    try {
      result = await response.json();
    } catch (parseError) {
      console.error(`JSON解析错误 (${endpoint}):`, parseError);
      // 读取原始响应文本以调试
      const responseText = await response.text();
      console.error(`原始响应文本 (${endpoint}):`, responseText);
      throw new Error(`服务器响应格式错误: 无法解析JSON - ${responseText}`);
    }

    if (!response.ok) {
      // 检查是否是认证相关错误
      if (response.status === 401) {
        // 检查错误消息是否明确指示认证问题
        const authRelatedErrors = [
          '令牌', 'token', 'Token', 'expired', 'invalid', '认证', 
          'Unauthorized', 'Missing', 'CSRF', 'need', 'login', '未登录',
          '认证错误', '需要登录', '登陆', '过期', 'invalid token', 'expired token'
        ];
        
        const errorText = result.error || result.message || '';
        const isAuthError = authRelatedErrors.some(authTerm => 
          errorText.toLowerCase().includes(authTerm.toLowerCase())
        );
        
        if (isAuthError) {
          console.error(`认证错误 (${endpoint}):`, result);
          // 确实是认证问题才清除令牌
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          // 触发全局事件，通知应用更新状态
          window.dispatchEvent(new Event('logout'));
        } else {
          // 可能是其他类型的401错误，不一定是认证问题
          console.error(`API请求错误 [${response.status}] (${endpoint}):`, result);
          // 不清除认证信息
        }
      } else if (response.status === 404) {
        console.error(`API端点不存在 (${endpoint}) [${response.status}]:`, result);
      } else {
        console.error(`API请求失败 (${endpoint}) [${response.status}]:`, result);
      }
      throw new Error(result.error || result.message || `请求失败: ${response.status}`);
    }

    return result;
  } catch (error) {
    // 检查是否是网络错误
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.error('网络错误，请检查后端服务是否运行:', error);
      throw new Error('网络连接失败，请检查后端服务是否正常运行');
    }
    console.error('API请求错误:', error);
    throw error;
  }
};

// 专门用于登录的请求函数，不需要认证令牌
export const loginRequest = async (endpoint, method = 'POST', data = null) => {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
    credentials: 'include' // 包含cookie
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: '未知错误' }));
    throw new Error(errorData.error || `登录请求失败: ${response.status}`);
  }
  
  return await response.json();
};