import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../stores/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 处理Token过期
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // 如果是401错误且不是刷新Token的请求，尝试刷新Token
    if (error.response?.status === 401 && !originalRequest.url?.includes('/auth/refresh')) {
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        
        const { refreshToken, logout } = useAuthStore.getState();
        
        if (refreshToken) {
          try {
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            });
            
            const { access_token, refresh_token } = response.data;
            const { login } = useAuthStore.getState();
            
            // 更新Token
            useAuthStore.setState({
              accessToken: access_token,
              refreshToken: refresh_token,
            });
            
            // 重试原始请求
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          } catch (refreshError) {
            // 刷新失败，登出用户
            logout();
            window.location.href = '/login';
          }
        } else {
          logout();
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

// 认证API
export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  register: (data: {
    username: string;
    password: string;
    email?: string;
    nickname?: string;
  }) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
};

// 账号API
export const accountApi = {
  list: (params?: { page?: number; page_size?: number; is_active?: boolean }) =>
    api.get('/accounts', { params }),
  get: (id: number) => api.get(`/accounts/${id}`),
  create: (data: any) => api.post('/accounts', data),
  update: (id: number, data: any) => api.put(`/accounts/${id}`, data),
  delete: (id: number) => api.delete(`/accounts/${id}`),
  refreshCookie: (id: number, data: { cookie_web_session: string; cookie_a1: string }) =>
    api.post(`/accounts/${id}/refresh-cookie`, data),
  stats: () => api.get('/accounts/stats'),
};

// 规则API
export const ruleApi = {
  list: (params?: { account_id?: number; rule_type?: string; is_enabled?: boolean }) =>
    api.get('/accounts/rules', { params }),
  get: (id: number) => api.get(`/accounts/rules/${id}`),
  create: (data: any) => api.post('/accounts/rules', data),
  update: (id: number, data: any) => api.put(`/accounts/rules/${id}`, data),
  delete: (id: number) => api.delete(`/accounts/rules/${id}`),
  bulkEnable: (ids: number[], enabled: boolean) =>
    api.post('/accounts/rules/bulk-enable', { ids, enabled }),
};

// 统计API
export const statsApi = {
  overview: () => api.get('/accounts/stats/overview'),
  trend: (period: string) => api.get('/accounts/stats/trend', { params: { period } }),
  history: (params?: {
    page?: number;
    page_size?: number;
    account_id?: number;
    target_type?: string;
  }) => api.get('/accounts/history', { params }),
};

// 用户API
export const userApi = {
  profile: () => api.get('/user/profile'),
  update: (data: any) => api.put('/user/profile', data),
  subscription: () => api.get('/user/subscription'),
};

// 套餐API
export const subscriptionApi = {
  list: () => api.get('/subscription/plans'),
  current: () => api.get('/subscription/current'),
  subscribe: (plan: string) => api.post('/subscription/subscribe', { plan }),
  cancel: () => api.post('/subscription/cancel'),
};