import React, { useEffect, useState } from 'react';
import { topicsApi } from '../adminApis';

export default function AdminTopics(){
  const [topics, setTopics] = useState([]);
  const [editing, setEditing] = useState(null);

  const load = ()=> topicsApi.getAll().then(r=>setTopics(r.data)).catch(()=>{});
  useEffect(()=>{ load(); },[]);

  const save = (t)=>{
    if(t.topic_id) topicsApi.getOne(t.topic_id).then(()=>{}); // noop
    if(t.topic_id){
      topicsApi.update(t.topic_id, t).then(()=>load());
    } else {
      topicsApi.create(t).then(()=>load());
    }
    setEditing(null);
  }

  const del = (id)=>{ if(!confirm('Delete topic?'))return; topicsApi.delete(id).then(()=>load()); }

  return (
    <div>
      <h2>Topics</h2>
      <button className='btn' onClick={()=>setEditing({})}>Create</button>
      <table style={{width:'100%'}}>
        <thead><tr><th>ID</th><th>Title</th><th>Difficulty</th><th/></tr></thead>
        <tbody>
          {topics.map(t=> (
            <tr key={t.topic_id}><td>{t.topic_id}</td><td>{t.title}</td><td>{t.difficulty}</td><td>
              <button className='btn' onClick={()=>setEditing(t)}>Edit</button>
              <button className='btn ghost' onClick={()=>del(t.topic_id)} style={{marginLeft:8}}>Delete</button>
            </td></tr>
          ))}
        </tbody>
      </table>

      {editing && <TopicForm topic={editing} onCancel={()=>setEditing(null)} onSave={save} />}
    </div>
  )
}

function TopicForm({topic, onCancel, onSave}){
  const [title, setTitle] = useState(topic.title||'');
  const [description, setDescription] = useState(topic.description||'');
  const [difficulty, setDifficulty] = useState(topic.difficulty||'');
  return (
    <div style={{marginTop:12}}>
      <h3>{topic.topic_id ? 'Edit' : 'Create'}</h3>
      <div><label>Title</label><input value={title} onChange={e=>setTitle(e.target.value)} /></div>
      <div><label>Description</label><textarea value={description} onChange={e=>setDescription(e.target.value)} /></div>
      <div><label>Difficulty</label><input value={difficulty} onChange={e=>setDifficulty(e.target.value)} /></div>
      <div style={{marginTop:8}}>
        <button className='btn' onClick={()=>onSave({...topic, title, description, difficulty})}>Save</button>
        <button className='btn ghost' onClick={onCancel} style={{marginLeft:8}}>Cancel</button>
      </div>
    </div>
  )
}
