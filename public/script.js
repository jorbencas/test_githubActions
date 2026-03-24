let selSemana = { tipo: "all_recent", ini: null, fin: null };
let selCanal = "all";

// Función para los Chips (Reciente)
function filtrarSemana(el) {
  el.parentElement
    .querySelectorAll(".chip")
    .forEach((c) => c.classList.remove("active"));
  document.getElementById("selectorSemanas").value = "all";
  el.classList.add("active");

  if (el.getAttribute("data-inicio") === "all_recent") {
    selSemana.tipo = "all_recent";
  }
  aplicarFiltros();
}

// Función para el Selector Agrupado
function filtrarDesdeSelector(el) {
  if (el.value === "all") {
    // Si vuelve a la opción por defecto, mostramos "Reciente"
    selSemana.tipo = "all_recent";
    document
      .querySelector('.chip[data-inicio="all_recent"]')
      .classList.add("active");
  } else {
    el.parentElement
      .querySelectorAll(".chip")
      .forEach((c) => c.classList.remove("active"));
    const [ini, fin] = el.value.split("|");
    selSemana.tipo = "range";
    selSemana.ini = new Date(ini).getTime();
    selSemana.fin = new Date(fin).getTime();
  }
  aplicarFiltros();
}

// CAMBIO: Asegúrate de que la definición acepte el parámetro por defecto
function aplicarFiltros(afectarNoticias = true) {
  // Usamos un nombre más claro
  const ahora = new Date().getTime();
  const limiteReciente = ahora - 14 * 24 * 60 * 60 * 1000;

  // Si afectarNoticias es false (desde filtrarCanal), el selector SOLO coge vídeos.
  // Esto hace que las noticias ni se oculten ni se muestren: se quedan como estaban.
  let itemsfiler = afectarNoticias ? ".card, .news-item" : ".card";

  document.querySelectorAll(itemsfiler).forEach((item) => {
    const tsAttr = item.getAttribute("data-ts");
    if (!tsAttr) return;

    const itemTS = new Date(tsAttr).getTime();
    const itemFuente = item.getAttribute("data-fuente");

    // Lógica de tiempo (Semanas)
    let okSemana = false;
    if (selSemana.tipo === "all_recent") {
      okSemana = itemTS >= limiteReciente;
    } else if (selSemana.tipo === "range") {
      okSemana = itemTS >= selSemana.ini && itemTS <= selSemana.fin;
    }

    // Lógica de Canal
    const okCanal = selCanal === "all" || itemFuente === selCanal;

    if (okSemana && okCanal) {
      item.style.display = item.classList.contains("news-item")
        ? "list-item"
        : "block";
    } else {
      item.style.display = "none";
    }
  });
}

function filtrarCanal(canal, el) {
  const chips = el.parentElement.querySelectorAll(".chip");
  console.log(chips);
  chips.forEach((c) => c.classList.remove("active"));
  el.classList.add("active");
  selCanal = canal;
  aplicarFiltros(false);
}



async function descargarVideo(urlVideo, boton) {
  const originalText = boton.innerHTML;
  boton.innerHTML = "⏳..."; // Feedback visual

  const API_BASE = "https://tu-api.koyeb.app/download";
  const TOKEN = "TU_CLAVE_MAESTRA_9922";

  try {
    const response = await fetch(
      `${API_BASE}?url=${encodeURIComponent(urlVideo)}&token=${TOKEN}`
    );
    const data = await response.json();

    if (data.url) {
      // Creamos un link temporal y simulamos el click para descargar
      const a = document.createElement("a");
      a.href = data.url;
      a.download = data.title + ".mp4"; // Intenta forzar nombre de archivo
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      boton.innerHTML = "✅";
    } else {
      alert("No se pudo obtener el link directo.");
      boton.innerHTML = "❌";
    }
  } catch (error) {
    console.error("Error:", error);
    boton.innerHTML = "❌";
  } finally {
    setTimeout(() => (boton.innerHTML = originalText), 3000);
  }
}