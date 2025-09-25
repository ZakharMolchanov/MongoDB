import React, { useEffect, useState } from 'react';
import { assignmentsApi } from '../adminApis';

export default function AdminAssignments(){
  const [items, setItems] = useState([]);
  const [q, setQ] = useState('');
  const [topicFilter, setTopicFilter] = useState('');
  const [editing, setEditing] = useState(null);

  const load = ()=> assignmentsApi.list({ q: q || undefined, topic_id: topicFilter || undefined }).then(r=>{
    const data = r.data;
    if (Array.isArray(data)) setItems(data);
    else if (Array.isArray(data.data)) setItems(data.data);
    else setItems([]);
  }).catch(()=>{setItems([])});
  useEffect(()=>{ load(); },[]);

  const save = async (a)=>{
    try{
      if(a.assignment_id){
        await assignmentsApi.update(a.assignment_id, a);
      } else {
        await assignmentsApi.create(a);
      }
      await load();
    }catch(e){
      alert('Save failed: '+(e?.response?.data?.error || e?.message || ''))
    }
    setEditing(null);
  }

  const del = (id)=>{ if(!confirm('Delete assignment?'))return; assignmentsApi.delete(id).then(()=>load()).catch(()=>{}); }

  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h2 style={{margin:0}}>Assignments</h2>
        <div style={{display:'flex', gap:8}}>
          <input placeholder='Поиск' value={q} onChange={e=>setQ(e.target.value)} />
          <input placeholder='topic_id' value={topicFilter} onChange={e=>setTopicFilter(e.target.value)} style={{width:120}} />
          <button className='btn' onClick={()=>{ load();}}>Search</button>
        </div>
        <button className='btn primary' onClick={()=>setEditing({})}>Create</button>
      </div>
        <table className="table" style={{width:'100%'}}>
          <thead><tr><th>ID</th><th>Title</th><th>Topic</th><th>Required</th><th/></tr></thead>
          <tbody>
            {items.map(a=> (
              <tr key={a.assignment_id}><td>{a.assignment_id}</td><td>{a.title}</td><td>{a.topic_id}</td><td>{a.schema?.required_method || ''}</td><td>
                <button className='btn' onClick={()=>setEditing(a)}>Edit</button>
                <button className='btn ghost' onClick={()=>del(a.assignment_id)} style={{marginLeft:8}}>Delete</button>
              </td></tr>
            ))}
          </tbody>
        </table>

      {editing && <AssignmentForm assignment={editing} onCancel={()=>setEditing(null)} onSave={save} />}
    </div>
  )
}

function AssignmentForm({assignment, onCancel, onSave}){
  const [title, setTitle] = useState(assignment.title||'');
  const [description, setDescription] = useState(assignment.description||'');
  const [topic_id, setTopicId] = useState(assignment.topic_id||'');
  const [required_method, setRequiredMethod] = useState((assignment.schema && assignment.schema.required_method) || '');

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" onClick={(e)=>e.stopPropagation()}>
        <h3 style={{marginTop:0}}>{assignment.assignment_id ? 'Edit Assignment' : 'Create Assignment'}</h3>
        <div style={{display:'grid', gap:10}}>
          <label className="small">Title</label>
          <input value={title} onChange={e=>setTitle(e.target.value)} />

          <label className="small">Description</label>
          <textarea value={description} onChange={e=>setDescription(e.target.value)} />

          <label className="small">Topic ID</label>
          <input value={topic_id} onChange={e=>setTopicId(e.target.value)} />

          <label className="small">Required method (optional, e.g. find)</label>
          <input value={required_method} onChange={e=>setRequiredMethod(e.target.value)} placeholder="find" />

          <div style={{textAlign:'right', marginTop:8}}>
            <button className='btn primary' onClick={()=>onSave({...assignment, title, description, topic_id, schema: { required_method: required_method || undefined } })}>Save</button>
            <button className='btn ghost' onClick={onCancel} style={{marginLeft:8}}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}
