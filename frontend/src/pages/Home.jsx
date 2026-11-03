import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div>
      <h1>Welcome to CreatorFlow</h1>
      <p style={{ marginTop: "1rem", color: "var(--text-muted)" }}>
        A data-driven analytics platform for social media content creators.
        Upload your historical post data to get validation, analytics, sentiment
        analysis, and predictions about your future content.
      </p>

      <div style={{ marginTop: "2rem" }}>
        <Link to="/upload" className="btn btn-primary">
          Get Started → Upload CSV
        </Link>
      </div>
    </div>
  );
}