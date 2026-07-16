import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import * as endpoints from "../api/endpoints";
import type { Page, Post, PostInput } from "../types";

const PAGE_SIZE = 10;

/** Centralized query keys — invalidation targets match on prefix. */
export const keys = {
  feed: ["feed"] as const,
  post: (id: number) => ["posts", id] as const,
  userPosts: (username: string) => ["users", username, "posts"] as const,
  followers: (username: string) => ["users", username, "followers"] as const,
  following: (username: string) => ["users", username, "following"] as const,
};

export function useFeed() {
  return useInfiniteQuery({
    queryKey: keys.feed,
    queryFn: ({ pageParam }) => endpoints.getFeed(PAGE_SIZE, pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage: Page<Post>) => {
      const nextOffset = lastPage.offset + lastPage.items.length;
      return nextOffset < lastPage.total ? nextOffset : undefined;
    },
  });
}

export function usePost(id: number) {
  return useQuery({
    queryKey: keys.post(id),
    queryFn: () => endpoints.getPost(id),
  });
}

export function useUserPosts(username: string) {
  return useInfiniteQuery({
    queryKey: keys.userPosts(username),
    queryFn: ({ pageParam }) => endpoints.getUserPosts(username, PAGE_SIZE, pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage: Page<Post>) => {
      const nextOffset = lastPage.offset + lastPage.items.length;
      return nextOffset < lastPage.total ? nextOffset : undefined;
    },
  });
}

export function useCreatePost() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: PostInput) => endpoints.createPost(input),
    onSuccess: (post) => {
      queryClient.setQueryData(keys.post(post.id), post);
      void queryClient.invalidateQueries({ queryKey: keys.feed });
      void queryClient.invalidateQueries({ queryKey: keys.userPosts(post.author.username) });
    },
  });
}

export function useUpdatePost(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: PostInput) => endpoints.updatePost(id, input),
    onSuccess: (post) => {
      queryClient.setQueryData(keys.post(id), post);
      void queryClient.invalidateQueries({ queryKey: keys.feed });
      void queryClient.invalidateQueries({ queryKey: keys.userPosts(post.author.username) });
    },
  });
}

export function useDeletePost(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => endpoints.deletePost(id),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: keys.post(id) });
      void queryClient.invalidateQueries({ queryKey: keys.feed });
      void queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

export function useRegenerateAi(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => endpoints.regenerateAi(id),
    onSuccess: () => {
      // AI runs in the backend's background task; refetch after a grace period
      setTimeout(() => {
        void queryClient.invalidateQueries({ queryKey: keys.post(id) });
      }, 4000);
    },
  });
}
