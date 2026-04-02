export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ScoreBreakdown {
  demand_growth: number;
  competition: number;
  pain_intensity: number;
  confidence: number;
  momentum: number;
  query_volume: number;
}

export interface IdeaListItem {
  id: number;
  title: string;
  problem_statement: string | null;
  category: string | null;
  region: string | null;
  trend_type: string | null;
  opportunity_score: number;
  score_label: string | null;
  demand_growth_score: number;
  confidence_score: number;
  momentum_score: number;
  query_volume: number;
  created_at: string;
}

export interface IdeaDetail {
  id: number;
  title: string;
  problem_statement: string | null;
  why_it_matters: string | null;
  suggested_product: string | null;
  category: string | null;
  region: string | null;
  trend_type: string | null;
  opportunity_score: number;
  score_label: string | null;
  demand_growth_score: number;
  competition_score: number;
  pain_intensity_score: number;
  confidence_score: number;
  momentum_score: number;
  query_volume: number;
  ranking_reason: string | null;
  confidence_caveats: string | null;
  trend_data: string | null;
  signals_summary: string | null;
  cluster: ClusterListItem | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedIdeas {
  items: IdeaListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ClusterListItem {
  id: number;
  label: string;
  category: string | null;
  idea_count: number;
  created_at: string;
}

export interface ClusterDetail {
  id: number;
  label: string;
  description: string | null;
  category: string | null;
  idea_count: number;
  keywords: KeywordItem[];
  created_at: string;
}

export interface KeywordItem {
  id: number;
  keyword: string;
  weight: number;
  query_volume: number | null;
}

export interface SavedIdea {
  id: number;
  idea_id: number;
  note: string | null;
  created_at: string;
  updated_at: string;
  idea: {
    id: number;
    title: string;
    opportunity_score: number;
    score_label: string | null;
    category: string | null;
    region: string | null;
  } | null;
}

export interface Alert {
  id: number;
  keyword: string | null;
  category: string | null;
  region: string | null;
  min_score: number | null;
  cadence: string;
  is_active: boolean;
  last_triggered_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExportItem {
  id: number;
  format: string;
  status: string;
  file_url: string | null;
  created_at: string;
  completed_at: string | null;
}

export type ScoreLabel = "Very Strong" | "Promising" | "Weak Signal" | "Low Priority";

export interface IdeasFilters {
  search?: string;
  category?: string;
  region?: string;
  trend_type?: string;
  min_score?: number;
  max_score?: number;
  confidence_min?: number;
  competition_max?: number;
  sort?: "score" | "recency" | "growth" | "confidence" | "momentum";
  order?: "asc" | "desc";
  page?: number;
  limit?: number;
}
