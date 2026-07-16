import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { apiErrorMessage } from "../api/client";
import { useCreatePost } from "../hooks/usePosts";

export function WritePage() {
  const navigate = useNavigate();
  const createMutation = useCreatePost();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [clientError, setClientError] = useState<string | null>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (title.trim().length < 3) {
      setClientError("Title must be at least 3 characters");
      return;
    }
    if (content.trim().length < 10) {
      setClientError("Content must be at least 10 characters");
      return;
    }
    setClientError(null);
    createMutation.mutate(
      { title: title.trim(), content: content.trim() },
      { onSuccess: (post) => navigate(`/posts/${post.id}`) },
    );
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <h1>Write a post</h1>
      <label>
        Title
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          placeholder="A clear, descriptive title"
          required
        />
      </label>
      <label>
        Content
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={14}
          placeholder="Write your post… AI will generate the summary and tags."
          required
        />
      </label>
      {clientError && <p className="error">{clientError}</p>}
      {createMutation.error && (
        <p className="error">{apiErrorMessage(createMutation.error)}</p>
      )}
      <button type="submit" disabled={createMutation.isPending}>
        {createMutation.isPending ? "Publishing…" : "Publish"}
      </button>
    </form>
  );
}
