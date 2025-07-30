document.addEventListener("DOMContentLoaded", function () {
    const cantidades = document.querySelectorAll(".cantidad");
    const totalElement = document.getElementById("total");
    const form = document.getElementById("facturaForm");

    cantidades.forEach(input => {
        input.addEventListener("input", actualizarTotales);
    });

    function actualizarTotales() {
        let total = 0;
        document.querySelectorAll("tbody tr").forEach(fila => {
            const precio = parseFloat(fila.querySelector(".precio").value);
            const cantidad = parseInt(fila.querySelector(".cantidad").value) || 0;
            const subtotal = precio * cantidad;
            fila.querySelector(".subtotal").textContent = `$${subtotal}`;
            total += subtotal;
        });
        totalElement.textContent = `$${total}`;
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        let productosSeleccionados = [];

        document.querySelectorAll("tbody tr").forEach((fila, index) => {
            const id = parseInt(fila.getAttribute("data-id"));
            const precio = parseFloat(fila.querySelector(".precio").value);
            const cantidad = parseInt(fila.querySelector(".cantidad").value);

            if (cantidad > 0) {
                productosSeleccionados.push({
                    id_grupo_producto: id,
                    cantidad: cantidad,
                    subtotal: cantidad * precio
                });
            }
        });

        const total = productosSeleccionados.reduce((sum, p) => sum + p.subtotal, 0);

        fetch("/facturar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
            productos: productosSeleccionados,
            total: total
        })

        })
        .then(res => res.json())
        .then(data => {
            alert(data.mensaje || "✅ Factura creada");
            window.location.reload();
        })
        .catch(err => {
            alert("❌ Error al crear factura");
            console.error(err);
        });
    });
});

