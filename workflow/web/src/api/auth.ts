import client from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserInfo {
  id: string;
  name: string;
  role: string;
}

export interface LoginResponse {
  token: string;
  user: UserInfo;
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await client.post<LoginResponse>("/auth/login", data);
  return res.data;
}

export async function getMe(): Promise<UserInfo> {
  const res = await client.get<UserInfo>("/auth/me");
  return res.data;
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  await client.put("/auth/change-password", { oldPassword, newPassword });
}
