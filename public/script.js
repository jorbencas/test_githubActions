let selSemana = { tipo: "all_recent", ini: null, fin: null };
let selCanal = "all";

// Función para los Chips (Reciente)
function filtrarSemana(el) {
  document
    .querySelectorAll("filter-group .chip")
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
    document
      .querySelectorAll("filter-group .chip")
      .forEach((c) => c.classList.remove("active"));
    const [ini, fin] = el.value.split("|");
    selSemana.tipo = "range";
    selSemana.ini = new Date(ini).getTime();
    selSemana.fin = new Date(fin).getTime();
  }
  aplicarFiltros();
}

function aplicarFiltros() {
  const ahora = new Date().getTime();
  const limiteReciente = ahora - 14 * 24 * 60 * 60 * 1000;

  document.querySelectorAll(".card, .news-item").forEach((item) => {
    const tsAttr = item.getAttribute("data-ts");
    if (!tsAttr) return; // Seguridad si falta el atributo

    const itemTS = new Date(tsAttr).getTime();
    const itemFuente = item.getAttribute("data-fuente");

    let okSemana = false;
    if (selSemana.tipo === "all_recent") {
      okSemana = itemTS >= limiteReciente;
    } else if (selSemana.tipo === "range") {
      okSemana = itemTS >= selSemana.ini && itemTS <= selSemana.fin;
    }

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
    const chips = el.parentElement.querySelectorAll('.chip');
    console.log(chips);
    chips.forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    selCanal = canal;
    aplicarFiltros();
  }