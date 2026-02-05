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
