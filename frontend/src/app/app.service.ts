import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export interface CurrentUser {
  id: number;
  name: string;
  email: string;
}

export interface Appointment {
  patient: string;
  cpf: string;
  doctor: string;
  specialty: string;
  date: string;
  time: string;
  insurance: string;
  status: string;
}

interface AuthResponse {
  ok: boolean;
  message?: string;
  user: CurrentUser;
}

interface MeResponse {
  ok: boolean;
  authenticated: boolean;
  user: CurrentUser;
}

interface AppointmentsResponse {
  ok: boolean;
  message: string;
  records: Appointment[];
}

@Injectable({ providedIn: 'root' })
export class AppointmentsApiService {
  private readonly http = inject(HttpClient);

  login(credentials: { identifier: string; password: string }): Promise<AuthResponse> {
    return firstValueFrom(this.http.post<AuthResponse>('/api/login', credentials, { withCredentials: true }));
  }

  logout(): Promise<void> {
    return firstValueFrom(this.http.post<void>('/api/logout', {}, { withCredentials: true }));
  }

  me(): Promise<MeResponse> {
    return firstValueFrom(this.http.get<MeResponse>('/api/me', { withCredentials: true }));
  }

  getAppointments(search = ''): Promise<AppointmentsResponse> {
    const params: Record<string, string> | undefined = search.trim() ? { search: search.trim() } : undefined;
    return firstValueFrom(this.http.get<AppointmentsResponse>('/api/appointments', { withCredentials: true, params }));
  }
}