import React, { useEffect, useState } from 'react';
import { adminApi } from '../adminApi';

function EditModal({user, onClose, onSave, onDelete}){
  const [isAdmin, setIsAdmin] = useState(Boolean(user?.is_admin));
  const [email, setEmail] = useState(user?.email || "");
  const [first, setFirst] = useState(user?.first_name || "");
  const [last, setLast] = useState(user?.last_name || "");
  if(!user) return null;
  return (
    <div style={{position:'fixed', left:0, right:0, top:0, bottom:0, background:'rgba(0,0,0,.4)', display:'flex', alignItems:'center', justifyContent:'center'}} onClick={onClose}>
      <div style={{width:480, background:'#fff', padding:20, borderRadius:8}} onClick={e=>e.stopPropagation()}>
        <h3>Edit {user.email}</h3>
        <div style={{display:'grid', gap:8}}>
          <label> Email <input value={email} onChange={e=>setEmail(e.target.value)} /></label>
          <label> First name <input value={first} onChange={e=>setFirst(e.target.value)} /></label>
          <label> Last name <input value={last} onChange={e=>setLast(e.target.value)} /></label>
          <label><input type='checkbox' checked={isAdmin} onChange={e=>setIsAdmin(e.target.checked)} /> is admin</label>
        </div>
        <div style={{display:'flex', justifyContent:'space-between', marginTop:12}}>
          <div>
            <button className='btn ghost' onClick={()=>{ if(confirm('Delete user?')) onDelete(user.id); }} style={{color:'red'}}>Delete</button>
          </div>
          <div>
            <button className='btn' onClick={()=>onSave({...user, is_admin:isAdmin, email, first_name:first, last_name:last})}>Save</button>
            <button className='btn ghost' onClick={onClose} style={{marginLeft:8}}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AdminUsers(){
  const [users, setUsers] = useState([]);
  const [editing, setEditing] = useState(null);

  const load = ()=> adminApi.listUsers().then(r=>{
    const data = r.data;
    if (Array.isArray(data)) setUsers(data);
    else if (Array.isArray(data.data)) setUsers(data.data);
    else setUsers([]);
  }).catch(()=>{setUsers([])});
  useEffect(()=>{ load(); },[]);

  const handleSave = (u)=>{
    adminApi.updateUser(u.id, { is_admin: u.is_admin, email: u.email, first_name: u.first_name, last_name: u.last_name }).then(()=>{ load(); setEditing(null); }).catch(()=>{});
  }

  const handleDelete = (id)=>{
    if(!confirm('Delete user?')) return;
    adminApi.deleteUser(id).then(()=>load()).catch(()=>{});
  }

  return (
    <div className="card" style={{padding:18}}>
      <h2 style={{marginTop:0}}>Users</h2>
  <table className="table" style={{width:'100%', borderCollapse:'collapse'}}>
        <thead><tr><th>ID</th><th>Email</th><th>Name</th><th>Admin</th><th/></tr></thead>
        <tbody>
          {users.map(u=> (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.email}</td>
              <td>{u.first_name} {u.last_name}</td>
              <td>{String(u.is_admin)}</td>
              <td>
                <button className='btn' onClick={()=>setEditing(u)}>Edit</button>
                <button className='btn ghost' onClick={()=>handleDelete(u.id)} style={{marginLeft:8}}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

  {editing && <EditModal user={editing} onClose={()=>setEditing(null)} onSave={handleSave} onDelete={(id)=>{ handleDelete(id); setEditing(null); }} />}
    </div>
  )
}
