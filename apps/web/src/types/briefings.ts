export type BriefingScores = {
  heat: number | null;
  credibility: number | null;
  opportunity: number | null;
  risk: number | null;
};

export type BriefingEvidence = {
  raw_item_id: string;
  title: string;
  url: string | null;
};

export type BriefingItem = {
  intel_file_id: string;
  title: string;
  status: string;
  reason: string;
  scores: BriefingScores;
  key_evidence: BriefingEvidence[];
};

export type BriefingSections = {
  new_files: BriefingItem[];
  updated_files: BriefingItem[];
  resurrected: BriefingItem[];
  high_opportunity: BriefingItem[];
  risk_or_noise: BriefingItem[];
};

export type DailyBriefingData = {
  meta: {
    generated_at: string;
    window_hours: number;
    item_count: number;
  };
  overview: string;
  sections: BriefingSections;
  debug: Record<string, unknown>;
};

export type WeeklyBriefingSections = {
  changed_files: BriefingItem[];
  resurrected: BriefingItem[];
  verified_or_debunked: BriefingItem[];
  opportunity_gainers: BriefingItem[];
  cooling_or_noise: BriefingItem[];
};

export type WeeklyRetrospectiveData = {
  meta: {
    generated_at: string;
    window_days: number;
    item_count: number;
  };
  overview: string;
  sections: WeeklyBriefingSections;
  debug: Record<string, unknown>;
};
