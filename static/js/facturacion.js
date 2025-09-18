document.addEventListener("DOMContentLoaded", function () {
    console.log("📦 JS cargado");

    const form = document.getElementById("facturaForm");
    const totalElement = document.getElementById("total");

    function actualizarTotales() {
        let total = 0;

        document.querySelectorAll("tbody tr").forEach(fila => {
            const precio = parseFloat(fila.querySelector(".precio").value);
            const cantidadInput = fila.querySelector(".cantidad");
            const cantidad = parseInt(cantidadInput.value) || 0;
            const subtotal = precio * cantidad;

            // Debug
            console.log(`Producto ID: ${fila.dataset.id}, Precio: ${precio}, Cantidad: ${cantidad}, Subtotal: ${subtotal}`);

            fila.querySelector(".subtotal").textContent = `$${subtotal}`;
            total += subtotal;
        });

        totalElement.textContent = `$${total}`;
        console.log("💰 Total actualizado:", total);
    }

    // Asignar evento a cada input .cantidad (esto va después de definir la función)
    document.querySelectorAll(".cantidad").forEach(input => {
        input.addEventListener("input", actualizarTotales);
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        let productosSeleccionados = [];

        document.querySelectorAll("tbody tr").forEach(fila => {
            const id = parseInt(fila.getAttribute("data-id"));
            const precio = parseFloat(fila.querySelector(".precio").value);
            const cantidad = parseInt(fila.querySelector(".cantidad").value) || 0;

            if (cantidad > 0) {
                productosSeleccionados.push({
                    id_grupo_producto: id,
                    cantidad: cantidad,
                    subtotal: precio * cantidad
                });
            }
        });

        const total = productosSeleccionados.reduce((sum, p) => sum + p.subtotal, 0);

         if (rol_usuario !== "administrador") {
            alert("❌ No tienes permisos para crear facturas");
            return;
         }

        fetch("/facturar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                productos: productosSeleccionados,
                total: total,
                id_usuario: id_usuario
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
