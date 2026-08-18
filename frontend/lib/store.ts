/**
 * 全局状态管理（使用 Zustand）
 */

import { create } from 'zustand';

// API 结果存储
interface ApiStore {
  // 关键词分析
  keywordResult: any | null;
  setKeywordResult: (result: any) => void;

  // 邮箱验证
  emailResults: any[];
  setEmailResults: (results: any[]) => void;
  addEmailResult: (result: any) => void;

  // SEO 机会
  seoOpportunities: any[];
  setSeoOpportunities: (opportunities: any[]) => void;

  // 报告
  reports: any[];
  setReports: (reports: any[]) => void;

  // 加载状态
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  // 错误状态
  error: string | null;
  setError: (error: string | null) => void;

  // 清除所有状态
  reset: () => void;
}

export const useApiStore = create<ApiStore>((set) => ({
  keywordResult: null,
  setKeywordResult: (result) => set({ keywordResult: result }),

  emailResults: [],
  setEmailResults: (results) => set({ emailResults: results }),
  addEmailResult: (result) => 
    set((state) => ({ emailResults: [...state.emailResults, result] })),

  seoOpportunities: [],
  setSeoOpportunities: (opportunities) => set({ seoOpportunities: opportunities }),

  reports: [],
  setReports: (reports) => set({ reports }),

  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  error: null,
  setError: (error) => set({ error }),

  reset: () =>
    set({
      keywordResult: null,
      emailResults: [],
      seoOpportunities: [],
      reports: [],
      isLoading: false,
      error: null,
    }),
}));
