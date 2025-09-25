import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import Footer from "./components/Footer.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Topics from "./pages/Topics.jsx";
import Assignments from "./pages/Assignments.jsx";  // 👈 новая страница
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import AssignmentDetail from "./pages/AssignmentDetail.jsx";
import AdminLogs from './pages/AdminLogs';
import AdminUsers from './pages/AdminUsers';
import AdminTopics from './pages/AdminTopics';
import AdminAssignments from './pages/AdminAssignments';
import AdminRoute from './components/AdminRoute';


export default function App() {
  return (
    <div>
      <NavBar />

      <main className="container" style={{ marginTop: "32px" }}>
        <Routes>
          <Route path="/" element={<Navigate to="/topics" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/topics"
            element={
              <ProtectedRoute>
                <Topics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/topics/:id"
            element={
              <ProtectedRoute>
                <Assignments />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assignments/:id"
            element={
              <ProtectedRoute>
                <AssignmentDetail />
              </ProtectedRoute>
            }
          />

          <Route path="/admin/logs" element={<AdminRoute><AdminLogs/></AdminRoute>} />
          <Route path="/admin/users" element={<AdminRoute><AdminUsers/></AdminRoute>} />
          <Route path="/admin/topics" element={<AdminRoute><AdminTopics/></AdminRoute>} />
          <Route path="/admin/assignments" element={<AdminRoute><AdminAssignments/></AdminRoute>} />

          <Route path="*" element={<div>Страница не найдена</div>} />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}
