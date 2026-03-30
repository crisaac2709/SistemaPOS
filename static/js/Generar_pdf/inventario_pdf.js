// Función exportar PDF de inventario con diseño mejorado
function exportarInventarioPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Colores de la paleta con #52c2e8
    const colors = {
        primaryBlue: [30, 64, 175],      // Azul principal
        lightBlue: [219, 234, 254],      // Azul claro
        mediumBlue: [59, 130, 246],      // Azul medio
        darkBlue: [15, 23, 42],          // Azul oscuro
        white: [255, 255, 255],          // Blanco
        lightGray: [248, 250, 252]       // Gris muy claro
    };
    
    // Obtener datos del filtro actual
    const umbralInput = document.getElementById('umbral');
    const categoriaSelect = document.getElementById('categoria');
    const marcaSelect = document.getElementById('marca');
    
    const umbral = umbralInput ? umbralInput.value : 'No definido';
    const categoria = categoriaSelect ? categoriaSelect.options[categoriaSelect.selectedIndex].text : 'Todas';
    const marca = marcaSelect ? marcaSelect.options[marcaSelect.selectedIndex].text : 'Todas';
    
    // Contar productos por estado desde la tabla
    let totalProductos = 0;
    let productosStockBajo = 0;
    let productosStockOk = 0;
    
    const tabla = document.getElementById("tabla-inventario");
    const filas = tabla.querySelectorAll("tbody tr");
    
    filas.forEach(fila => {
        const estadoCell = fila.querySelector('td:last-child');
        if (estadoCell && estadoCell.textContent.trim() !== 'No se encontraron productos') {
            totalProductos++;
            if (estadoCell.textContent.includes('BAJO STOCK')) {
                productosStockBajo++;
            } else if (estadoCell.textContent.includes('STOCK OK')) {
                productosStockOk++;
            }
        }
    });
    
    // Configurar página
    const pageWidth = doc.internal.pageSize.width;
    const pageHeight = doc.internal.pageSize.height;
    
    // Header con fondo azul
    doc.setFillColor(...colors.primaryBlue);
    doc.rect(0, 0, pageWidth, 35, 'F');
    
    // Título principal en blanco
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.text("REPORTE DE INVENTARIO", pageWidth / 2, 20, { align: 'center' });
    
    // Línea decorativa
    doc.setDrawColor(...colors.lightBlue);
    doc.setLineWidth(2);
    doc.line(14, 37, pageWidth - 14, 37);
    
    // Información de filtros aplicados
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text("Filtros Aplicados", 14, 48);
    
    // Caja de filtros con fondo azul claro
    doc.setFillColor(...colors.lightBlue);
    doc.rect(14, 52, pageWidth - 28, 20, 'F');
    
    // Borde de la caja
    doc.setDrawColor(...colors.mediumBlue);
    doc.setLineWidth(0.5);
    doc.rect(14, 52, pageWidth - 28, 20);
    
    // Contenido de filtros
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(9);
    doc.setFont(undefined, 'normal');
    
    doc.setFont(undefined, 'bold');
    doc.text("Umbral Stock Bajo:", 18, 60);
    doc.setFont(undefined, 'normal');
    doc.text(umbral, 55, 60);
    
    doc.setFont(undefined, 'bold');
    doc.text("Categoría:", 90, 60);
    doc.setFont(undefined, 'normal');
    doc.text(categoria, 115, 60);
    
    doc.setFont(undefined, 'bold');
    doc.text("Marca:", 18, 67);
    doc.setFont(undefined, 'normal');
    doc.text(marca, 35, 67);
    
    // Resumen estadístico
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text("Resumen del Inventario", 14, 85);
    
    // Cajas de resumen
    const boxWidth = (pageWidth - 42) / 3;
    const startX = 14;
    const startY = 90;
    
    // Total productos
    doc.setFillColor(...colors.lightBlue);
    doc.rect(startX, startY, boxWidth, 20, 'F');
    doc.setDrawColor(...colors.mediumBlue);
    doc.setLineWidth(0.5);
    doc.rect(startX, startY, boxWidth, 20);
    
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    doc.text("Total Productos", startX + 2, startY + 7);
    doc.setTextColor(...colors.primaryBlue);
    doc.setFontSize(16);
    doc.text(totalProductos.toString(), startX + boxWidth/2, startY + 15, { align: 'center' });
    
    // Stock bajo
    doc.setFillColor(255, 243, 243); // Fondo rojo claro
    doc.rect(startX + boxWidth + 4, startY, boxWidth, 20, 'F');
    doc.setDrawColor(239, 68, 68); // Borde rojo
    doc.rect(startX + boxWidth + 4, startY, boxWidth, 20);
    
    doc.setTextColor(185, 28, 28); // Texto rojo
    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    doc.text("Stock Bajo", startX + boxWidth + 6, startY + 7);
    doc.setFontSize(16);
    doc.text(productosStockBajo.toString(), startX + boxWidth + 4 + boxWidth/2, startY + 15, { align: 'center' });
    
    // Stock OK
    doc.setFillColor(240, 253, 244); // Fondo verde claro
    doc.rect(startX + (boxWidth + 4) * 2, startY, boxWidth, 20, 'F');
    doc.setDrawColor(34, 197, 94); // Borde verde
    doc.rect(startX + (boxWidth + 4) * 2, startY, boxWidth, 20);
    
    doc.setTextColor(21, 128, 61); // Texto verde
    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    doc.text("Stock OK", startX + (boxWidth + 4) * 2 + 2, startY + 7);
    doc.setFontSize(16);
    doc.text(productosStockOk.toString(), startX + (boxWidth + 4) * 2 + boxWidth/2, startY + 15, { align: 'center' });
    
    // Título de la tabla
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text("Detalle del Inventario", 14, 125);
    
    // Preparar datos de la tabla
    const datos = [];
    const headers = [];
    
    // Encabezados
    tabla.querySelectorAll("thead tr th").forEach(th => {
        headers.push(th.innerText.trim());
    });
    
    // Filas
    tabla.querySelectorAll("tbody tr").forEach(tr => {
        const fila = [];
        tr.querySelectorAll("td").forEach((td, index) => {
            // Limpiar el texto del estado (quitar iconos SVG)
            if (index === 5) { // Columna de estado
                if (td.textContent.includes('BAJO STOCK')) {
                    fila.push('BAJO STOCK');
                } else if (td.textContent.includes('STOCK OK')) {
                    fila.push('STOCK OK');
                } else {
                    fila.push(td.innerText.trim());
                }
            } else {
                fila.push(td.innerText.trim());
            }
        });
        if (fila.length > 0 && !fila[0].includes('No se encontraron')) {
            datos.push(fila);
        }
    });
    
    // Generar tabla con diseño mejorado
    doc.autoTable({
        startY: 130,
        head: [headers],
        body: datos,
        theme: 'grid',
        styles: { 
            fontSize: 8,
            cellPadding: 3,
            textColor: colors.darkBlue,
            lineColor: colors.mediumBlue,
            lineWidth: 0.1
        },
        headStyles: { 
            fillColor: colors.primaryBlue,
            textColor: colors.white,
            fontSize: 9,
            fontStyle: 'bold',
            halign: 'center'
        },
        alternateRowStyles: {
            fillColor: colors.lightGray
        },
        columnStyles: {
            0: { halign: 'center', cellWidth: 15 },  // # - más estrecho
            1: { halign: 'left', cellWidth: 45 },    // Producto - más ancho
            2: { halign: 'left', cellWidth: 30 },    // Marca
            3: { halign: 'left', cellWidth: 35 },    // Categoría
            4: { halign: 'center', cellWidth: 25 },  // Stock Actual
            5: { halign: 'center', cellWidth: 30 }   // Estado
        },
        // Colorear filas según estado
        didParseCell: function(data) {
            if (data.column.index === 5 && data.cell.raw === 'BAJO STOCK') {
                data.cell.styles.textColor = [185, 28, 28]; // Rojo
                data.cell.styles.fillColor = [254, 242, 242]; // Fondo rojo claro
            } else if (data.column.index === 5 && data.cell.raw === 'STOCK OK') {
                data.cell.styles.textColor = [21, 128, 61]; // Verde
                data.cell.styles.fillColor = [240, 253, 244]; // Fondo verde claro
            }
            // Colorear stock bajo en números también
            if (data.column.index === 4 && data.row.index >= 0) {
                const estado = datos[data.row.index][5];
                if (estado === 'BAJO STOCK') {
                    data.cell.styles.textColor = [185, 28, 28]; // Rojo
                    data.cell.styles.fontStyle = 'bold';
                }
            }
        },
        margin: { left: 14, right: 14 },
        didDrawPage: function(data) {
            // Footer en cada página
            const pageNumber = doc.internal.getNumberOfPages();
            const currentPage = doc.internal.getCurrentPageInfo().pageNumber;
            
            // Línea del footer
            doc.setDrawColor(...colors.lightBlue);
            doc.setLineWidth(1);
            doc.line(14, pageHeight - 20, pageWidth - 14, pageHeight - 20);
            
            // Texto del footer
            doc.setTextColor(...colors.mediumBlue);
            doc.setFontSize(8);
            doc.setFont(undefined, 'normal');
            
            // Fecha de generación
            const fechaGeneracion = new Date().toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            doc.text(`Generado el: ${fechaGeneracion}`, 14, pageHeight - 12);
            doc.text(`Página ${currentPage} de ${pageNumber}`, pageWidth - 14, pageHeight - 12, { align: 'right' });
        }
    });
    
    // Guardar el archivo
    const fechaActual = new Date().toISOString().split('T')[0];
    const fileName = `reporte_inventario_${fechaActual}.pdf`;
    doc.save(fileName);
}

// Función exportar CSV (sin cambios)
function exportarInventarioCSV() {
    const tabla = document.getElementById("tabla-inventario");
    let csv = [];
    const filas = tabla.querySelectorAll("tr");
    
    filas.forEach(fila => {
        const columnas = fila.querySelectorAll("th, td");
        const filaCSV = Array.from(columnas).map(col => {
            // Limpiar texto de estado para CSV
            let texto = col.innerText.trim();
            if (texto.includes('BAJO STOCK')) {
                texto = 'BAJO STOCK';
            } else if (texto.includes('STOCK OK')) {
                texto = 'STOCK OK';
            }
            return `"${texto}"`;
        }).join(",");
        csv.push(filaCSV);
    });
    
    const blob = new Blob([csv.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    
    const enlace = document.createElement("a");
    const fechaActual = new Date().toISOString().split('T')[0];
    enlace.setAttribute("href", url);
    enlace.setAttribute("download", `reporte_inventario_${fechaActual}.csv`);
    document.body.appendChild(enlace);
    enlace.click();
    document.body.removeChild(enlace);
}