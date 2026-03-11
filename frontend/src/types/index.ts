// 用户相关类型
export interface User {
  id: number;
  username: string;
  email?: string;
  phone?: string;
  nickname?: string;
  avatar?: string;
  bio?: string;
  subscription_plan: string;
  subscription_expire_at?: string;
  is_active: boolean;
  is_verified: boolean;
  total_replies: number;
  today_replies: number;
  created_at: string;
  last_login_at?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  phone?: string;
  nickname?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface PlanInfo {
  plan: string;
  name: string;
  price: number;
  accounts_limit: number;
  daily_replies_limit: number;
  keywords_limit: number;
  features: Record<string, boolean>;
}

export interface SubscriptionInfo {
  plan: string;
  plan_info: PlanInfo;
  expire_at?: string;
  auto_renew: boolean;
  status: string;
}

// 账号相关类型
export interface XHSAccount {
  id: number;
  user_id: number;
  name: string;
  cookie_web_session?: string;
  cookie_a1?: string;
  xhs_user_id?: string;
  nickname?: string;
  avatar?: string;
  follower_count?: number;
  monitor_comments: boolean;
  monitor_messages: boolean;
  monitor_note_ids?: string;
  ignored_users?: string;
  is_active: boolean;
  login_status: string;
  last_check_at?: string;
  cookie_expire_at?: string;
  created_at: string;
  updated_at: string;
}

export interface XHSAccountCreate {
  name: string;
  cookie_web_session?: string;
  cookie_a1?: string;
  monitor_comments?: boolean;
  monitor_messages?: boolean;
  monitor_note_ids?: string;
  ignored_users?: string;
}

// 规则相关类型
export interface ReplyRule {
  id: number;
  user_id: number;
  account_id?: number;
  name: string;
  rule_type: string;
  match_type: string;
  keywords: string;
  reply_templates: string;
  priority: number;
  is_enabled: boolean;
  use_ai_reply: boolean;
  ai_prompt?: string;
  match_count: number;
  reply_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReplyRuleCreate {
  name: string;
  rule_type: string;
  match_type?: string;
  keywords: string;
  reply_templates: string;
  account_id?: number;
  priority?: number;
  is_enabled?: boolean;
  use_ai_reply?: boolean;
  ai_prompt?: string;
}

// 统计相关类型
export interface StatsOverview {
  total_accounts: number;
  active_accounts: number;
  total_rules: number;
  enabled_rules: number;
  total_replies: number;
  today_replies: number;
  success_rate: number;
}

export interface TrendDataPoint {
  date: string;
  replies: number;
  success: number;
  failed: number;
}

export interface StatsTrend {
  period: string;
  data: TrendDataPoint[];
}

export interface ReplyHistoryItem {
  id: number;
  account_id: number;
  target_type: string;
  target_id: string;
  target_user_id?: string;
  target_content: string;
  reply_content: string;
  reply_status: string;
  error_message?: string;
  created_at: string;
}

export interface ReplyHistoryResponse {
  items: ReplyHistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// API响应类型
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}