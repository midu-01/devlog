import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { RequireAuth } from "./components/RequireAuth";
import { AuthProvider } from "./context/AuthContext";
import { FeedPage } from "./pages/FeedPage";
import { LoginPage } from "./pages/LoginPage";
import { PostPage } from "./pages/PostPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { WritePage } from "./pages/WritePage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <main className="container">
          <Routes>
            <Route
              path="/"
              element={
                <RequireAuth>
                  <FeedPage />
                </RequireAuth>
              }
            />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/posts/:id" element={<PostPage />} />
            <Route
              path="/write"
              element={
                <RequireAuth>
                  <WritePage />
                </RequireAuth>
              }
            />
            <Route path="/users/:username" element={<ProfilePage />} />
            <Route path="*" element={<p className="error">Page not found</p>} />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
  );
}
