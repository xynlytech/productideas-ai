import type {
  TokenResponse,
  User,
  PaginatedIdeas,
  IdeaDetail,
  IdeaListItem,
  ClusterListItem,
  ClusterDetail,
  SavedIdea,
  Alert,
  ExportItem,
  IdeasFilters,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("access_token");
    }
    return this.token;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      this.setToken(null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new Error("Unauthorized");
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `API error: ${res.status}`);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Auth
  async signup(email: string, password: string, name: string): Promise<TokenResponse> {
    const data = await this.request<TokenResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const data = await this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async logout(): Promise<void> {
    await this.request("/auth/logout", { method: "POST" });
    this.setToken(null);
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  // Ideas
  async getIdeas(filters: IdeasFilters = {}): Promise<PaginatedIdeas> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
      }
    });
    return this.request<PaginatedIdeas>(`/ideas?${params}`);
  }

  async getIdea(id: number): Promise<IdeaDetail> {
    return this.request<IdeaDetail>(`/ideas/${id}`);
  }

  async getRelatedIdeas(id: number, limit = 5): Promise<IdeaListItem[]> {
    return this.request<IdeaListItem[]>(`/ideas/${id}/related?limit=${limit}`);
  }

  // Clusters
  async getClusters(category?: string): Promise<ClusterListItem[]> {
    const params = category ? `?category=${encodeURIComponent(category)}` : "";
    return this.request<ClusterListItem[]>(`/clusters${params}`);
  }

  async getCluster(id: number): Promise<ClusterDetail> {
    return this.request<ClusterDetail>(`/clusters/${id}`);
  }

  // Saved Ideas
  async getSavedIdeas(): Promise<SavedIdea[]> {
    return this.request<SavedIdea[]>("/saved-ideas");
  }

  async saveIdea(ideaId: number, note?: string): Promise<SavedIdea> {
    return this.request<SavedIdea>("/saved-ideas", {
      method: "POST",
      body: JSON.stringify({ idea_id: ideaId, note }),
    });
  }

  async updateSavedIdea(savedId: number, note: string): Promise<SavedIdea> {
    return this.request<SavedIdea>(`/saved-ideas/${savedId}`, {
      method: "PATCH",
      body: JSON.stringify({ note }),
    });
  }

  async deleteSavedIdea(savedId: number): Promise<void> {
    return this.request(`/saved-ideas/${savedId}`, { method: "DELETE" });
  }

  // Alerts
  async getAlerts(): Promise<Alert[]> {
    return this.request<Alert[]>("/alerts");
  }

  async createAlert(data: {
    keyword?: string;
    category?: string;
    region?: string;
    min_score?: number;
    cadence?: string;
  }): Promise<Alert> {
    return this.request<Alert>("/alerts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateAlert(
    id: number,
    data: Partial<Alert>
  ): Promise<Alert> {
    return this.request<Alert>(`/alerts/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteAlert(id: number): Promise<void> {
    return this.request(`/alerts/${id}`, { method: "DELETE" });
  }

  // Exports
  async createExport(format: "csv" | "pdf", filters?: Record<string, unknown>): Promise<ExportItem> {
    return this.request<ExportItem>("/exports", {
      method: "POST",
      body: JSON.stringify({ format, filters }),
    });
  }

  async getExport(id: number): Promise<ExportItem> {
    return this.request<ExportItem>(`/exports/${id}`);
  }
}

export const api = new ApiClient();
