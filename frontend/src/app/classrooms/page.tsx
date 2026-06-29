"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { School, Bookmark, Calendar, Monitor, BookOpen } from "lucide-react";
import { api, getSession, UserSession } from "../../lib/api";


export default function ClassroomsPage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [rooms, setRooms] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Booking Form States
  const [roomNumber, setRoomNumber] = useState("");
  const [bookingDate, setBookingDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [purpose, setPurpose] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const fetchData = () => {
    api.getClassrooms()
      .then((data) => {
        setRooms(data.classrooms || []);
        setBookings(data.bookings || []);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    fetchData();
  }, [router]);

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg("");
    setErrorMsg("");
    try {
      await api.bookClassroom(roomNumber, bookingDate, startTime, endTime, purpose);
      setSuccessMsg("Classroom booked successfully!");
      setRoomNumber("");
      setBookingDate("");
      setStartTime("");
      setEndTime("");
      setPurpose("");
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to book classroom.");
    }
  };

  if (loading || !session) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="w-6 h-6 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl w-full mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Classrooms &amp; Bookings</h1>
        <p className="text-slate-500 mt-1">Track room capacities, projector utilities, and reservations.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Classrooms List Card */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md h-fit">
          <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
            <School className="w-5 h-5 text-indigo-600" />
            <span>Classroom Capacity</span>
          </h3>

          <div className="space-y-4">
            {rooms.map((room) => (
              <div key={room.room_number} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/40 flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-slate-850 text-sm">{room.room_number}</h4>
                  <p className="text-xs text-slate-400 font-medium mt-0.5">{room.building}</p>
                  <p className="text-xs text-slate-500 mt-1">Seats: <span className="text-slate-850 font-bold">{room.capacity}</span></p>
                </div>
                {room.has_projector && (
                  <span className="p-2 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600" title="Projector Enabled">
                    <Monitor className="w-4 h-4" />
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bookings & Form Section */}
        <div className="lg:col-span-2 space-y-8">
          {/* Reservation Request form for Faculty */}
          {session.role === "faculty" && (
            <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md">
              <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                <Bookmark className="w-5 h-5 text-indigo-600" />
                <span>Reserve classroom</span>
              </h3>

              {successMsg && <p className="mb-4 text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-100 p-3 rounded-2xl">{successMsg}</p>}
              {errorMsg && <p className="mb-4 text-xs font-bold text-red-600 bg-red-50 border border-red-100 p-3 rounded-2xl">{errorMsg}</p>}

              <form onSubmit={handleBook} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Room Number</label>
                  <select
                    required
                    value={roomNumber}
                    onChange={(e) => setRoomNumber(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Select Room</option>
                    {rooms.map((r) => (
                      <option key={r.room_number} value={r.room_number}>{r.room_number}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Date</label>
                  <input
                    type="date"
                    required
                    value={bookingDate}
                    onChange={(e) => setBookingDate(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Start Time (HH:MM)</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 09:00"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">End Time (HH:MM)</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 11:00"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Purpose</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Guest Lecture, Lab Revision"
                    value={purpose}
                    onChange={(e) => setPurpose(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none"
                  />
                </div>

                <button
                  type="submit"
                  className="md:col-span-2 w-full mt-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-semibold text-sm transition-colors duration-200 shadow-md shadow-indigo-100"
                >
                  Confirm Reservation
                </button>
              </form>
            </div>
          )}

          {/* Bookings lists */}
          <div className="bg-white rounded-3xl border border-slate-200/80 shadow-md overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <h3 className="font-bold text-slate-800 text-base">Current Bookings Schedule</h3>
            </div>
            
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-400 uppercase tracking-wider">
                  <th className="px-6 py-4">Room</th>
                  <th className="px-6 py-4">Date / Slot</th>
                  <th className="px-6 py-4">Reserved By</th>
                  <th className="px-6 py-4">Purpose</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm font-medium text-slate-700">
                {bookings.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                      No classroom reservations booked.
                    </td>
                  </tr>
                ) : (
                  bookings.map((b) => (
                    <tr key={b.booking_id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 font-bold text-slate-850">{b.room_number}</td>
                      <td className="px-6 py-4">
                        <p className="font-bold text-slate-800">{b.date}</p>
                        <p className="text-[10px] text-slate-400 mt-0.5">{b.start_time} - {b.end_time}</p>
                      </td>
                      <td className="px-6 py-4">
                        <p className="font-bold text-slate-800">{b.faculty_name}</p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">ID: {b.booked_by}</p>
                      </td>
                      <td className="px-6 py-4 max-w-xs truncate">{b.purpose}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
