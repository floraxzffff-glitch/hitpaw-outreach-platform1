/**
 * VikPea API 调用库
 * 处理所有与后端 API 的通信
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// API 响应类型定义
export interface KeywordAnalysisResponse {
  keyword: string;
  source: string;
  total_found: number;
  eligible_count: number;
  email_found_count: number;
  email_rate: number;
  timestamp: string;
  details?: Record<string, any>;
}

export interface EmailValidationResponse {
  email: string;
  is_valid: boolean;
  is_blacklisted: boolean;
  confidence_score: number;
  reason?: string;
}

export interface SEOOpportunityResponse {
  url: string;
  title: string;
  relevance_score: number;
  level: 'A' | 'B' | 'C';
  opportunity_type: string;
  action: string;
  timestamp: string;
}

export interface ReportResponse {
  report_id: string;
  report_type: string;
  title: string;
  generated_at: string;
  data: Record<string, any>;
  file_url?: string;
}

export interface StatsResponse {
  total_keywords_analyzed: number;
  total_emails_validated: number;
  total_opportunities_found: number;
  today_activities: {
    keywords_analyzed: number;
    emails_validated: number;
    opportunities_found: number;
  };
  last_updated: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

export interface YoutubeKeyword {
  keyword: string;
  enabled: boolean;
  note: string;
}

export interface YoutubeSearchSettings {
  YOUTUBE_RESULTS_PER_KEYWORD: number;
  YOUTUBE_MIN_VIDEO_VIEWS: number;
  YOUTUBE_MIN_SHORTS_VIEWS: number;
  YOUTUBE_MIN_RECENT_AVG_VIEWS: number;
  YOUTUBE_RECENT_VIDEO_COUNT: number;
  YOUTUBE_ACTIVE_WITHIN_DAYS: number;
  YOUTUBE_SUB_MIN: number;
  YOUTUBE_SUB_MAX: number;
  YOUTUBE_MARKET_SCORE_MIN: number;
}

export interface YoutubeSearchJob {
  job_id: string;
  resource: string;
  label: string;
  status: 'running' | 'stopping' | 'stopped' | 'completed' | 'failed';
  log: string[];
  error?: string | null;
  started_at: string;
  finished_at?: string | null;
  stoppable?: boolean;
}

export interface EmailTemplateSettings {
  PRODUCT_NAME: string;
  PRODUCT_TEAM: string;
  PRODUCT_URL: string;
  FROM_NAME: string;
  OUTREACH_SUBJECT_YOUTUBE: string;
  OUTREACH_TEMPLATE_YOUTUBE: string;
  OUTREACH_SUBJECT_ARTICLE: string;
  OUTREACH_TEMPLATE_ARTICLE: string;
}

export interface SystemSettings {
  SMTP_SERVER: string;
  SMTP_PORT: number;
  SMTP_TIMEOUT: number;
  SMTP_ALLOW_INSECURE_SSL: boolean;
  FROM_EMAIL: string;
  IMAP_SERVER: string;
  IMAP_PORT: number;
  DAILY_SEND_LIMIT: number;
  FOLLOWUP_DAILY_LIMIT: number;
  FOLLOWUP1_AFTER_DAYS: number;
  FOLLOWUP2_AFTER_DAYS: number;
  DELAY_SEC: number;
  SERP_PROVIDER: string;
  DATAFORSEO_LOGIN: string;
  ANTHROPIC_API_BASE: string;
  ANTHROPIC_TAG_MODEL: string;
  PASSWORD_SET: boolean;
  SERPER_API_KEY_SET: boolean;
  SERPAPI_KEY_SET: boolean;
  DATAFORSEO_PASSWORD_SET: boolean;
  YOUTUBE_API_KEY_SET: boolean;
  ANTHROPIC_API_KEY_SET: boolean;
}

export interface ConfirmedCandidateInput {
  频道名: string;
  邮箱: string;
  主页链接: string;
  视频链接: string;
  备注: string;
  类型: string;
  来源关键词: string;
  频道标签: string;
}

export interface TrackerUpdateInput {
  是否回复: string;
  回复摘要: string;
  当前状态: string;
  ABC分级: string;
  跟进1日期: string;
  跟进1状态: string;
  跟进2日期: string;
  跟进2状态: string;
  最近回复日期: string;
  频道标签: string;
}

export interface SendTarget {
  rownum: number;
  name: string;
  email: string;
  subject: string;
  opening: string;
  link: string;
  type: string;
  source: string;
}

export interface SendBlockedTarget extends SendTarget {
  status: string;
  reason: string;
}

export interface SendPreview {
  preview_id: string | null;
  message: string | null;
  targets: SendTarget[];
  blocked: SendBlockedTarget[];
}

export interface SendJob {
  job_id: string;
  resource: string;
  label: string;
  status: 'running' | 'completed' | 'failed';
  log: string[];
  error?: string | null;
  started_at: string;
  finished_at?: string | null;
}

// API 错误类
export class APIError extends Error {
  public statusCode: number;
  public data?: any;

  constructor(message: string, statusCode: number, data?: any) {
    super(message);
    this.statusCode = statusCode;
    this.data = data;
    this.name = 'APIError';
  }
}

// VikPea API 客户端类
class VikPeaAPI {
  private axiosInstance: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error)
    );
  }

  private handleError(error: AxiosError): never {
    if (error.response) {
      const data = error.response.data as { detail?: string } | undefined;
      throw new APIError(
        data?.detail || error.message,
        error.response.status,
        error.response.data
      );
    }
    throw new APIError(error.message, 500);
  }

  // ======================== 健康检查 ========================

  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.axiosInstance.get('/health');
    return response.data;
  }

  // ======================== 关键词分析 ========================

  async analyzeKeyword(
    keyword: string,
    source: 'youtube' | 'article' | 'seo' = 'article',
    limit: number = 30,
    minScore: number = 3.0
  ): Promise<KeywordAnalysisResponse> {
    const response = await this.axiosInstance.post('/api/analyze/keyword', {
      keyword,
      source,
      limit,
      min_score: minScore,
    });
    return response.data;
  }

  async analyzeKeywordsBatch(keywords: Array<{keyword: string; source: string}>): Promise<string> {
    const response = await this.axiosInstance.post('/api/analyze/batch', keywords);
    return response.data.task_id;
  }

  async getBatchResult(taskId: string): Promise<{
    task_id: string;
    status: 'processing' | 'completed' | 'failed';
    results?: KeywordAnalysisResponse[];
    error?: string;
  }> {
    const response = await this.axiosInstance.get(`/api/analyze/batch/${taskId}`);
    return response.data;
  }

  // ======================== 邮箱验证 ========================

  async validateEmail(
    email: string,
    checkBlacklist: boolean = true
  ): Promise<EmailValidationResponse> {
    const response = await this.axiosInstance.post('/api/validate/email', {
      email,
      check_blacklist: checkBlacklist,
    });
    return response.data;
  }

  async validateEmailsBatch(emails: string[]): Promise<{
    total: number;
    processed: number;
    results: EmailValidationResponse[];
    timestamp: string;
  }> {
    const response = await this.axiosInstance.post('/api/validate/batch', emails);
    return response.data;
  }

  // ======================== SEO 扫描 ========================

  async scanSEO(
    keyword: string,
    source: 'youtube' | 'article' | 'seo' = 'seo',
    minScore: number = 3.0
  ): Promise<SEOOpportunityResponse[]> {
    const response = await this.axiosInstance.post('/api/seo/scan', {
      keyword,
      source,
      limit: 50,
      min_score: minScore,
    });
    return response.data;
  }

  // ======================== 报告生成 ========================

  async generateReport(
    reportType: 'keyword_review' | 'seo_analysis' | 'email_validation',
    includeStats: boolean = true
  ): Promise<ReportResponse> {
    const response = await this.axiosInstance.post('/api/report/generate', {
      report_type: reportType,
      include_stats: includeStats,
    });
    return response.data;
  }

  async getReport(reportId: string): Promise<ReportResponse> {
    const response = await this.axiosInstance.get(`/api/report/${reportId}`);
    return response.data;
  }

  async listReports(skip: number = 0, limit: number = 20): Promise<{
    total: number;
    reports: ReportResponse[];
    skip: number;
    limit: number;
  }> {
    const response = await this.axiosInstance.get('/api/reports', {
      params: { skip, limit },
    });
    return response.data;
  }

  // ======================== YouTube KOL 搜索 ========================

  async listYoutubeKeywords(): Promise<{ keywords: YoutubeKeyword[] }> {
    const response = await this.axiosInstance.get('/api/youtube/keywords');
    return response.data;
  }

  async toggleYoutubeKeyword(
    keyword: string,
    enabled: boolean,
    note?: string
  ): Promise<{ status: string; keywords: YoutubeKeyword[] }> {
    const response = await this.axiosInstance.post('/api/youtube/keywords/toggle', {
      keyword,
      enabled,
      note,
    });
    return response.data;
  }

  async addYoutubeKeywordsBatch(
    keywords: string[]
  ): Promise<{ added: number; updated: number; keywords: YoutubeKeyword[] }> {
    const response = await this.axiosInstance.post('/api/youtube/keywords/batch', { keywords });
    return response.data;
  }

  async deleteYoutubeKeyword(keyword: string): Promise<{ keywords: YoutubeKeyword[] }> {
    const response = await this.axiosInstance.delete(
      `/api/youtube/keywords/${encodeURIComponent(keyword)}`
    );
    return response.data;
  }

  async getYoutubeSettings(): Promise<YoutubeSearchSettings> {
    const response = await this.axiosInstance.get('/api/youtube/settings');
    return response.data;
  }

  async updateYoutubeSettings(
    updates: Partial<YoutubeSearchSettings>
  ): Promise<YoutubeSearchSettings> {
    const response = await this.axiosInstance.put('/api/youtube/settings', updates);
    return response.data;
  }

  async startYoutubeSearch(): Promise<{ job_id: string; status: string }> {
    const response = await this.axiosInstance.post('/api/youtube/search/start');
    return response.data;
  }

  async getYoutubeSearchJob(jobId: string): Promise<YoutubeSearchJob> {
    const response = await this.axiosInstance.get(`/api/youtube/search/jobs/${jobId}`);
    return response.data;
  }

  async listYoutubeSearchJobs(): Promise<{ jobs: YoutubeSearchJob[] }> {
    const response = await this.axiosInstance.get('/api/youtube/search/jobs');
    return response.data;
  }

  async stopYoutubeSearchJob(jobId: string): Promise<{ status: string }> {
    const response = await this.axiosInstance.post(`/api/youtube/search/jobs/${jobId}/stop`);
    return response.data;
  }

  async getKolCandidates(): Promise<{
    confirmed: Record<string, any>[];
    pending: Record<string, any>[];
    no_email: Record<string, any>[];
  }> {
    const response = await this.axiosInstance.get('/api/kol/candidates');
    return response.data;
  }

  async addConfirmedCandidate(
    data: Partial<ConfirmedCandidateInput>
  ): Promise<{ candidates: Record<string, any>[] }> {
    const response = await this.axiosInstance.post('/api/kol/candidates/confirmed', data);
    return response.data;
  }

  async updateConfirmedCandidate(
    rownum: number,
    data: Partial<ConfirmedCandidateInput>
  ): Promise<{ candidates: Record<string, any>[] }> {
    const response = await this.axiosInstance.put(`/api/kol/candidates/confirmed/${rownum}`, data);
    return response.data;
  }

  async deleteConfirmedCandidate(rownum: number): Promise<{ candidates: Record<string, any>[] }> {
    const response = await this.axiosInstance.delete(`/api/kol/candidates/confirmed/${rownum}`);
    return response.data;
  }

  // ======================== 发送追踪 ========================

  async getTracker(): Promise<{ rows: Record<string, any>[] }> {
    const response = await this.axiosInstance.get('/api/tracker');
    return response.data;
  }

  async updateTracker(
    rownum: number,
    data: Partial<TrackerUpdateInput>
  ): Promise<{ rows: Record<string, any>[] }> {
    const response = await this.axiosInstance.put(`/api/tracker/${rownum}`, data);
    return response.data;
  }

  // ======================== 邮件模板 ========================

  async getEmailTemplates(): Promise<EmailTemplateSettings> {
    const response = await this.axiosInstance.get('/api/email-templates');
    return response.data;
  }

  async updateEmailTemplates(
    updates: Partial<EmailTemplateSettings>
  ): Promise<EmailTemplateSettings> {
    const response = await this.axiosInstance.put('/api/email-templates', updates);
    return response.data;
  }

  // ======================== 系统设置（SMTP/IMAP/API Key） ========================

  async getSystemSettings(): Promise<SystemSettings> {
    const response = await this.axiosInstance.get('/api/system-settings');
    return response.data;
  }

  async updateSystemSettings(updates: Record<string, any>): Promise<SystemSettings> {
    const response = await this.axiosInstance.put('/api/system-settings', updates);
    return response.data;
  }

  // ======================== 过滤配置管理 ========================

  async getFilterConfig(): Promise<{
    negative_keywords: string[];
    negative_keywords_count: number;
    competitor_sites_count: number;
    competitor_email_suffixes_count: number;
    affiliate_blacklist_count: number;
    longterm_partners_count: number;
  }> {
    const response = await this.axiosInstance.get('/api/filter-config');
    return response.data;
  }

  async reloadFilterConfig(): Promise<{ status: string; message: string }> {
    const response = await this.axiosInstance.post('/api/filter-config/reload');
    return response.data;
  }

  // ======================== 发送开发信 ========================

  async previewSend(personalize: boolean = false): Promise<SendPreview> {
    const response = await this.axiosInstance.post('/api/send/preview', null, {
      params: { personalize },
    });
    return response.data;
  }

  async confirmSend(previewId: string, rownums: number[]): Promise<{ job_id: string; status: string }> {
    const response = await this.axiosInstance.post('/api/send/confirm', {
      preview_id: previewId,
      rownums,
    });
    return response.data;
  }

  async getSendJob(jobId: string): Promise<SendJob> {
    const response = await this.axiosInstance.get(`/api/send/jobs/${jobId}`);
    return response.data;
  }

  // ======================== 统计数据 ========================

  async getStats(): Promise<StatsResponse> {
    const response = await this.axiosInstance.get('/api/stats');
    return response.data;
  }

  // ======================== DataForSEO API ========================

  async testDataForSEO(login: string, password: string): Promise<{
    success: boolean;
    balance?: number;
    currency?: string;
    message: string;
  }> {
    const response = await this.axiosInstance.post('/api/dataforseo/test', {
      login,
      password,
    });
    return response.data;
  }

  async analyzeChannelDeep(channelId: string): Promise<{
    channel_id: string;
    title: string;
    description: string;
    subscriber_count: number;
    video_count: number;
    view_count: number;
    subscriber_growth_30d: number;
    view_growth_30d: number;
    avg_views_per_video: number;
    avg_likes_per_video: number;
    avg_comments_per_video: number;
    last_video_date: string;
    videos_last_30d: number;
    engagement_rate: number;
    growth_score: number;
    activity_score: number;
  }> {
    const response = await this.axiosInstance.post('/api/dataforseo/channel/analyze', {
      channel_id: channelId,
    });
    return response.data;
  }

  async searchChannelsDataForSEO(params: {
    keyword: string;
    limit?: number;
    min_subscribers?: number;
    max_subscribers?: number;
    language?: string;
  }): Promise<{
    keyword: string;
    total: number;
    channels: Array<{
      channel_id: string;
      title: string;
      url: string;
      subscriber_count: number;
      video_count: number;
      description: string;
    }>;
  }> {
    const response = await this.axiosInstance.post('/api/dataforseo/channel/search', params);
    return response.data;
  }

  async findSimilarChannels(
    channelId: string,
    limit: number = 20
  ): Promise<{
    reference_channel_id: string;
    total: number;
    similar_channels: Array<{
      channel_id: string;
      title: string;
      url: string;
      subscriber_count: number;
      video_count: number;
      description: string;
    }>;
  }> {
    const response = await this.axiosInstance.post('/api/dataforseo/channel/similar', {
      channel_id: channelId,
      limit,
    });
    return response.data;
  }

  async batchAnalyzeChannels(channelIds: string[]): Promise<{
    total_requested: number;
    successful: number;
    failed: number;
    results: any[];
    errors: any[];
  }> {
    const response = await this.axiosInstance.post('/api/dataforseo/channel/batch-analyze', {
      channel_ids: channelIds,
    });
    return response.data;
  }

  // ======================== 配置 ========================

  async getConfig(): Promise<{
    app: string;
    version: string;
    features: string[];
  }> {
    const response = await this.axiosInstance.get('/api/config');
    return response.data;
  }
}

// 导出单例
export const vikpeaAPI = new VikPeaAPI();

// ======================== 便捷导出函数 ========================

// DataForSEO 相关
export const testDataForSEO = (login: string, password: string) =>
  vikpeaAPI.testDataForSEO(login, password);

export const analyzeChannelDeep = (channelId: string) =>
  vikpeaAPI.analyzeChannelDeep(channelId);

export const searchChannelsDataForSEO = (params: {
  keyword: string;
  limit?: number;
  min_subscribers?: number;
  max_subscribers?: number;
  language?: string;
}) => vikpeaAPI.searchChannelsDataForSEO(params);

export const findSimilarChannels = (channelId: string, limit?: number) =>
  vikpeaAPI.findSimilarChannels(channelId, limit);

export const batchAnalyzeChannels = (channelIds: string[]) =>
  vikpeaAPI.batchAnalyzeChannels(channelIds);

export default vikpeaAPI;
