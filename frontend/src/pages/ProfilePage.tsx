import { useParams } from "react-router-dom";
import { apiErrorMessage } from "../api/client";
import { PostCard } from "../components/PostCard";
import { useAuth } from "../context/AuthContext";
import { useFollow, useFollowers, useFollowing, useIsFollowing } from "../hooks/useFollows";
import { useUserPosts } from "../hooks/usePosts";

export function ProfilePage() {
  const { username = "" } = useParams<{ username: string }>();
  const { user } = useAuth();

  const postsQuery = useUserPosts(username);
  const followersQuery = useFollowers(username);
  const followingQuery = useFollowing(username);
  const isFollowing = useIsFollowing(username);
  const followMutation = useFollow(username);

  const isMe = user?.username === username;

  if (postsQuery.isPending) return <p className="status">Loading profile…</p>;
  if (postsQuery.error) return <p className="error">{apiErrorMessage(postsQuery.error)}</p>;

  const posts = postsQuery.data.pages.flatMap((page) => page.items);

  return (
    <div>
      <header className="profile-header">
        <h1>@{username}</h1>
        <p className="post-meta">
          <strong>{followersQuery.data?.total ?? "…"}</strong> followers ·{" "}
          <strong>{followingQuery.data?.total ?? "…"}</strong> following ·{" "}
          <strong>{postsQuery.data.pages[0]?.total ?? 0}</strong> posts
        </p>
        {!isMe && user && (
          <button
            type="button"
            onClick={() => followMutation.mutate(isFollowing ? "unfollow" : "follow")}
            disabled={followMutation.isPending || followersQuery.isPending}
          >
            {isFollowing ? "Unfollow" : "Follow"}
          </button>
        )}
        {followMutation.error && (
          <p className="error">{apiErrorMessage(followMutation.error)}</p>
        )}
      </header>

      {posts.length === 0 ? (
        <p className="status">No posts yet.</p>
      ) : (
        posts.map((post) => <PostCard key={post.id} post={post} />)
      )}
      {postsQuery.hasNextPage && (
        <button
          type="button"
          className="load-more"
          onClick={() => void postsQuery.fetchNextPage()}
          disabled={postsQuery.isFetchingNextPage}
        >
          {postsQuery.isFetchingNextPage ? "Loading…" : "Load more"}
        </button>
      )}
    </div>
  );
}
