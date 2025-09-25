import axios from "axios";

const base = axios.create({
  baseURL: import.meta.env.VITE_AI_URL || "/ai",
});

export const aiApi = {
  // Simple chat endpoint: messages is an array of { role, content }
  chat: (messages, opts = {}) =>
    base.post("/chat", {
      messages,
      ...opts,
    }),

  hint: ({ assignment_title, assignment_description, schema, user_query }) =>
    base.post("/task", {
      kind: "hint",
      context: { assignment_title, assignment_description, schema, user_query },
    }),

  explain: ({ assignment_title, assignment_description, schema, user_query }) =>
    base.post("/task", {
      kind: "explain",
      context: { assignment_title, assignment_description, schema, user_query },
    }),

  fixError: ({
    assignment_title,
    assignment_description,
    schema,
    user_query,
    error_text,
  }) =>
    base.post("/task", {
      kind: "fix_error",
      context: {
        assignment_title,
        assignment_description,
        schema,
        user_query,
        error_text,
      },
    }),
};
