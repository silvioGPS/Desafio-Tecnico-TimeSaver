import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Tabulator } from 'tabulator-tables';

import { Appointment, AppointmentsApiService, CurrentUser } from './app.service';

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements AfterViewInit, OnDestroy {
  @ViewChild('tableHost') tableHost?: ElementRef<HTMLDivElement>;

  private readonly api = inject(AppointmentsApiService);

  protected readonly currentUser = signal<CurrentUser | null>(null);
  protected readonly loadingSession = signal(true);
  protected readonly loadingAppointments = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly appointmentsMessage = signal('Carregando agenda...');

  protected identifier = 'admin';
  protected password = 'Agenda@123';
  protected searchTerm = '';

  private table?: any;

  private readonly statusPalette: Record<string, { color: string; background: string; border: string }> = {
    confirmado: { color: '#062114', background: 'rgba(130, 227, 155, 0.95)', border: '#82e39b' },
    aguardando: { color: '#251903', background: 'rgba(255, 211, 107, 0.95)', border: '#ffd36b' },
    'em-andamento': { color: '#251903', background: 'rgba(255, 211, 107, 0.95)', border: '#ffd36b' },
    concluido: { color: '#061a2a', background: 'rgba(102, 184, 255, 0.95)', border: '#66b8ff' },
    cancelado: { color: '#2a060a', background: 'rgba(255, 110, 122, 0.95)', border: '#ff6e7a' },
  };

  constructor() {
    void this.restoreSession();
  }

  ngAfterViewInit(): void {
    // A tabela é criada somente depois da autenticação, quando o host existir no DOM.
  }

  ngOnDestroy(): void {
    this.table?.destroy();
  }

  protected get isAuthenticated(): boolean {
    return this.currentUser() !== null;
  }

  protected async submitLogin(): Promise<void> {
    this.errorMessage.set('');

    if (!this.identifier.trim() || !this.password) {
      this.errorMessage.set('Preencha usuário/e-mail e senha para continuar.');
      return;
    }

    try {
      const response = await this.api.login({ identifier: this.identifier.trim(), password: this.password });
      this.currentUser.set(response.user);
      this.searchTerm = '';
      await this.waitForViewUpdate();
      await this.loadAppointments('');
    } catch (error) {
      this.errorMessage.set(this.extractMessage(error, 'Não foi possível autenticar agora.'));
    }
  }

  protected async logout(): Promise<void> {
    try {
      await this.api.logout();
    } finally {
      this.currentUser.set(null);
      this.errorMessage.set('');
      this.appointmentsMessage.set('Carregando agenda...');
      this.searchTerm = '';
      this.table?.clearData();
      this.table?.destroy();
      this.table = undefined;
    }
  }

  protected async searchAppointments(): Promise<void> {
    await this.loadAppointments(this.searchTerm.trim());
  }

  protected clearSearch(): void {
    this.searchTerm = '';
    void this.loadAppointments('');
  }

  private async restoreSession(): Promise<void> {
    try {
      const response = await this.api.me();
      this.currentUser.set(response.user);
      await this.waitForViewUpdate();
      await this.loadAppointments('');
    } catch {
      this.currentUser.set(null);
    } finally {
      this.loadingSession.set(false);
    }
  }

  private async loadAppointments(search: string): Promise<void> {
    this.loadingAppointments.set(true);
    this.errorMessage.set('');

    try {
      const response = await this.api.getAppointments(search);
      this.appointmentsMessage.set(response.message);
      this.syncTable(response.records);
    } catch (error) {
      this.appointmentsMessage.set(this.extractMessage(error, 'Não foi possível carregar os agendamentos no momento.'));
      this.syncTable([]);
    } finally {
      this.loadingAppointments.set(false);
    }
  }

  private syncTable(records: Appointment[]): void {
    if (!this.tableHost?.nativeElement) {
      return;
    }

    if (!this.table) {
      this.table = new Tabulator(this.tableHost.nativeElement, {
        data: records,
        layout: 'fitColumns',
        placeholder: 'Nenhum agendamento disponível.',
        columns: [
          { title: 'Data', field: 'date', width: 110, hozAlign: 'center', headerHozAlign: 'center', formatter: this.formatDate },
          { title: 'Horário', field: 'time', width: 90, hozAlign: 'center', headerHozAlign: 'center' },
          { title: 'Paciente', field: 'patient', minWidth: 160, hozAlign: 'left', headerHozAlign: 'left' },
          { title: 'CPF', field: 'cpf', width: 140, hozAlign: 'center', headerHozAlign: 'center' },
          { title: 'Médico', field: 'doctor', minWidth: 170, hozAlign: 'left', headerHozAlign: 'left' },
          { title: 'Especialidade', field: 'specialty', minWidth: 140, hozAlign: 'left', headerHozAlign: 'left' },
          { title: 'Convênio', field: 'insurance', minWidth: 130, hozAlign: 'left', headerHozAlign: 'left' },
          { title: 'Status', field: 'status', width: 140, hozAlign: 'center', headerHozAlign: 'center', formatter: this.formatStatus },
        ],
      });
      return;
    }

    void this.table.setData(records);
  }

  private async waitForViewUpdate(): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, 0));
  }

  private formatDate = (cell: { getValue: () => string }) => {
    const value = cell.getValue();
    if (!value) {
      return '-';
    }

    const [year, month, day] = value.split('-');
    if (!year || !month || !day) {
      return value;
    }

    return `${day}/${month}/${year}`;
  };

  private formatStatus = (cell: { getValue: () => string }) => {
    const value = (cell.getValue() || '').toString();
    const slug = this.toStatusSlug(value);
    const palette = this.statusPalette[slug] || { color: '#1e293b', background: '#e2e8f0', border: '#cbd5e1' };

    return `<span class="status-pill status-${slug}" style="color: ${palette.color}; background-color: ${palette.background}; border: 1px solid ${palette.border};">${value}</span>`;
  };

  private toStatusSlug(value: string): string {
    return value
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\w\s-]/g, '')
      .trim()
      .toLowerCase()
      .replace(/\s+/g, '-');
  }

  private extractMessage(error: unknown, fallback: string): string {
    if (error instanceof Error && error.message) {
      return error.message;
    }

    return fallback;
  }
}
