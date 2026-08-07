import { useState } from "react";
import axios from "axios";

export const Consents = () => {
  const [userId, setUserId] = useState("");
  const [consents, setConsents] = useState<any[]>([]);

  // New consent form state
  const [channel, setChannel] = useState("email");
  const [status, setStatus] = useState("granted");
  const [source, setSource] = useState("web_form");

  const handleFetchConsents = () => {
    if (!userId) return;
    axios
      .get(`http://localhost:8000/api/consents/${userId}`)
      .then((res) => setConsents(res.data))
      .catch((err) => {
        console.error("API failed, using mock data", err);
        setConsents([
          {
            id: "1",
            channel: "email",
            status: "granted",
            source: "signup",
            created_at: new Date().toISOString(),
          },
          {
            id: "2",
            channel: "sms",
            status: "withdrawn",
            source: "preference_center",
            created_at: new Date().toISOString(),
          },
        ]);
      });
  };

  const handleRecordConsent = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) {
      alert("Please enter a User ID first.");
      return;
    }

    const payload = {
      user_id: userId,
      channel,
      status,
      source,
    };

    axios
      .post("http://localhost:8000/api/consents", payload)
      .then(() => {
        alert("Consent recorded successfully!");
        handleFetchConsents();
      })
      .catch((err) => {
        console.error("API failed, mocking success", err);
        alert("Consent recorded successfully (Mock)!");
        setConsents((prev) => [
          {
            id: Math.random().toString(),
            channel,
            status,
            source,
            created_at: new Date().toISOString(),
          },
          ...prev,
        ]);
      });
  };

  return (
    <div className="page-container">
      <h1>Consents</h1>

      <div style={{ marginBottom: "20px" }}>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter User ID"
          style={{ padding: "5px", marginRight: "10px" }}
        />
        <button onClick={handleFetchConsents}>Fetch Consents</button>
      </div>

      <div
        style={{
          border: "1px solid #ccc",
          padding: "15px",
          marginBottom: "20px",
        }}
      >
        <h3>Record New Consent</h3>
        <form onSubmit={handleRecordConsent}>
          <label style={{ marginRight: "10px" }}>
            Channel:
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              style={{ marginLeft: "5px" }}
            >
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="push">Push</option>
            </select>
          </label>
          <label style={{ marginRight: "10px" }}>
            Status:
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              style={{ marginLeft: "5px" }}
            >
              <option value="granted">Granted</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          </label>
          <label style={{ marginRight: "10px" }}>
            Source:
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              style={{ marginLeft: "5px", width: "100px" }}
            />
          </label>
          <button type="submit">Record</button>
        </form>
      </div>

      <h2>Consent Records</h2>
      <table>
        <thead>
          <tr>
            <th>Channel</th>
            <th>Status</th>
            <th>Source</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {consents.map((c) => (
            <tr key={c.id}>
              <td>{c.channel}</td>
              <td>{c.status}</td>
              <td>{c.source}</td>
              <td>{new Date(c.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
