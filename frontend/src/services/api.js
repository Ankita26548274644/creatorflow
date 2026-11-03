import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";
const API_KEY = "creatorflow_dev_key";

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    "X-API-Key": API_KEY,
  },
});

export async function checkHealth() {
  const res = await client.get("/health");
  return res.data;
}

export async function uploadAndValidate(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await client.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function validateOnly(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await client.post("/api/validate", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}