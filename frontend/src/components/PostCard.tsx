import { Link } from "react-router-dom";
import type { Post } from "../types";

const PREVIEW_LENGTH = 180;

export function PostCard({ post }: { post: Post }) {
  const preview =
    post.summary ??
    (post.content.length > PREVIEW_LENGTH
      ? `${post.content.slice(0, PREVIEW_LENGTH)}…`
      : post.content);

  return (
    <article className="post-card">
      <h2>
        <Link to={`/posts/${post.id}`}>{post.title}</Link>
      </h2>
      <p className="post-meta">
        by <Link to={`/users/${post.author.username}`}>@{post.author.username}</Link> ·{" "}
        {new Date(post.created_at).toLocaleDateString()}
        {post.summary && <span className="ai-badge" title="AI-generated summary"> ✨ AI</span>}
      </p>
      <p>{preview}</p>
      {post.tags && post.tags.length > 0 && <TagChips tags={post.tags} />}
    </article>
  );
}

export function TagChips({ tags }: { tags: string[] }) {
  return (
    <div className="tag-chips">
      {tags.map((tag) => (
        <span key={tag} className="tag-chip">
          {tag}
        </span>
      ))}
    </div>
  );
}
