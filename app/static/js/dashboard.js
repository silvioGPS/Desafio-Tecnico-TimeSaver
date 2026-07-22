document.addEventListener("DOMContentLoaded", () => {
  const tableElement = document.getElementById("appointments-table");
  const searchForm = document.getElementById("search-form");
  const searchInput = document.getElementById("search-input");
  const resetButton = document.getElementById("reset-search");
  const statusMessage = document.getElementById("status-message");

  const table = new Tabulator(tableElement, {
    data: [],
    layout: "fitColumns",
    responsiveLayout: "collapse",
    height: "100%",
    placeholder: "Nenhum agendamento disponível.",
    columns: [
      { title: "Data", field: "date", width: 130, sorter: "string", formatter: formatDate },
      { title: "Horário", field: "time", width: 110 },
      { title: "Paciente", field: "patient", minWidth: 180 },
      { title: "CPF", field: "cpf", width: 150 },
      { title: "Médico", field: "doctor", minWidth: 200 },
      { title: "Especialidade", field: "specialty", minWidth: 160 },
      { title: "Convênio", field: "insurance", minWidth: 160 },
      { title: "Status", field: "status", width: 140, formatter: statusFormatter },
    ],
  });

  async function loadAppointments(search = "") {
    statusMessage.textContent = "Carregando agenda...";
    statusMessage.dataset.state = "loading";

    try {
      const response = await fetch(`/appointments/data?search=${encodeURIComponent(search)}`);
      const payload = await response.json();

      if (!response.ok || !payload.ok) {
        throw new Error(payload.message || "Não foi possível carregar os agendamentos.");
      }

      await table.setData(payload.records || []);
      statusMessage.textContent = payload.message || "Agenda atualizada.";
      statusMessage.dataset.state = (payload.records || []).length === 0 ? "empty" : "success";
    } catch (error) {
      await table.setData([]);
      statusMessage.textContent = error.message;
      statusMessage.dataset.state = "error";
    }
  }

  function formatDate(cell) {
    const value = cell.getValue();
    if (!value) {
      return "-";
    }

    const [year, month, day] = String(value).split("-");
    if (!year || !month || !day) {
      return value;
    }

    return `${day}/${month}/${year}`;
  }

  function statusFormatter(cell) {
    const value = (cell.getValue() || "").toString();
    return `<span class="status-pill status-${slugify(value)}">${value}</span>`;
  }

  function slugify(value) {
    return value
      .normalize("NFD")
      .replace(/[^\w\s-]/g, "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-");
  }

  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    loadAppointments(searchInput.value.trim());
  });

  resetButton.addEventListener("click", () => {
    searchInput.value = "";
    loadAppointments("");
  });

  loadAppointments("");
});