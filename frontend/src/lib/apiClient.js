const BASE = import.meta.env.VITE_API_V1_BASE_URL || "http://localhost:8001/api/v1";
export async function apiFetch(path, { method="GET", body, token, idempotencyKey }={}) {
  const headers={"Content-Type":"application/json"};
  if(token) headers["Authorization"]=`Bearer ${token}`;
  if(idempotencyKey) headers["Idempotency-Key"]=idempotencyKey;
  const res=await fetch(`${BASE}${path}`,{method, headers, body: body ? JSON.stringify(body): undefined});
  const json=await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(json.message || `API ${res.status}`);
  return json;
}
