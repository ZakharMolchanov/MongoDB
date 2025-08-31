import React from "react";

export default function Footer(){
  return (
    <footer className="footer">
      <div className="container" style={{display:'flex',justifyContent:'space-between',gap:12,flexWrap:'wrap'}}>
        <div>© {new Date().getFullYear()} Mongo Trainer</div>
        <div>Учимся MongoDB: запросы, пайплайны, индексы.</div>
      </div>
    </footer>
  );
}
