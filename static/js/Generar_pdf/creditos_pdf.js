function exportarCreditosPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Paleta de colores reutilizada
    const colors = {
        primaryBlue: [30, 64, 175],
        lightBlue: [219, 234, 254],
        mediumBlue: [59, 130, 246],
        darkBlue: [15, 23, 42],
        white: [255, 255, 255],
        lightGray: [248, 250, 252]
    };

    const pageWidth = doc.internal.pageSize.width;
    const pageHeight = doc.internal.pageSize.height;

    // Encabezado
    doc.setFillColor(...colors.primaryBlue);
    doc.rect(0, 0, pageWidth, 35, 'F');

    doc.setTextColor(...colors.white);
    doc.setFontSize(20);
    doc.setFont(undefined, 'bold');
    doc.text("REPORTE DE CRÉDITOS OTORGADOS", pageWidth / 2, 20, { align: 'center' });

    doc.setDrawColor(...colors.lightBlue);
    doc.setLineWidth(2);
    doc.line(14, 37, pageWidth - 14, 37);

    // Subtítulo informativo
    doc.setTextColor(...colors.darkBlue);
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text("Detalle de Créditos", 14, 48);

    // Obtener tabla
    const tabla = document.querySelector("table");
    if (!tabla) {
        alert("No se encontró la tabla para exportar.");
        return;
    }

    const headers = Array.from(tabla.querySelectorAll("thead th")).map(th => th.innerText.trim());
    const rows = Array.from(tabla.querySelectorAll("tbody tr"))
        .filter(tr => tr.querySelectorAll("td").length > 0)
        .map(tr => Array.from(tr.querySelectorAll("td")).map(td => td.innerText.trim()));

    // Tabla con diseño
    doc.autoTable({
        startY: 53,
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
        margin: { left: 14, right: 14 },
        didDrawPage: function (data) {
            // Footer
            const pageNumber = doc.internal.getNumberOfPages();
            const currentPage = doc.internal.getCurrentPageInfo().pageNumber;

            doc.setDrawColor(...colors.lightBlue);
            doc.setLineWidth(1);
            doc.line(14, pageHeight - 20, pageWidth - 14, pageHeight - 20);

            doc.setTextColor(...colors.mediumBlue);
            doc.setFontSize(8);
            doc.setFont(undefined, 'normal');

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

    doc.save("reporte_creditos.pdf");
}