import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as endpoints from "../api/endpoints";
import { keys } from "./usePosts";
import { useAuth } from "../context/AuthContext";

export function useFollowers(username: string) {
  return useQuery({
    queryKey: keys.followers(username),
    queryFn: () => endpoints.getFollowers(username),
  });
}

export function useFollowing(username: string) {
  return useQuery({
    queryKey: keys.following(username),
    queryFn: () => endpoints.getFollowing(username),
  });
}

/** Am I (current user) following `username`? Derived from their followers list. */
export function useIsFollowing(username: string): boolean {
  const { user } = useAuth();
  const { data } = useFollowers(username);
  if (!user || !data) return false;
  return data.items.some((u) => u.id === user.id);
}

export function useFollow(username: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (action: "follow" | "unfollow") =>
      action === "follow"
        ? endpoints.followUser(username)
        : endpoints.unfollowUser(username),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: keys.followers(username) });
      void queryClient.invalidateQueries({ queryKey: keys.following(username) });
      void queryClient.invalidateQueries({ queryKey: keys.feed });
    },
  });
}
