import React from "react";
import ReactDOM from "react-dom/client";
import "leaflet/dist/leaflet.css";
import "./styles.css";
import App from "./App";
import InspectionApp from "./InspectionApp";
import "./inspection.css";
import "./operator.css";

const rootElement = window.location.pathname.startsWith("/inspection") ? <InspectionApp /> : <App />;

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/service-worker.js"));
}

ReactDOM.createRoot(document.getElementById("root")).render(<React.StrictMode>{rootElement}</React.StrictMode>);
