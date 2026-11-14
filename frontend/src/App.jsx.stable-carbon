import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, Activity, Search, RefreshCw, AlertTriangle, 
  Send, KeyRound, Zap, ChevronRight, Database, TrendingUp, Users,
  BarChart3, Filter, Radio, ShieldCheck, Terminal
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';
const WS_BASE = 'ws://127.0.0.1:8000/ws/feed';

const api = async (path, method = 'GET', body = null, token = null) => {
  const headers = { 'Content-Type': 'application/json' };
  const auth = token || localStorage.getItem('token');
  if (auth) headers['Authorization'] = `Bearer ${auth}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    ...(body ? { body: JSON.stringify(body) } : {})
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = Array.isArray(data.detail)
      ? data.detail.map(d => `${d.loc ? d.loc.slice(-1)[0] : 'field'}: ${d.msg}`).join(', ')
      : (data.detail || `HTTP Error ${res.status}`);
    throw new Error(msg);
  }
  return data;
};

const VECTOR_CONFIG = {
  fraud: { label: 'Fraud Scam', color: '#f43f5e', badge: 'bg-rose-500/10 text-rose-400 border-rose-500/20' },
  phishing: { label: 'Phishing', color: '#f59e0b', badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  impersonation: { label: 'Impersonation', color: '#a855f7', badge: 'bg-purple-500/10 text-purple-400 border-purple-500/20' },
  harassment: { label: 'Harassment', color: '#38bdf8', badge: 'bg-sky-500/10 text-sky-400 border-sky-500/20' },
  spam: { label: 'Spam Call', color: '#ef4444', badge: 'bg-red-500/10 text-red-400 border-red-500/20' },
};

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token') || '');
  const [reports, setReports] = useState([]);
  const [wsStatus, setWsStatus] = useState('Connecting');

  const [metrics, setMetrics] = useState({
    total_reports: 0,
    total_identities: 0,
    high_risk_identities: 0,
    reports_per_min: 0,
    active_subscribers: 1,
    categories: {}
  });

  const [auth, setAuth] = useState({ email: 'analyst@riskly.dev', password: 'analyst123' });
  const [authErr, setAuthErr] = useState('');

  const [rep, setRep] = useState({
    contact_type: 'phone',
    contact_value: '+919876543210',
    report_type: 'fraud',
    description: 'Fake lottery prize scam call requesting OTP verification.',
    evidence: ''
  });
  const [submitStatus, setSubmitStatus] = useState({ msg: '', err: false });
  const [loading, setLoading] = useState(false);

  const [search, setSearch] = useState({ type: 'auto', value: '' });
  const [scanRes, setScanRes] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanErr, setScanErr] = useState('');

  const [feedFilter, setFeedFilter] = useState('ALL');

  const wsRef = useRef(null);

  const fetchMetrics = async () => {
    try {
      const data = await api('/reports/analytics/summary');
      setMetrics(data);
    } catch (e) {}
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let t;
    const connect = () => {
      const ws = new WebSocket(WS_BASE);
      wsRef.current = ws;
      ws.onopen = () => setWsStatus('Online');
      ws.onmessage = (e) => {
        try {
          const item = JSON.parse(e.data);
          setReports(prev => [item, ...prev.slice(0, 49)]);
          setMetrics(prev => {
            const cat = (item.report_type || 'fraud').toLowerCase();
            const currCats = { ...prev.categories };
            currCats[cat] = (currCats[cat] || 0) + 1;
            return {
              ...prev,
              total_reports: prev.total_reports + 1,
              categories: currCats
            };
          });
        } catch {}
      };
      ws.onclose = () => {
        setWsStatus('Reconnecting');
        t = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
    };
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      clearTimeout(t);
    };
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthErr('');
    try {
      const data = await api('/auth/login', 'POST', {
        email: auth.email.trim(),
        password: auth.password.trim()
      });
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setAuthErr(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
  };

  const handleReport = async (e) => {
    e.preventDefault();
    const val = rep.contact_value.trim();
    if (!val) return setSubmitStatus({ msg: 'Please specify an entity value.', err: true });

    setLoading(true);
    setSubmitStatus({ msg: 'Dispatching incident...', err: false });

    try {
      await api('/reports', 'POST', {
        ...rep,
        contact_value: val,
        description: rep.description.trim() || 'Manual incident submission',
        evidence: rep.evidence.trim() || null
      }, token);

      setSubmitStatus({ msg: 'Incident report verified and logged.', err: false });
      fetchMetrics();
      setTimeout(() => setSubmitStatus({ msg: '', err: false }), 4000);
    } catch (err) {
      setSubmitStatus({ msg: err.message, err: true });
    } finally {
      setLoading(false);
    }
  };

  const triggerSearch = async (val, type = 'auto') => {
    const queryVal = (val || search.value).trim();
    if (!queryVal) return;

    setScanLoading(true);
    setScanErr('');

    try {
      const params = new URLSearchParams({ contact_value: queryVal });
      if (type && type !== 'auto') params.append('contact_type', type);

      const data = await api(`/reports/reputation?${params.toString()}`, 'GET', null, token);
      setScanRes(data);
    } catch (err) {
      setScanErr(err.message);
    } finally {
      setScanLoading(false);
    }
  };

  const totalCatReports = Object.values(metrics.categories || {}).reduce((a, b) => a + b, 0) || 1;

  const filteredReports = reports.filter(item => {
    if (feedFilter === 'ALL') return true;
    if (feedFilter === 'HIGH_RISK') return (item.ml_risk_score >= 50 || item.urgency_level?.toLowerCase() === 'high');
    return (item.report_type || '').toLowerCase() === feedFilter.toLowerCase();
  });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#08090e' }}>
      
      {/* Top Navbar */}
      <header style={{ 
        borderBottom: '1px solid rgba(255, 255, 255, 0.07)', 
        background: 'rgba(12, 14, 22, 0.95)',
        backdropFilter: 'blur(12px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)'
          }}>
            <ShieldAlert style={{ width: '16px', height: '16px', color: '#fff' }} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '15px', fontWeight: '700', letterSpacing: '-0.02em', color: '#f8fafc' }}>RISKLY</span>
              <span style={{ 
                fontSize: '10px', 
                fontWeight: '600', 
                background: 'rgba(99, 102, 241, 0.12)', 
                color: '#818cf8', 
                border: '1px solid rgba(99, 102, 241, 0.25)', 
                padding: '2px 6px', 
                borderRadius: '4px' 
              }}>SOC TERMINAL</span>
            </div>
            <p style={{ fontSize: '11px', color: '#64748b', marginTop: '1px' }}>Personal Fraud Risk Intelligence Engine</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px', 
            background: '#121522', 
            border: '1px solid rgba(255, 255, 255, 0.06)',
            padding: '5px 12px',
            borderRadius: '6px'
          }}>
            <span style={{ 
              width: '7px', 
              height: '7px', 
              borderRadius: '50%', 
              backgroundColor: wsStatus === 'Online' ? '#10b981' : '#f59e0b',
              boxShadow: wsStatus === 'Online' ? '0 0 8px #10b981' : 'none'
            }} />
            <span className="font-mono" style={{ fontSize: '11px', color: '#94a3b8' }}>Pipeline: {wsStatus}</span>
          </div>

          {token ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ 
                fontSize: '11px', 
                background: 'rgba(16, 185, 129, 0.1)', 
                color: '#34d399', 
                border: '1px solid rgba(16, 185, 129, 0.2)', 
                padding: '4px 10px', 
                borderRadius: '6px',
                fontWeight: '600'
              }}>Analyst Session Active</span>
              <button 
                onClick={handleLogout}
                style={{
                  background: '#191f33',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  color: '#cbd5e1',
                  fontSize: '11px',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >Sign Out</button>
            </div>
          ) : (
            <span style={{ 
              fontSize: '11px', 
              background: 'rgba(245, 158, 11, 0.1)', 
              color: '#fbbf24', 
              border: '1px solid rgba(245, 158, 11, 0.2)', 
              padding: '4px 10px', 
              borderRadius: '6px' 
            }}>Read-Only View</span>
          )}
        </div>
      </header>

      {/* Global Executive Metric Strip */}
      <section style={{ 
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)', 
        background: '#0b0d15', 
        padding: '14px 24px' 
      }}>
        <div style={{ 
          maxWidth: '1280px', 
          margin: '0 auto', 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', 
          gap: '12px' 
        }}>
          
          <div className="risk-card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ padding: '8px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '8px', color: '#818cf8' }}>
              <Database style={{ width: '18px', height: '18px' }} />
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Ingested Reports</span>
              <p className="font-mono" style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc', marginTop: '2px' }}>
                {metrics.total_reports.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="risk-card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ padding: '8px', background: 'rgba(244, 63, 94, 0.1)', borderRadius: '8px', color: '#fb7185' }}>
              <AlertTriangle style={{ width: '18px', height: '18px' }} />
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Flagged Entities</span>
              <p className="font-mono" style={{ fontSize: '18px', fontWeight: '700', color: '#fb7185', marginTop: '2px' }}>
                {metrics.high_risk_identities.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="risk-card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ padding: '8px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px', color: '#fbbf24' }}>
              <TrendingUp style={{ width: '18px', height: '18px' }} />
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Event Velocity</span>
              <p className="font-mono" style={{ fontSize: '18px', fontWeight: '700', color: '#fbbf24', marginTop: '2px' }}>
                {metrics.reports_per_min} <span style={{ fontSize: '10px', color: '#64748b', fontWeight: '400' }}>req/min</span>
              </p>
            </div>
          </div>

          <div className="risk-card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ padding: '8px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', color: '#34d399' }}>
              <Radio style={{ width: '18px', height: '18px' }} />
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Live Stream Nodes</span>
              <p className="font-mono" style={{ fontSize: '18px', fontWeight: '700', color: '#34d399', marginTop: '2px' }}>
                {metrics.active_subscribers}
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* Main Command Dashboard */}
      <main style={{ 
        maxWidth: '1280px', 
        width: '100%', 
        margin: '0 auto', 
        padding: '24px', 
        display: 'grid', 
        gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', 
        gap: '20px', 
        flex: 1 
      }}>
        
        {/* Column 1: Universal Scanner & Ingestion Stream */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* Universal Reputation Scanner */}
          <div className="risk-card" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Search style={{ width: '15px', height: '15px', color: '#818cf8' }} />
                <span style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#e2e8f0' }}>Universal Threat Lookup</span>
              </div>
              <span className="font-mono" style={{ 
                fontSize: '10px', 
                background: 'rgba(99, 102, 241, 0.1)', 
                color: '#818cf8', 
                border: '1px solid rgba(99, 102, 241, 0.2)', 
                padding: '3px 8px', 
                borderRadius: '4px' 
              }}>AUTO-INDEX ACTIVE</span>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); triggerSearch(); }} style={{ display: 'flex', gap: '8px' }}>
              <select
                value={search.type}
                onChange={(e) => setSearch(s => ({ ...s, type: e.target.value }))}
                className="risk-input"
                style={{ fontSize: '12px', padding: '9px 12px', cursor: 'pointer' }}
              >
                <option value="auto">AUTO</option>
                <option value="phone">PHONE</option>
                <option value="upi">UPI ID</option>
                <option value="email">EMAIL</option>
                <option value="bank_account">BANK ACC</option>
                <option value="url">DOMAIN/URL</option>
              </select>

              <input
                type="text"
                value={search.value}
                onChange={(e) => setSearch(s => ({ ...s, value: e.target.value }))}
                placeholder="Query phone, UPI, email, bank account, or scam domain..."
                className="risk-input font-mono"
                style={{ flex: 1, fontSize: '12px', padding: '9px 14px' }}
              />

              <button
                type="submit"
                disabled={scanLoading}
                style={{
                  background: '#4f46e5',
                  border: 'none',
                  color: '#ffffff',
                  fontSize: '12px',
                  fontWeight: '600',
                  padding: '9px 18px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'background 0.15s ease'
                }}
              >
                {scanLoading ? <RefreshCw style={{ width: '14px', height: '14px', animation: 'spin 1s linear infinite' }} /> : 'Analyze'}
              </button>
            </form>

            {scanErr && <p style={{ fontSize: '11px', color: '#fb7185', marginTop: '10px' }}>{scanErr}</p>}

            {/* Diagnostic Scorecard */}
            {scanRes && (
              <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="font-mono" style={{ fontSize: '13px', fontWeight: '600', color: '#f8fafc' }}>{scanRes.normalized_value}</span>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', background: '#1c2236', color: '#94a3b8', padding: '2px 6px', borderRadius: '4px' }}>
                      {scanRes.contact_type}
                    </span>
                  </div>
                  {scanRes.found ? (
                    <span style={{ fontSize: '10px', color: '#34d399', background: 'rgba(16, 185, 129, 0.1)', padding: '2px 8px', borderRadius: '4px', fontWeight: '600' }}>
                      Profile Identified
                    </span>
                  ) : (
                    <span style={{ fontSize: '10px', color: '#94a3b8', background: '#1c2236', padding: '2px 8px', borderRadius: '4px' }}>
                      Unseen Entity
                    </span>
                  )}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
                  <div style={{ background: '#131726', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <span style={{ fontSize: '10px', color: '#64748b', display: 'block' }}>Risk Score</span>
                    <span className="font-mono" style={{ fontSize: '16px', fontWeight: '700', color: scanRes.score >= 50 ? '#fb7185' : '#34d399' }}>
                      {scanRes.score}<span style={{ fontSize: '10px', color: '#64748b' }}>/100</span>
                    </span>
                  </div>

                  <div style={{ background: '#131726', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <span style={{ fontSize: '10px', color: '#64748b', display: 'block' }}>Urgency</span>
                    <span className="font-mono" style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', color: scanRes.risk_level === 'HIGH' ? '#fb7185' : '#fbbf24', marginTop: '4px', display: 'inline-block' }}>
                      {scanRes.risk_level || 'LOW'}
                    </span>
                  </div>

                  <div style={{ background: '#131726', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <span style={{ fontSize: '10px', color: '#64748b', display: 'block' }}>Reports</span>
                    <span className="font-mono" style={{ fontSize: '16px', fontWeight: '700', color: '#818cf8' }}>
                      {scanRes.report_count ?? 0}
                    </span>
                  </div>

                  <div style={{ background: '#131726', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255, 255, 0.04)' }}>
                    <span style={{ fontSize: '10px', color: '#64748b', display: 'block' }}>Recidivism</span>
                    <span className="font-mono" style={{ fontSize: '16px', fontWeight: '700', color: '#fbbf24' }}>
                      {scanRes.recidivism_multiplier ? `${scanRes.recidivism_multiplier}x` : '1.0x'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Live Ingestion Stream */}
          <div className="risk-card" style={{ padding: '18px', display: 'flex', flexDirection: 'column', flex: 1, minHeight: '480px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity style={{ width: '15px', height: '15px', color: '#38bdf8' }} />
                <span style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#e2e8f0' }}>Live Ingestion Stream</span>
              </div>
              <span style={{ fontSize: '11px', color: '#64748b' }}>Real-time telemetry intake</span>
            </div>

            {/* Filter Pills */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px', overflowX: 'auto', paddingBottom: '4px' }}>
              <span style={{ fontSize: '10px', color: '#64748b', marginRight: '4px' }}>Filter:</span>
              {['ALL', 'HIGH_RISK', 'fraud', 'phishing', 'impersonation'].map(filterKey => (
                <button
                  key={filterKey}
                  onClick={() => setFeedFilter(filterKey)}
                  style={{
                    fontSize: '11px',
                    fontWeight: feedFilter === filterKey ? '600' : '400',
                    background: feedFilter === filterKey ? '#4f46e5' : '#141827',
                    border: '1px solid',
                    borderColor: feedFilter === filterKey ? '#6366f1' : 'rgba(255, 255, 255, 0.06)',
                    color: feedFilter === filterKey ? '#ffffff' : '#94a3b8',
                    padding: '3px 10px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    textTransform: 'uppercase'
                  }}
                >
                  {filterKey === 'HIGH_RISK' ? 'Critical' : filterKey}
                </button>
              ))}
            </div>

            {/* Stream Scroll Container */}
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '460px' }}>
              {filteredReports.length === 0 ? (
                <div style={{ margin: 'auto', textAlign: 'center', color: '#64748b', fontSize: '12px' }}>
                  Awaiting threat signals from stream...
                </div>
              ) : (
                filteredReports.map((item, idx) => {
                  const conf = VECTOR_CONFIG[(item.report_type || 'fraud').toLowerCase()] || VECTOR_CONFIG.fraud;
                  return (
                    <div 
                      key={idx}
                      onClick={() => { setSearch({ type: 'auto', value: item.contact_value }); triggerSearch(item.contact_value); }}
                      style={{
                        background: '#121522',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        borderRadius: '8px',
                        padding: '12px 14px',
                        cursor: 'pointer',
                        transition: 'border-color 0.15s ease'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)'}
                      onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)'}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span className="font-mono" style={{ fontSize: '12px', fontWeight: '600', color: '#f8fafc' }}>
                            {item.contact_value}
                          </span>
                          <span style={{ fontSize: '9px', background: '#1c2236', color: '#94a3b8', padding: '1px 5px', borderRadius: '3px', textTransform: 'uppercase' }}>
                            {item.contact_type}
                          </span>
                        </div>
                        <span style={{ 
                          fontSize: '10px', 
                          fontWeight: '600', 
                          color: conf.color, 
                          background: `${conf.color}15`, 
                          border: `1px solid ${conf.color}30`, 
                          padding: '2px 7px', 
                          borderRadius: '4px',
                          textTransform: 'uppercase'
                        }}>
                          {item.report_type}
                        </span>
                      </div>

                      {item.description && (
                        <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.4', marginBottom: '8px' }}>
                          {item.description}
                        </p>
                      )}

                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '10px', color: '#64748b', borderTop: '1px solid rgba(255, 255, 255, 0.04)', paddingTop: '6px' }}>
                        <span>ML Confidence: <strong style={{ color: '#cbd5e1' }}>{item.ml_risk_score ?? 0}%</strong></span>
                        <span>Urgency: <strong style={{ color: '#cbd5e1' }}>{item.urgency_level ?? 'Standard'}</strong></span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

        </div>

        {/* Column 2: Vector Analytics & Incident Submission */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* Threat Vector Distribution */}
          <div className="risk-card" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart3 style={{ width: '15px', height: '15px', color: '#818cf8' }} />
                <span style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#e2e8f0' }}>Threat Vectors</span>
              </div>
              <span className="font-mono" style={{ fontSize: '10px', color: '#64748b' }}>AGGREGATED</span>
            </div>

            {/* Stacked Proportional Spectrum */}
            <div style={{ 
              height: '8px', 
              width: '100%', 
              background: '#141827', 
              borderRadius: '999px', 
              overflow: 'hidden', 
              display: 'flex', 
              marginBottom: '14px' 
            }}>
              {Object.keys(VECTOR_CONFIG).map(cat => {
                const count = metrics.categories?.[cat] || 0;
                const pct = ((count / totalCatReports) * 100).toFixed(1);
                if (count === 0) return null;
                return (
                  <div
                    key={cat}
                    style={{ width: `${pct}%`, background: VECTOR_CONFIG[cat].color }}
                    title={`${cat.toUpperCase()}: ${pct}%`}
                  />
                );
              })}
            </div>

            {/* Breakdown List */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
              {Object.entries(VECTOR_CONFIG).map(([cat, conf]) => {
                const count = metrics.categories?.[cat] || 0;
                const pct = Math.round((count / totalCatReports) * 100);
                return (
                  <div key={cat} style={{ background: '#121522', padding: '10px 12px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '11px', fontWeight: '600', color: conf.color }}>{conf.label}</span>
                      <span className="font-mono" style={{ fontSize: '10px', color: '#64748b' }}>{pct}%</span>
                    </div>
                    <span className="font-mono" style={{ fontSize: '14px', fontWeight: '700', color: '#f8fafc' }}>
                      {count.toLocaleString()}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Submit Fraud Incident */}
          <div className="risk-card" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <AlertTriangle style={{ width: '15px', height: '15px', color: '#f59e0b' }} />
              <span style={{ fontSize: '12px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#e2e8f0' }}>Dispatch Incident Log</span>
            </div>
            <p style={{ fontSize: '11px', color: '#64748b', marginBottom: '14px' }}>Inject verifiable threat data into intelligence stream.</p>

            <form onSubmit={handleReport} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <label style={{ fontSize: '10px', color: '#64748b', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>Target Medium</label>
                  <select
                    value={rep.contact_type}
                    onChange={(e) => setRep(r => ({ ...r, contact_type: e.target.value }))}
                    className="risk-input"
                    style={{ width: '100%', fontSize: '11px', padding: '8px 10px' }}
                  >
                    {['phone', 'email', 'upi', 'bank_account', 'url'].map(t => (
                      <option key={t} value={t}>{t.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '10px', color: '#64748b', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>Category</label>
                  <select
                    value={rep.report_type}
                    onChange={(e) => setRep(r => ({ ...r, report_type: e.target.value }))}
                    className="risk-input"
                    style={{ width: '100%', fontSize: '11px', padding: '8px 10px' }}
                  >
                    <option value="fraud">Fraud (+30)</option>
                    <option value="phishing">Phishing (+25)</option>
                    <option value="spam">Spam (+10)</option>
                    <option value="impersonation">Impersonation (+35)</option>
                    <option value="harassment">Harassment (+20)</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '10px', color: '#64748b', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>Entity Identifier</label>
                <input
                  type="text"
                  value={rep.contact_value}
                  onChange={(e) => setRep(r => ({ ...r, contact_value: e.target.value }))}
                  placeholder="+919876543210 or user@okhdfcbank"
                  className="risk-input font-mono"
                  style={{ width: '100%', fontSize: '11px', padding: '8px 10px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '10px', color: '#64748b', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>Incident Summary</label>
                <textarea
                  value={rep.description}
                  onChange={(e) => setRep(r => ({ ...r, description: e.target.value }))}
                  rows={2}
                  className="risk-input"
                  style={{ width: '100%', fontSize: '11px', padding: '8px 10px', resize: 'none' }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  background: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
                  border: 'none',
                  color: '#ffffff',
                  fontSize: '12px',
                  fontWeight: '600',
                  padding: '10px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  marginTop: '4px',
                  boxShadow: '0 4px 12px rgba(79, 70, 229, 0.25)'
                }}
              >
                {loading ? <RefreshCw style={{ width: '14px', height: '14px', animation: 'spin 1s linear infinite' }} /> : <>
                  <Send style={{ width: '13px', height: '13px' }} />
                  <span>Transmit Report Log</span>
                </>}
              </button>

              {submitStatus.msg && (
                <p style={{ fontSize: '11px', textAlign: 'center', marginTop: '4px', color: submitStatus.err ? '#fb7185' : '#34d399' }}>
                  {submitStatus.msg}
                </p>
              )}
            </form>
          </div>

          {/* Analyst Authentication */}
          <div className="risk-card" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <KeyRound style={{ width: '14px', height: '14px', color: '#818cf8' }} />
              <span style={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#cbd5e1' }}>Operator Credentials</span>
            </div>

            {token ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#121522', padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <div>
                  <span style={{ fontSize: '10px', color: '#64748b', display: 'block' }}>Signed in</span>
                  <span className="font-mono" style={{ fontSize: '11px', color: '#34d399', fontWeight: '600' }}>{auth.email}</span>
                </div>
                <button
                  onClick={handleLogout}
                  style={{
                    background: 'transparent',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#94a3b8',
                    fontSize: '10px',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >Revoke</button>
              </div>
            ) : (
              <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <input
                  type="email"
                  value={auth.email}
                  onChange={(e) => setAuth(a => ({ ...a, email: e.target.value }))}
                  placeholder="analyst@riskly.dev"
                  className="risk-input"
                  style={{ fontSize: '11px', padding: '7px 10px' }}
                />
                <input
                  type="password"
                  value={auth.password}
                  onChange={(e) => setAuth(a => ({ ...a, password: e.target.value }))}
                  placeholder="Password"
                  className="risk-input"
                  style={{ fontSize: '11px', padding: '7px 10px' }}
                />
                {authErr && <p style={{ fontSize: '10px', color: '#fb7185' }}>{authErr}</p>}
                <button
                  type="submit"
                  style={{
                    background: '#1e2438',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    color: '#e2e8f0',
                    fontSize: '11px',
                    fontWeight: '600',
                    padding: '8px',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >Authenticate Session</button>
              </form>
            )}
          </div>

        </div>

      </main>
    </div>
  );
}

