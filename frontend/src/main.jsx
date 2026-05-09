import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";

// Initialize React application with StrictMode for development safety
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
