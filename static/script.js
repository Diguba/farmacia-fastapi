function startScanner() {
    const scanner = document.getElementById("scanner");
    scanner.style.display = "block";
    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: scanner
        },
        decoder: {
            readers: ["ean_reader", "ean_8_reader"]
        }
    }, function (err) {
        if (err) return console.error(err);
        Quagga.start();
    });

    Quagga.onDetected(function (result) {
        const code = result.codeResult.code;
        document.getElementById("codigoInput").value = code;
        Quagga.stop();
        scanner.style.display = "none";
    });
}

// Botón editar: llena el formulario
function editar(id) {
    fetch(`/api/medicamento/${id}`)
        .then(res => res.json())
        .then(data => {
            document.querySelector('input[name=nombre]').value = data.nombre;
            document.querySelector('input[name=codigo]').value = data.codigo;
            document.querySelector('input[name=precio]').value = data.precio;
            document.querySelector('select[name=tipo]').value = data.tipo;
            document.querySelector('select[name=presentacion]').value = data.presentacion;
            document.querySelector('input[name=sustancia1]').value = data.sustancias[0] || '';
            document.querySelector('input[name=concentracion1]').value = data.concentraciones[0] || '';
            document.querySelector('input[name=sustancia2]').value = data.sustancias[1] || '';
            document.querySelector('input[name=concentracion2]').value = data.concentraciones[1] || '';
        });
}

// Búsqueda dinámica
document.addEventListener("DOMContentLoaded", () => {
    const search = document.getElementById("buscador");
    if (search) {
        search.addEventListener("input", () => {
            const q = search.value;
            fetch(`/api/sugerencias?q=${encodeURIComponent(q)}`)
                .then(res => res.json())
                .then(data => {
                    const ul = document.getElementById("lista-medicamentos");
                    if (!ul) return;

                    ul.innerHTML = "";

                    if (data.coincidencias.length > 0) {
                        data.coincidencias.forEach(n => {
                            const li = document.createElement("li");
                            li.textContent = n;
                            ul.appendChild(li);
                        });
                    } else if (data.sugerencia) {
                        const li = document.createElement("li");
                        li.textContent = data.sugerencia;
                        ul.appendChild(li);
                    }
                });
        });
    }
});
