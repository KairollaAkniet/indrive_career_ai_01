import axios from "axios";
import type { Candidate, CandidatesListResponse } from "./types";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 15000,
});

export async function fetchCandidates(): Promise<Candidate[]> {
  const res = await api.get<CandidatesListResponse>("/api/candidates");
  return res.data.candidates;
}

export async function fetchCandidateById(id: number): Promise<Candidate> {
  const res = await api.get<Candidate>(`/api/candidates/${id}`);
  return res.data;
}

