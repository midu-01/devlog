/** Mirrors backend Pydantic schemas exactly. */

export interface Author {
  id: number;
  username: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  bio: string | null;
  created_at: string;
}

export interface UserSummary {
  id: number;
  username: string;
  bio: string | null;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  author: Author;
  summary: string | null;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface RegisterInput {
  username: string;
  email: string;
  password: string;
  bio?: string;
}

export interface LoginInput {
  username: string;
  password: string;
}

export interface PostInput {
  title: string;
  content: string;
}

/** FastAPI error body: detail is a string for HTTPException, an array for 422s. */
export interface ApiError {
  detail: string | Array<{ msg: string; loc: Array<string | number> }>;
}
