import React from 'react';

export default function AdminLogDetail({log, onClose}){
  if(!log) return null;
  return (
    <div style={{position:'fixed', left:0, right:0, top:0, bottom:0, background:'rgba(0,0,0,.4)', display:'flex', alignItems:'center', justifyContent:'center'}} onClick={onClose}>
      <div style={{width:800, background:'#fff', padding:20, borderRadius:8}} onClick={e=>e.stopPropagation()}>
        <h3>Log #{log.id}</h3>
        <p><b>Path:</b> {log.path}</p>
        <p><b>Method:</b> {log.method}</p>
        <p><b>Status:</b> {log.status_code}</p>
        <p><b>User:</b> {log.user_id}</p>
        <p><b>When:</b> {log.created_at}</p>
        <p><b>Payload:</b></p>
        <pre style={{maxHeight:300, overflow:'auto', background:'#f7f7f7', padding:10}}>{log.payload}</pre>
        <div style={{textAlign:'right'}}><button className='btn' onClick={onClose}>Close</button></div>
      </div>
    </div>
  )
}
