import React, { useEffect, useState } from 'react';
import { adminApi } from '../adminApi';
import AdminLogDetail from '../components/AdminLogDetail';

export default function AdminLogs(){
  const [logs, setLogs] = useState([]);
  const [query, setQuery] = useState('');
  const [userId, setUserId] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState(null);
  const [warning, setWarning] = useState(null);

  const load = ()=>{
    const params = { offset: page*50, limit:50 };
    if(query) params.path = query;
    if(userId) params.user_id = userId;
    if(status) params.status_code = status;
    adminApi.listLogs(params).then(r=>{
      const data = r.data;
      setWarning(null);
      if (data && data.warning) {
        setLogs([]);
        setWarning(data.warning);
        return;
      }
      // Some proxies return { data: [...] } or an array directly
      if (Array.isArray(data)) setLogs(data);
      else if (Array.isArray(data.data)) setLogs(data.data);
      else setLogs([]);
    }).catch(()=>{setLogs([])});
  }

  useEffect(()=>{ load(); }, [page]);

  return (
    <div className="card" style={{padding:18}}>
      <h2 style={{marginTop:0}}>Logs</h2>
      <div style={{display:'flex', gap:8, marginBottom:12}}>
        <input placeholder='path contains' value={query} onChange={e=>setQuery(e.target.value)} />
        <input placeholder='user id' value={userId} onChange={e=>setUserId(e.target.value)} style={{width:120}} />
        <input placeholder='status' value={status} onChange={e=>setStatus(e.target.value)} style={{width:120}} />
        <button className='btn' onClick={()=>{setPage(0); load();}}>Search</button>
      </div>

  <table className="table" style={{width:'100%', borderCollapse:'collapse'}}>
        <thead><tr><th>ID</th><th>Path</th><th>Method</th><th>Status</th><th>User</th><th>When</th><th/></tr></thead>
        <tbody>
          {logs.map(l=> (
            <tr key={l.id}>
              <td>{l.id}</td>
              <td style={{maxWidth:300, overflow:'hidden', textOverflow:'ellipsis'}}>{l.path}</td>
              <td>{l.method}</td>
              <td>{l.status_code}</td>
              <td>{l.user_id}</td>
              <td>{l.created_at}</td>
              <td><button className='btn ghost' onClick={()=>setSelected(l)}>Details</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{marginTop:12}}>
        <button className='btn' onClick={()=>{ if(page>0){ setPage(p=>p-1); load(); } }}>Prev</button>
        <button className='btn' onClick={()=>{ setPage(p=>p+1); load(); }}>Next</button>
      </div>

      {selected && <AdminLogDetail log={selected} onClose={()=>setSelected(null)} />}
      {warning && (
        <div style={{marginTop:12, padding:12, background:'#fff7cc', border:'1px solid #f0d88a', borderRadius:6}}>
          <b>Warning:</b> {warning} <button className='btn ghost' onClick={()=>setWarning(null)} style={{marginLeft:12}}>Dismiss</button>
        </div>
      )}
    </div>
  )
}
