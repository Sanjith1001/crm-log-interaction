import { useState } from "react";
import { useDispatch } from "react-redux";
import { setCurrentPage } from "../store/slices/uiSlice";
import "./pages.css";

export function LoginPage() {
  const dispatch = useDispatch();
  const [email, setEmail] = useState("demo.rep@pharma.com");
  const [password, setPassword] = useState("password");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password) {
      dispatch(setCurrentPage("log"));
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-logo" />
        <h2 className="login-title">Welcome to Aegis CRM</h2>
        <p className="login-subtitle">AI-First Healthcare Representative Console</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="login-btn">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
export default LoginPage;
