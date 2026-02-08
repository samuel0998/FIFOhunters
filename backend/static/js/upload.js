async function uploadExcel() {
  const fileInput = document.getElementById("file");
  const msg = document.getElementById("msg");

  msg.textContent = "";
  msg.className = "msg";

  if (fileInput.files.length === 0) {
    msg.textContent = "❌ Selecione um arquivo .xlsx";
    msg.classList.add("error");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const response = await fetch("/api/upload/excel", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Erro ao enviar arquivo");
    }

    msg.textContent = `✅ Upload concluído! Registros inseridos: ${data.registros_inseridos}`;
    msg.classList.add("success");

    fileInput.value = "";
  } catch (err) {
    msg.textContent = "❌ " + err.message;
    msg.classList.add("error");
  }
}


async function scanValor() {
  const input = document.getElementById("scanInput").value.trim();
  const result = document.getElementById("result");

  if (!input) {
    alert("Digite ou escaneie um valor");
    return;
  }

  result.innerHTML = "<p>Buscando...</p>";

  try {
    const res = await fetch(`/api/scan?q=${input}`);
    const data = await res.json();

    if (!res.ok) {
      result.innerHTML = `<p>${data.error}</p>`;
      return;
    }

    result.innerHTML = data.map(item => `
      <div class="fifo-card ${item.status}">
        <h3>${item.descricao}</h3>

        <p><b>ISD:</b> ${item.isd}</p>
        <p><b>NF-e:</b> ${item.nfe_id}</p>

        <p><b>Data abertura:</b> ${formatDate(item.opened_since)}</p>
        <p><b>FIFO Days:</b> ${item.fifo_days}</p>

        <p><b>Esperado:</b> ${item.expected}</p>
        <p><b>Recebido:</b> ${item.received}</p>
        <p><b>Falta receber:</b> ${item.falta_receber}</p>

        <span class="status ${item.status}">${item.status}</span>
      </div>
    `).join("");

  } catch (err) {
    result.innerHTML = "<p>Erro ao consultar o servidor</p>";
  }
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return d.toLocaleDateString("pt-BR");
}

