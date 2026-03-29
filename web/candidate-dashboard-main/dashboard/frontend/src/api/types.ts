export type Candidate = {
  id: number;
  user_id: number;
  username: string | null;
  full_name: string | null;
  answers_text: string;
  ai_score: number;
  ai_summary: string | null;
  created_at: string; // приходит как ISO-строка
};

export type CandidatesListResponse = {
  candidates: Candidate[];
};

