import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Activity, Search, RefreshCw, AlertTriangle, Send, KeyRound } from 'lucide-react';

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
      : (data.detail || HTTP );
    throw new Error(msg);
  }
  return data;
};

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token') || '');
  const [reports, setReports] = useState([]);
  const [wsStatus, setWsStatus] = useState('Connecting...');
  
  const [auth, setAuth] = useState({ email: 'analyst@riskly.dev', password: 'analyst123' });
  const [authErr, setAuthErr] = useState('');

  const [rep, setRep] = useState({
    contact_type: 'phone',
    contact_value: '+919876543210',
    report_type: 'fraud',
    description: 'Fake lottery prize scam call requesting OTP.',
    evidence: ''
  });
  const [submitStatus, setSubmitStatus] = useState({ msg: '', err: false });
  const [loading, setLoading] = useState(false);

  const [search, setSearch] = useState({ type: 'phone', value: '' });
  const [scanRes, setScanRes] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanErr, setScanErr] = useState('');

  const wsRef = useRef(null);

  useEffect(() => {
    let t;
    const connect = () => {
      const ws = new WebSocket(WS_BASE);
      wsRef.current = ws;
      ws.onopen = () => setWsStatus('Stream Active');
      ws.onmessage = (e) => {
        try {
          const item = JSON.parse(e.data);
          setReports(prev => [item, ...prev.slice(0, 49)]);
        } catch {}
      };
      ws.onclose = () => {
        setWsStatus('Reconnecting...');
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
    if (!val) return setSubmitStatus({ msg: 'Please provide an entity value.', err: true });

    setLoading(true);
    setSubmitStatus({ msg: 'Dispatching...', err: false });

    try {
      await api('/reports', 'POST', {
        ...rep,
        contact_value: val,
        description: rep.description.trim() || 'Manual incident submission',
        evidence: rep.evidence.trim() || null
      }, token);

      setSubmitStatus({ msg: 'Report successfully dispatched!', err: false });
      setTimeout(() => setSubmitStatus({ msg: '', err: false }), 4000);
    } catch (err) {
      setSubmitStatus({ msg: err.message, err: true });
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async (e) => {
    e.preventDefault();
    const val = search.value.trim();
    if (!val) return;

    setScanLoading(true);
    setScanErr('');
    setScanRes(null);

    try {
      const q = new URLSearchParams({ contact_type: search.type, contact_value: val }).toString();
      const data = await api(`/reports/reputation?${q}`, 'GET', null, token);
      setScanRes(data);
    } catch (err) {
      setScanErr(err.message);
    } finally {
      setScanLoading(false);
    }
  };

  return (
    <div className='min-h-screen bg-[#070913] text-slate-100 flex flex-col font-sans'>
      <header className='border-b border-slate-800 bg-[#0c1022]/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between'>
        <div className='flex items-center space-x-3'>
          <div className='w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-600/30'>
            <ShieldAlert className='w-4 h-4 text-white' />
          </div>
          <div>
            <div className='flex items-center space-x-2'>
              <span className='font-semibold text-sm text-white'>Riskly</span>
              <span className='text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-1.5 py-0.5 rounded font-mono'>v0.1.0</span>
            </div>
            <p className='text-[10px] text-slate-400'>Personal Fraud Risk Intelligence Platform</p>
          </div>
        </div>

        <div className='flex items-center space-x-4'>
          <div className='flex items-center space-x-2 text-xs'>
            <span className="w-2 h-2 rounded-full" />
            <span className='text-slate-300 font-mono text-[11px]'>{wsStatus}</span>
          </div>

          {token ? (
            <div className='flex items-center space-x-2'>
              <span className='text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded'>? Authenticated</span>
              <button onClick={handleLogout} className='text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded transition'>Logout</button>
            </div>
          ) : (
            <span className='text-[11px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded'>Unauthenticated</span>
          )}
        </div>
      </header>

      <main className='flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6'>
        <section className='lg:col-span-7 flex flex-col space-y-6'>
          <div className='bg-[#0e1222]/80 border border-slate-800 rounded-2xl p-5 shadow-xl'>
            <div className='flex items-center justify-between mb-3'>
              <h2 className='text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2'>
                <Search className='w-3.5 h-3.5 text-indigo-400' />
                <span>Verify Identity Reputation</span>
              </h2>
              <span className='text-[10px] text-emerald-400 font-mono bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded'>((•)) Live Pipeline</span>
            </div>

            <form onSubmit={handleScan} className='flex space-x-2'>
              <select
                value={search.type}
                onChange={(e) => setSearch(s => ({ ...s, type: e.target.value }))}
                className='bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-200 focus:outline-none'
              >
                {['phone', 'email', 'upi', 'bank_account', 'url'].map(t => (
                  <option key={t} value={t}>{t.toUpperCase()}</option>
                ))}
              </select>
              <input
                type='text'
                value={search.value}
                onChange={(e) => setSearch(s => ({ ...s, value: e.target.value }))}
                placeholder='+919876543210 or user@example.com'
                className='flex-1 bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none'
              />
              <button
                type='submit'
                disabled={scanLoading}
                className='bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium px-4 py-2 rounded-xl transition shadow-md shadow-indigo-600/20 cursor-pointer'
              >
                {scanLoading ? <RefreshCw className='w-3.5 h-3.5 animate-spin' /> : 'Scan'}
              </button>
            </form>

            {scanErr && <p className='text-xs text-rose-400 mt-2'>{scanErr}</p>}

            {scanRes && (
              <div className='mt-4 pt-4 border-t border-slate-800 grid grid-cols-3 gap-4'>
                <div className='bg-[#13192f] p-3 rounded-xl border border-slate-800'>
                  <span className='text-[10px] text-slate-400 block mb-1'>Reputation Score</span>
                  <div className='flex items-baseline space-x-1'>
                    <span className='text-2xl font-bold font-mono'>{scanRes.score}</span>
                    <span className='text-xs text-slate-500'>/ 100</span>
                  </div>
                </div>
                <div className='bg-[#13192f] p-3 rounded-xl border border-slate-800'>
                  <span className='text-[10px] text-slate-400 block mb-1'>Risk Level</span>
                  <span className='text-xs font-bold uppercase font-mono px-2 py-0.5 rounded inline-block mt-1 bg-indigo-500/20 text-indigo-300'>
                    {scanRes.risk_level || 'LOW'}
                  </span>
                </div>
                <div className='bg-[#13192f] p-3 rounded-xl border border-slate-800'>
                  <span className='text-[10px] text-slate-400 block mb-1'>Total Reports</span>
                  <span className='text-2xl font-bold text-indigo-400 font-mono'>{scanRes.report_count ?? 0}</span>
                </div>
              </div>
            )}
          </div>

          <div className='bg-[#0e1222]/80 border border-slate-800 rounded-2xl p-5 shadow-xl flex-1 flex flex-col min-h-[380px]'>
            <div className='flex items-center justify-between mb-4'>
              <h2 className='text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2'>
                <Activity className='w-3.5 h-3.5 text-indigo-400' />
                <span>Live Activity Feed</span>
              </h2>
              <span className='text-[10px] text-slate-500 font-mono'>Real-time Broadcast</span>
            </div>

            <div className='flex-1 overflow-y-auto space-y-3 pr-1 max-h-[500px]'>
              {reports.length === 0 ? (
                <div className='h-44 flex items-center justify-center text-slate-500 text-xs'>
                  Listening for incoming fraud signals across network...
                </div>
              ) : (
                reports.map((item, idx) => (
                  <div key={idx} className='bg-[#13192f] border border-slate-800 rounded-xl p-3.5'>
                    <div className='flex items-center justify-between mb-1.5'>
                      <div className='flex items-center space-x-2'>
                        <span className='text-xs font-mono font-medium text-slate-200'>{item.contact_value}</span>
                        <span className='text-[10px] font-mono uppercase bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded'>{item.contact_type}</span>
                      </div>
                      <span className='text-[10px] font-bold font-mono px-2 py-0.5 rounded uppercase bg-rose-500/10 text-rose-400 border border-rose-500/20'>
                        {item.report_type}
                      </span>
                    </div>
                    {item.description && <p className='text-xs text-slate-400 line-clamp-2'>{item.description}</p>}
                    <div className='mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono'>
                      <span>Score: <strong className='text-slate-300'>{item.ml_risk_score ?? 'N/A'}</strong></span>
                      <span>Urgency: <strong className='text-slate-300'>{item.urgency_level ?? 'Normal'}</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        <section className='lg:col-span-5 flex flex-col space-y-6'>
          <div className='bg-[#0e1222]/80 border border-slate-800 rounded-2xl p-5 shadow-xl'>
            <h2 className='text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-2 mb-1'>
              <AlertTriangle className='w-3.5 h-3.5' />
              <span>Submit Fraud Report</span>
            </h2>
            <p className='text-[11px] text-slate-400 mb-4'>Dispatches incident event directly to pipeline and live subscribers.</p>

            <form onSubmit={handleReport} className='space-y-3.5'>
              <div className='grid grid-cols-2 gap-3'>
                <div>
                  <label className='text-[11px] text-slate-400 block mb-1'>Entity Type</label>
                  <select
                    value={rep.contact_type}
                    onChange={(e) => setRep(r => ({ ...r, contact_type: e.target.value }))}
                    className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-200 focus:outline-none'
                  >
                    {['phone', 'email', 'upi', 'bank_account', 'url'].map(t => (
                      <option key={t} value={t}>{t.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className='text-[11px] text-slate-400 block mb-1'>Report Category</label>
                  <select
                    value={rep.report_type}
                    onChange={(e) => setRep(r => ({ ...r, report_type: e.target.value }))}
                    className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-200 focus:outline-none'
                  >
                    <option value='fraud'>Fraud (+30)</option>
                    <option value='phishing'>Phishing (+25)</option>
                    <option value='spam'>Spam (+10)</option>
                    <option value='impersonation'>Impersonation (+35)</option>
                    <option value='harassment'>Harassment (+20)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className='text-[11px] text-slate-400 block mb-1'>Entity Value</label>
                <input
                  type='text'
                  value={rep.contact_value}
                  onChange={(e) => setRep(r => ({ ...r, contact_value: e.target.value }))}
                  placeholder='+919876543210'
                  className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-100 focus:outline-none'
                />
              </div>

              <div>
                <label className='text-[11px] text-slate-400 block mb-1'>Incident Description</label>
                <textarea
                  value={rep.description}
                  onChange={(e) => setRep(r => ({ ...r, description: e.target.value }))}
                  rows={3}
                  className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-100 focus:outline-none resize-none'
                />
              </div>

              <div>
                <label className='text-[11px] text-slate-400 block mb-1'>Evidence / Notes (Optional)</label>
                <input
                  type='text'
                  value={rep.evidence}
                  onChange={(e) => setRep(r => ({ ...r, evidence: e.target.value }))}
                  placeholder='e.g. Malicious URL, OTP message body'
                  className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-100 focus:outline-none'
                />
              </div>

              <button
                type='submit'
                disabled={loading}
                className='w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs py-2.5 rounded-xl transition shadow-md shadow-indigo-600/20 flex items-center justify-center space-x-2 cursor-pointer'
              >
                {loading ? <RefreshCw className='w-3.5 h-3.5 animate-spin' /> : <><Send className='w-3.5 h-3.5' /><span>Dispatch Report Event</span></>}
              </button>

              {submitStatus.msg && (
                <p className="text-center text-xs pt-1">
                  {submitStatus.msg}
                </p>
              )}
            </form>
          </div>

          <div className='bg-[#0e1222]/80 border border-slate-800 rounded-2xl p-5 shadow-xl'>
            <h2 className='text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2 mb-3'>
              <KeyRound className='w-3.5 h-3.5 text-indigo-400' />
              <span>Analyst Authentication</span>
            </h2>

            {token ? (
              <div className='space-y-3'>
                <div className='bg-[#171f38] border border-emerald-900/40 rounded-xl p-3 flex items-center justify-between'>
                  <div>
                    <span className='text-[11px] text-slate-400 block'>Logged in as</span>
                    <span className='text-xs font-mono font-semibold text-emerald-400'>{auth.email}</span>
                  </div>
                  <span className='text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20'>Active</span>
                </div>
                <button
                  type='button'
                  onClick={handleLogout}
                  className='w-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs py-2 rounded-xl transition cursor-pointer'
                >
                  Clear Session / Logout
                </button>
              </div>
            ) : (
              <form onSubmit={handleLogin} className='space-y-3'>
                <input
                  type='email'
                  value={auth.email}
                  onChange={(e) => setAuth(a => ({ ...a, email: e.target.value }))}
                  placeholder='analyst@riskly.dev'
                  className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-100 focus:outline-none'
                />
                <input
                  type='password'
                  value={auth.password}
                  onChange={(e) => setAuth(a => ({ ...a, password: e.target.value }))}
                  placeholder='Password'
                  className='w-full bg-[#171f38] border border-slate-700 text-xs rounded-xl px-3 py-2 text-slate-100 focus:outline-none'
                />
                {authErr && <p className='text-xs text-rose-400'>{authErr}</p>}
                <button
                  type='submit'
                  className='w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs py-2.5 rounded-xl transition shadow-md shadow-indigo-600/20 font-medium cursor-pointer'
                >
                  Authenticate Session
                </button>
              </form>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
