import { useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiErrorMessage } from "../api/client";
import { TagChips } from "../components/PostCard";
import { useAuth } from "../context/AuthContext";
import {
  useDeletePost,
  usePost,
  useRegenerateAi,
  useUpdatePost,
} from "../hooks/usePosts";
import { Link } from "react-router-dom";

export function PostPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const { user } = useAuth();
  const navigate = useNavigate();

  const { data: post, error, isPending } = usePost(id);
  const updateMutation = useUpdatePost(id);
  const deleteMutation = useDeletePost(id);
  const regenMutation = useRegenerateAi(id);

  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  if (!Number.isInteger(id)) return <p className="error">Invalid post id</p>;
  if (isPending) return <p className="status">Loading post…</p>;
  if (error) return <p className="error">{apiErrorMessage(error)}</p>;

  const isAuthor = user?.id === post.author.id;

  function startEditing() {
    if (!post) return;
    setTitle(post.title);
    setContent(post.content);
    setEditing(true);
  }

  function handleUpdate(e: FormEvent) {
    e.preventDefault();
    updateMutation.mutate(
      { title, content },
      { onSuccess: () => setEditing(false) },
    );
  }

  function handleDelete() {
    if (!window.confirm("Delete this post? This cannot be undone.")) return;
    deleteMutation.mutate(undefined, { onSuccess: () => navigate("/") });
  }

  if (editing) {
    return (
      <form onSubmit={handleUpdate} className="form">
        <h1>Edit post</h1>
        <label>
          Title
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            minLength={3}
            maxLength={200}
            required
          />
        </label>
        <label>
          Content
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            minLength={10}
            rows={12}
            required
          />
        </label>
        {updateMutation.error && (
          <p className="error">{apiErrorMessage(updateMutation.error)}</p>
        )}
        <div className="button-row">
          <button type="submit" disabled={updateMutation.isPending}>
            {updateMutation.isPending ? "Saving…" : "Save"}
          </button>
          <button type="button" onClick={() => setEditing(false)}>
            Cancel
          </button>
        </div>
      </form>
    );
  }

  return (
    <article className="post-full">
      <h1>{post.title}</h1>
      <p className="post-meta">
        by <Link to={`/users/${post.author.username}`}>@{post.author.username}</Link> ·{" "}
        {new Date(post.created_at).toLocaleString()}
      </p>

      {post.summary && (
        <aside className="summary-box">
          <strong>✨ TL;DR</strong>
          <p>{post.summary}</p>
        </aside>
      )}
      {post.tags && post.tags.length > 0 && <TagChips tags={post.tags} />}

      <div className="post-content">{post.content}</div>

      {isAuthor && (
        <div className="button-row">
          <button type="button" onClick={startEditing}>
            Edit
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? "Deleting…" : "Delete"}
          </button>
          <button
            type="button"
            onClick={() => regenMutation.mutate()}
            disabled={regenMutation.isPending}
            title="Regenerate the AI summary and tags"
          >
            ✨ Regenerate AI
          </button>
        </div>
      )}
      {regenMutation.isSuccess && (
        <p className="status">AI regeneration queued — refreshing shortly…</p>
      )}
      {regenMutation.error && (
        <p className="error">{apiErrorMessage(regenMutation.error)}</p>
      )}
    </article>
  );
}
