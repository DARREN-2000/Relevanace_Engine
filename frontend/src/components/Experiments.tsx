import { useEffect, useState } from "react";
import axios from "axios";

export const Experiments = () => {
  const [experiments, setExperiments] = useState<any[]>([]);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/experiments")
      .then((res) => setExperiments(res.data))
      .catch((err) => {
        console.error("API failed, using mock data", err);
        setExperiments([
          {
            id: "1",
            name: "Subject Line A/B Test",
            description: "Testing emojis in subject lines",
            status: "running",
            traffic_split: { A: 50, B: 50 },
          },
          {
            id: "2",
            name: "Send Time Optimization",
            description: "Morning vs Afternoon sends",
            status: "completed",
            traffic_split: { A: 50, B: 50 },
          },
          {
            id: "3",
            name: "Channel Preference Test",
            description: "Email vs SMS vs Push",
            status: "draft",
            traffic_split: { A: 33, B: 33, C: 34 },
          },
        ]);
      });
  }, []);

  return (
    <div className="page-container">
      <h1>Experiments</h1>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Status</th>
            <th>Traffic Split</th>
          </tr>
        </thead>
        <tbody>
          {experiments.map((e) => (
            <tr key={e.id}>
              <td>{e.name}</td>
              <td>{e.description}</td>
              <td>{e.status}</td>
              <td>{JSON.stringify(e.traffic_split)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
