// Función exportar PDF con diseño mejorado
async function exportarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Colores de la paleta azul y blanco
    const colors = {
        primaryBlue: [30, 64, 175],      // Azul principal
        lightBlue: [219, 234, 254],      // Azul claro
        mediumBlue: [59, 130, 246],      // Azul medio
        darkBlue: [15, 23, 42],          // Azul oscuro
        white: [255, 255, 255],          // Blanco
        lightGray: [248, 250, 252]       // Gris muy claro
    };
    
    // Obtener datos
    const fechaDesde = document.getElementById('fecha_desde').value || '---';
    const fechaHasta = document.getElementById('fecha_hasta').value || '---';
    const totalVentas = document.querySelector('[data-total-ventas]')?.textContent || '0.00';
    const numTransacciones = document.querySelector('[data-num-transacciones]')?.textContent || '0';
    
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
    doc.text("REPORTE DE VENTAS", pageWidth / 2, 20, { align: 'center' });
    
    // Línea decorativa
    doc.setDrawColor(...colors.lightBlue);
    doc.setLineWidth(2);
    doc.line(14, 37, pageWidth - 14, 37);
    
    // Información del período
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text("Información del Período", 14, 48);
    
    // Caja de información con fondo azul claro
    doc.setFillColor(...colors.lightBlue);
    doc.rect(14, 52, pageWidth - 28, 25, 'F');
    
    // Borde de la caja
    doc.setDrawColor(...colors.mediumBlue);
    doc.setLineWidth(0.5);
    doc.rect(14, 52, pageWidth - 28, 25);
    
    // Contenido de la información
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    
    // Primera fila de información
    doc.setFont(undefined, 'bold');
    doc.text("Período:", 18, 62);
    doc.setFont(undefined, 'normal');
    doc.text(`${fechaDesde} al ${fechaHasta}`, 45, 62);
    
    // Segunda fila de información
    doc.setFont(undefined, 'bold');
    doc.text("Total de Ventas:", 18, 69);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(...colors.primaryBlue);
    doc.setFontSize(11);
    doc.text(totalVentas, 60, 69);
    
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    doc.text("N° Transacciones:", 120, 69);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(...colors.primaryBlue);
    doc.setFontSize(11);
    doc.text(numTransacciones, 165, 69);
    
    // Título de la tabla
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text("Detalle de Transacciones", 14, 90);
    
    // Preparar datos de la tabla
    const table = document.querySelector("#tabla-ventas");
    const headers = Array.from(table.querySelectorAll("thead th")).map(th => th.innerText.trim());
    const rows = Array.from(table.querySelectorAll("tbody tr"))
        .filter(tr => tr.querySelectorAll("td").length > 0)
        .map(tr => Array.from(tr.querySelectorAll("td")).map(td => td.innerText.trim()));
    
    // Generar tabla con diseño mejorado
    doc.autoTable({
        startY: 95,
        head: [headers],
        body: rows,
        theme: 'grid',
        styles: { 
            fontSize: 9,
            cellPadding: 4,
            textColor: colors.darkBlue,
            lineColor: colors.mediumBlue,
            lineWidth: 0.1
        },
        headStyles: { 
            fillColor: colors.primaryBlue,
            textColor: colors.white,
            fontSize: 10,
            fontStyle: 'bold',
            halign: 'center'
        },
        alternateRowStyles: {
            fillColor: colors.lightGray
        },
        columnStyles: {
            0: { halign: 'center' },  // ID centrado
            1: { halign: 'left' },    // Fecha alineada a la izquierda
            2: { halign: 'right' },   // Monto alineado a la derecha
            3: { halign: 'center' }   // Estado centrado
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
    const fileName = `reporte_ventas_${fechaDesde}_a_${fechaHasta}.pdf`;
    doc.save(fileName);
}

// Función exportar CSV (sin cambios)
function exportarCSV() {
    const table = document.querySelector("#tabla-ventas");
    const rows = table.querySelectorAll("tr");
    let csvContent = "";
    
    rows.forEach(row => {
        const cols = row.querySelectorAll("th, td");
        const line = Array.from(cols).map(col => `"${col.innerText.trim()}"`).join(",");
        csvContent += line + "\n";
    });
    
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const fechaDesde = document.getElementById('fecha_desde').value || 'inicio';
    const fechaHasta = document.getElementById('fecha_hasta').value || 'fin';
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", `reporte_ventas_${fechaDesde}_a_${fechaHasta}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}