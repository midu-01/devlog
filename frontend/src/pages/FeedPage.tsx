import { useFeed } from "../hooks/usePosts";
import { PostCard } from "../components/PostCard";
import { apiErrorMessage } from "../api/client";

export function FeedPage() {
  const { data, error, isPending, isFetchingNextPage, hasNextPage, fetchNextPage } =
    useFeed();

  if (isPending) return <p className="status">Loading feed…</p>;
  if (error) return <p className="error">{apiErrorMessage(error)}</p>;

  const posts = data.pages.flatMap((page) => page.items);

  return (
    <div>
      <h1>Your feed</h1>
      {posts.length === 0 ? (
        <p className="status">
          Nothing here yet — follow some authors and their posts will show up.
        </p>
      ) : (
        posts.map((post) => <PostCard key={post.id} post={post} />)
      )}
      {hasNextPage && (
        <button
          type="button"
          className="load-more"
          onClick={() => void fetchNextPage()}
          disabled={isFetchingNextPage}
        >
          {isFetchingNextPage ? "Loading…" : "Load more"}
        </button>
      )}
    </div>
  );
}
