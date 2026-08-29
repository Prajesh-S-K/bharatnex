# SMART-MINE command dashboard

The prototype interface uses React, Vite, Leaflet and Recharts. It displays the two
fixed local-XY sensor nodes, separate Risk and Confidence, sensor values, trend,
deterministic reasons, incidents and Alpha/Bravo dispatch.

```bash
npm install
npm run dev
```

Run the API on port 8000 first. Vite proxies `/api` to the local FastAPI process.

Owned by the Full Stack workstream. Build one React/Vite command view using Leaflet and Recharts. Consume API decisions; do not recalculate Risk or Confidence in the browser.
