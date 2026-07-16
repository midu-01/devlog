import { api } from "./client";
import type {
  LoginInput,
  Page,
  Post,
  PostInput,
  RegisterInput,
  Token,
  User,
  UserSummary,
} from "../types";

// ---- auth ----

export async function register(input: RegisterInput): Promise<User> {
  const { data } = await api.post<User>("/auth/register", input);
  return data;
}

export async function login(input: LoginInput): Promise<Token> {
  // OAuth2PasswordRequestForm expects form-encoded fields
  const form = new URLSearchParams();
  form.set("username", input.username);
  form.set("password", input.password);
  const { data } = await api.post<Token>("/auth/login", form);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>("/users/me");
  return data;
}

// ---- posts ----

export async function createPost(input: PostInput): Promise<Post> {
  const { data } = await api.post<Post>("/posts", input);
  return data;
}

export async function getPost(id: number): Promise<Post> {
  const { data } = await api.get<Post>(`/posts/${id}`);
  return data;
}

export async function updatePost(id: number, input: PostInput): Promise<Post> {
  const { data } = await api.put<Post>(`/posts/${id}`, input);
  return data;
}

export async function deletePost(id: number): Promise<void> {
  await api.delete(`/posts/${id}`);
}

export async function regenerateAi(id: number): Promise<void> {
  await api.post(`/posts/${id}/regenerate-ai`);
}

export async function getFeed(limit: number, offset: number): Promise<Page<Post>> {
  const { data } = await api.get<Page<Post>>("/feed", { params: { limit, offset } });
  return data;
}

export async function getUserPosts(
  username: string,
  limit: number,
  offset: number,
): Promise<Page<Post>> {
  const { data } = await api.get<Page<Post>>(`/users/${username}/posts`, {
    params: { limit, offset },
  });
  return data;
}

// ---- follows ----

export async function followUser(username: string): Promise<void> {
  await api.post(`/users/${username}/follow`);
}

export async function unfollowUser(username: string): Promise<void> {
  await api.delete(`/users/${username}/follow`);
}

export async function getFollowers(username: string): Promise<Page<UserSummary>> {
  const { data } = await api.get<Page<UserSummary>>(`/users/${username}/followers`);
  return data;
}

export async function getFollowing(username: string): Promise<Page<UserSummary>> {
  const { data } = await api.get<Page<UserSummary>>(`/users/${username}/following`);
  return data;
}
