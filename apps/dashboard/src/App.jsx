import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import L from "leaflet";
import { Activity, AlertTriangle, CheckCircle2, ChevronRight, Crosshair, Radio, RefreshCw, ShieldCheck, Siren, Users } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const API = "/api/v1";
const COLORS = { NORMAL: "#36d399", WATCH: "#fbbd23", WARNING: "#fb923c", CRITICAL: "#f43f5e", OFFLINE: "#64748b" };
const LABELS = { SENSOR_ANOMALY: "Sensor pattern exceeds baseline", DISPLACEMENT_RISING: "Displacement is elevated", TILT_CHANGE: "Tilt change detected", VIBRATION_SPIKE: "Vibration spike detected", NEIGHBOUR_CORRELATION: "Neighbour node confirms pattern", LOW_SENSOR_HEALTH: "Reduced sensor health" };

function MineMap({ nodes, selected, onSelect }) {
  const host = useRef(null); const map = useRef(null); const markers = useRef([]);
  useEffect(() => {
    if (!host.current || map.current) return;
    map.current = L.map(host.current, { crs: L.CRS.Simple, minZoom: 0, maxZoom: 2, zoomControl: false, attributionControl: false }).setView([50, 50], 0);
    L.control.zoom({ position: "bottomright" }).addTo(map.current);
    L.rectangle([[6, 5], [94, 95]], { color: "#26364d", weight: 1, fillColor: "#0b1423", fillOpacity: 1 }).addTo(map.current);
    [[18,12,82,26],[28,26,72,40],[38,40,62,55],[26,55,76,70],[16,70,86,86]].forEach(([a,b,c,d], i) => L.rectangle([[a,b],[c,d]], { color: "#263e58", weight: 1, dashArray: i===2 ? "5 5" : undefined, fillColor: i===2 ? "#0f2f34" : "#101d2e", fillOpacity: .9 }).addTo(map.current));
    L.polyline([[50,8],[50,92]], { color: "#314862", weight: 3 }).addTo(map.current);
    return () => { map.current?.remove(); map.current = null; };
  }, []);
  useEffect(() => {
    if (!map.current) return; markers.current.forEach(m => m.remove()); markers.current = nodes.map(node => {
      const state = node.reading?.decision?.state || "OFFLINE"; const color = COLORS[state]; const icon = L.divIcon({ className: "", html: `<div class="map-node ${selected===node.node_id?"selected":""}" style="--node:${color}"><span>${node.node_id.slice(-1)}</span><i></i></div>`, iconSize: [44,44] });
      return L.marker([node.position[1], node.position[0]], { icon }).addTo(map.current).on("click", () => onSelect(node.node_id));
    });
  }, [nodes, selected, onSelect]);
  return <div ref={host} className="mine-map" />;
}

function Gauge({ value, label, color }) {
  return <div className="gauge" style={{"--value": `${value*3.6}deg`, "--color": color}}><div><strong>{Math.round(value)}</strong><span>{label}</span></div></div>;
}

function App() {
  const [overview, setOverview] = useState({ nodes: [], incidents: [], units: [] });
  const [history, setHistory] = useState([]); const [selected, setSelected] = useState("NODE_A"); const [busy, setBusy] = useState(false); const [connected, setConnected] = useState(false);
  const refresh = useCallback(async () => { try { const [o,h] = await Promise.all([fetch(`${API}/overview`), fetch(`${API}/readings`)]); if (!o.ok || !h.ok) throw new Error(); setOverview(await o.json()); setHistory(await h.json()); setConnected(true); } catch { setConnected(false); } }, []);
  useEffect(() => { refresh(); const timer = setInterval(refresh, 4000); return () => clearInterval(timer); }, [refresh]);
  const run = async scenario => { setBusy(true); try { await fetch(`${API}/demo/${scenario}`, { method: "POST" }); await refresh(); } finally { setBusy(false); } };
  const node = overview.nodes.find(n => n.node_id === selected) || overview.nodes[0]; const reading = node?.reading; const decision = reading?.decision || { state: "OFFLINE", risk: 0, confidence: 0, trend: "INSUFFICIENT_DATA", reason_codes: [] }; const sensors = reading?.packet?.sensors || {};
  const chart = useMemo(() => history.filter(x => x.packet.node_id === selected).reverse().map((x,i) => ({ n: i+1, risk: x.decision.risk, confidence: x.decision.confidence })), [history, selected]);
  const activeIncident = overview.incidents.find(i => i.node_id === selected && i.status !== "RESOLVED");
  const dispatch = async unit => { if (!activeIncident) return; await fetch(`${API}/incidents/${activeIncident.id}/dispatch?unit=${unit}`, { method: "POST" }); refresh(); };
  return <main>
    <header><div className="brand"><div className="brandmark"><Crosshair size={22}/></div><div><strong>SMART-MINE <em>AI</em></strong><span>Geo-Sentry Command Centre</span></div></div><div className="header-status"><span className="prototype">PROTOTYPE</span><span className={connected?"live":"offline"}><i></i>{connected?"SYSTEM LIVE":"API OFFLINE"}</span><span className="clock">LOCAL CONTROL • CHENNAI</span></div></header>
    <section className="hero"><div><span className="eyebrow"><ShieldCheck size={14}/> GROUND-INSTABILITY DECISION SUPPORT</span><h1>Underground Risk Intelligence</h1><p>Geometry-aware sensing • explainable decisions • intelligent inspection dispatch</p></div><div className="scenario"><span>DEMO SCENARIO</span>{["normal","warning","critical","sensor_failure"].map(s=><button key={s} disabled={busy} onClick={()=>run(s)}>{s.replace("_"," ")}</button>)}<button className="refresh" onClick={refresh}><RefreshCw size={15}/></button></div></section>
    <section className="grid">
      <article className="panel map-panel"><div className="panel-title"><div><span>SPATIAL INTELLIGENCE</span><h2>Mine Panel Overview</h2></div><span className="legend"><i></i> Active face</span></div><MineMap nodes={overview.nodes} selected={selected} onSelect={setSelected}/><div className="map-caption"><span><Radio size={14}/> 2 sensor nodes</span><span>Local XY geometry • no underground GNSS</span></div></article>
      <article className="panel status-panel"><div className="panel-title"><div><span>SELECTED ASSET</span><h2>{selected.replace("_", " ")}</h2></div><span className="state" style={{color:COLORS[decision.state],borderColor:COLORS[decision.state]}}>{decision.state}</span></div><div className="gauges"><Gauge value={decision.risk} label="RISK" color={COLORS[decision.state]}/><Gauge value={decision.confidence} label="CONFIDENCE" color="#38bdf8"/></div><div className="trend"><Activity size={17}/><div><span>TREND PROJECTION</span><strong>{decision.trend.replaceAll("_"," ")}</strong></div></div><div className="sensor-grid"><div><span>DISPLACEMENT</span><strong>{sensors.displacement_mm ?? "—"}<small> mm</small></strong></div><div><span>VIBRATION</span><strong>{sensors.vibration_g ?? "—"}<small> g</small></strong></div><div><span>TILT X</span><strong>{sensors.tilt_x_deg ?? "—"}<small>°</small></strong></div><div><span>NODE HEALTH</span><strong className={node?.online?"good":"bad"}>{node?.online?"ONLINE":"NO DATA"}</strong></div></div></article>
      <article className="panel chart-panel"><div className="panel-title"><div><span>VALIDATED HISTORY</span><h2>Risk & Confidence</h2></div><span className="window">LAST {chart.length} READINGS</span></div><div className="chart"><ResponsiveContainer><AreaChart data={chart}><defs><linearGradient id="risk" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#f43f5e" stopOpacity={.45}/><stop offset="100%" stopColor="#f43f5e" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#203047" strokeDasharray="3 3"/><XAxis dataKey="n" hide/><YAxis domain={[0,100]} tick={{fill:"#637690",fontSize:10}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:"#0d1828",border:"1px solid #26364d"}}/><Area type="monotone" dataKey="risk" stroke="#f43f5e" fill="url(#risk)" strokeWidth={2}/><Area type="monotone" dataKey="confidence" stroke="#38bdf8" fill="transparent" strokeWidth={2}/></AreaChart></ResponsiveContainer></div><div className="chart-key"><span><i className="riskdot"></i>Risk</span><span><i className="confdot"></i>Confidence</span></div></article>
      <article className="panel explain-panel"><div className="panel-title"><div><span>EXPLAINABLE DECISION</span><h2>Why this state?</h2></div><AlertTriangle size={20} color={COLORS[decision.state]}/></div><div className="reasons">{decision.reason_codes.length ? decision.reason_codes.map(reason=><div key={reason}><CheckCircle2 size={16}/><span>{LABELS[reason] || reason.replaceAll("_"," ")}</span><ChevronRight size={14}/></div>) : <div className="empty"><CheckCircle2 size={16}/> No abnormal evidence detected</div>}</div><p className="notice">Decision support only. Follow approved mine safety procedures and authorized personnel.</p></article>
      <article className="panel dispatch-panel"><div className="panel-title"><div><span>SUPERVISORY ORCHESTRATOR</span><h2>Incident & Dispatch</h2></div><Siren size={20} color={activeIncident?"#fb923c":"#36d399"}/></div><div className="incident"><span>{activeIncident?`INC-${String(activeIncident.id).padStart(3,"0")}`:"NO ACTIVE INCIDENT"}</span><strong>{activeIncident?.status || "MONITORING"}</strong></div><div className="units">{overview.units.map(unit=><button key={unit.id} onClick={()=>dispatch(unit.id)} disabled={!activeIncident}><Users size={17}/><span>UNIT {unit.id}<small>{activeIncident?.assigned_unit===unit.id?"DISPATCHED":"AVAILABLE"}</small></span><ChevronRight size={15}/></button>)}</div></article>
    </section><footer><span>BHARATNEX • SIH 2026 PROTOTYPE</span><span>FastAPI + SQLite + React + Leaflet + Recharts</span><span>Not a certified industrial safety system</span></footer>
  </main>;
}

export default App;
