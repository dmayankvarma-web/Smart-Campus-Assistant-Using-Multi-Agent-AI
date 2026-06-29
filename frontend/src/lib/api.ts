const API_BASE_URL = "http://localhost:8000/api";

export interface UserSession {
  token: string;
  role: 'student' | 'faculty';
  name: string;
  userId: string;
}

export function getSession(): UserSession | null {
  if (typeof window === "undefined") return null;
  const session = localStorage.getItem("college_session");
  if (!session) return null;
  try {
    return JSON.parse(session);
  } catch {
    return null;
  }
}

export function setSession(session: UserSession) {
  if (typeof window !== "undefined") {
    localStorage.setItem("college_session", JSON.stringify(session));
  }
}

export function clearSession() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("college_session");
  }
}

async function request(path: string, options: RequestInit = {}) {
  const session = getSession();
  const headers = new Headers(options.headers || {});
  
  if (session?.token) {
    headers.set("Authorization", `Bearer ${session.token}`);
  }
  
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    clearSession();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }
  
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "Request failed");
  }
  
  return response.json();
}

export const api = {
  login: async (userId: string, password: string): Promise<any> => {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Invalid credentials");
    }
    const data = await res.json();
    const session: UserSession = {
      token: data.access_token,
      role: data.role,
      name: data.name,
      userId: data.user_id
    };
    setSession(session);
    return session;
  },
  
  getStats: () => request("/dashboard/stats"),
  
  sendMessage: (message: string, sessionId: string) => 
    request("/chat/message", {
      method: "POST",
      body: JSON.stringify({ message, session_id: sessionId })
    }),
    
  getChatHistory: () => request("/chat/history"),
  
  getAttendance: () => request("/data/attendance"),
  
  getCourses: () => request("/data/courses"),
  
  getLeaves: () => request("/data/leaves"),
  
  createLeave: (start_date: string, end_date: string, reason: string) =>
    request("/data/leaves", {
      method: "POST",
      body: JSON.stringify({ start_date, end_date, reason })
    }),
    
  reviewLeave: (leaveId: number, status: 'approved' | 'rejected', comments?: string) =>
    request("/data/leaves/review", {
      method: "POST",
      body: JSON.stringify({ leave_id: leaveId, status, comments })
    }),
    
  getFaculty: () => request("/data/faculty"),
  
  getClassrooms: () => request("/data/classrooms"),
  
  bookClassroom: (roomNumber: string, date: string, startTime: string, endTime: string, purpose: string) =>
    request("/data/classrooms/book", {
      method: "POST",
      body: JSON.stringify({
        room_number: roomNumber,
        date,
        start_time: startTime,
        end_time: endTime,
        purpose
      })
    })
};
