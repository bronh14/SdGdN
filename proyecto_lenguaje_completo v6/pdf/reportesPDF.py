from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import os
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Spacer, PageBreak
from config import database
import datetime
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
imagen1 = os.path.join(BASE_DIR, "..", "img", "logo1.jpeg")
imagen2 = os.path.join(BASE_DIR, "..", "img", "logo3.jpeg")


def estudiantesPorCarrera(self, carreras, valores, fileName, usuario):
    data = [["Nombre y Apellido", "Cédula", "Carrera", "Semestre"]]
    estudiantes = database.get_all_estudiantes_info()
    data.extend(estudiantes)

    table = Table(data, colWidths=[160, 100, 130, 80])
    style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ]
        + [
            (
                "BACKGROUND",
                (0, i),
                (-1, i),
                colors.whitesmoke if i % 2 == 0 else colors.lightgrey,
            )
            for i in range(1, len(data))
        ]
    )
    table.setStyle(style)

    def encabezado(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(300, 730, "REPUBLICA BOLIVARIANA DE VENEZUELA")
        canvas.drawCentredString(
            300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
        )
        canvas.drawCentredString(300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL")
        canvas.drawCentredString(300, 685, "POLITECNICA DE LAS FUERZAS ARMADAS")
        canvas.drawCentredString(300, 670, "NUCLEO PTO. CABELLO - EDO. CARABOBO")
        canvas.drawImage(imagen1, 30, 670, width=100, height=100)
        canvas.drawImage(imagen2, 470, 670, width=100, height=100)
        canvas.setFont("Helvetica-Bold", 22)
        canvas.setFillColor(colors.HexColor("#1e293b"))
        canvas.drawCentredString(300, 630, "REPORTE DE ESTUDIANTES POR CARRERA")
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica", 12)
        now = datetime.datetime.now()
        fecha_actual = now.strftime("%Y-%m-%d")
        hora_actual = now.strftime("%H:%M:%S")
        canvas.drawString(30, 600, f"Fecha: {fecha_actual}")
        canvas.drawString(30, 580, f"Hora: {hora_actual}")
        canvas.drawString(30, 560, f"Usuario: {usuario}")
        canvas.drawString(30, 540, "Tipo de Reporte: Estudiantes por Carrera")
        total_estudiantes = database.get_total_estudiantes()
        canvas.drawString(30, 520, f"Total de Estudiantes: {total_estudiantes}")
        canvas.restoreState()

    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            570, 20, f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        canvas.restoreState()

    elements = []
    elements.append(Spacer(1, 260))  # Espacio entre encabezado y tabla
    elements.append(table)
    elements.append(Spacer(1, 50))  # Espacio entre tabla principal y resumen

    # Título del resumen
    resumen_titulo = Table(
        [["Resumen por Carrera"]],
        colWidths=[400],
        style=[
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 15),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
        ],
    )
    elements.append(resumen_titulo)
    elements.append(Spacer(1, 20))

    # Tabla resumen
    resumen_data = [["Carrera", "Cantidad de Estudiantes"]]
    for i, carrera in enumerate(carreras):
        resumen_data.append([carrera, valores[i]])

    resumen_table = Table(resumen_data, colWidths=[220, 180])
    resumen_style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ]
        + [
            (
                "BACKGROUND",
                (0, i),
                (-1, i),
                colors.whitesmoke if i % 2 == 0 else colors.lightgrey,
            )
            for i in range(1, len(resumen_data))
        ]
    )
    resumen_table.setStyle(resumen_style)
    elements.append(resumen_table)

    doc = SimpleDocTemplate(fileName, pagesize=letter)
    doc.build(elements, onFirstPage=encabezado, onLaterPages=pie_pagina)
    os.startfile(fileName)


def profesoresPorCarrera(self, carreras, valores, fileName, usuario):
    elements = []
    style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ]
    )

    total_profesores = sum(
        cantidad for _, cantidad in database.get_profesores_por_carrera()
    )

    # Espacio inicial para que no se pegue al encabezado
    elements.append(Spacer(1, 250))

    for idx, (carrera, cantidad) in enumerate(database.get_profesores_por_carrera()):
        # Título de la carrera
        titulo_table = Table([[f"{carrera} (Total: {cantidad})"]], colWidths=[460])
        titulo_style = TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 15),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ]
        )
        titulo_table.setStyle(titulo_style)
        elements.append(titulo_table)
        elements.append(Spacer(1, 10))

        profesores = database.get_todos_los_profesores(carrera)
        data = [["Nombre", "Apellido", "Cédula", "Fecha Contratación"]]
        for prof in profesores:
            data.append([prof[0], prof[1], prof[2], prof[4]])
        # Alternar colores de filas
        prof_style = TableStyle(
            style.getCommands()
            + [
                (
                    "BACKGROUND",
                    (0, i),
                    (-1, i),
                    colors.whitesmoke if i % 2 == 0 else colors.lightgrey,
                )
                for i in range(1, len(data))
            ]
        )
        table = Table(data, colWidths=[120, 120, 100, 120])
        table.setStyle(prof_style)
        elements.append(table)
        # Espacio entre tablas, menos después de la última
        if idx < len(carreras) - 1:
            elements.append(Spacer(1, 40))

    def encabezado(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(300, 730, "REPUBLICA BOLIVARIANA DE VENEZUELA")
        canvas.drawCentredString(
            300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
        )
        canvas.drawCentredString(300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL")
        canvas.drawCentredString(300, 685, "POLITECNICA DE LAS FUERZAS ARMADAS")
        canvas.drawCentredString(300, 670, "NUCLEO PTO. CABELLO - EDO. CARABOBO")
        canvas.drawImage(imagen1, 30, 670, width=100, height=100)
        canvas.drawImage(imagen2, 470, 670, width=100, height=100)
        canvas.setFont("Helvetica-Bold", 22)
        canvas.setFillColor(colors.HexColor("#1e293b"))
        canvas.drawCentredString(300, 630, "REPORTE DE PROFESORES POR CARRERA")
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica", 12)
        now = datetime.datetime.now()
        fecha_actual = now.strftime("%Y-%m-%d")
        hora_actual = now.strftime("%H:%M:%S")
        canvas.drawString(30, 600, f"Fecha: {fecha_actual}")
        canvas.drawString(30, 580, f"Hora: {hora_actual}")
        canvas.drawString(30, 560, f"Usuario: {usuario}")
        canvas.drawString(30, 540, "Tipo de Reporte: Profesores por Carrera")
        canvas.drawString(30, 520, f"Total de Profesores: {total_profesores}")
        canvas.restoreState()

    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            570, 20, f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        canvas.restoreState()

    doc = SimpleDocTemplate(fileName, pagesize=letter)
    doc.build(elements, onFirstPage=encabezado, onLaterPages=pie_pagina)
    os.startfile(fileName)


# estudiantes por materias apartado del profesor


def estudiantesPorMaterias(self, resultado, fileName, usuario):
    # --- DATOS DE LA TABLA ---
    data = [["Nombre y Apellido", "Cedula", "Materia"]]
    # Aquí podrías agregar una función en database.py para obtener todos los estudiantes ordenados por carrera y semestre
    data.extend(resultado)

    # Agrupar y contar estudiantes por materia
    materias_conteo = {}
    for row in resultado:
        materia = row[
            2
        ]  # Suponiendo que la materia está en la tercera columna (índice 2)
        if materia not in materias_conteo:
            materias_conteo[materia] = 0
        materias_conteo[materia] += 1

    table = Table(data, colWidths=[150, 100, 120, 80])
    style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0, colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]
    )
    table.setStyle(style)

    def encabezado(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(300, 730, "REPUBLICA BOLIVARIANA DE VENEZUELA")
        canvas.drawCentredString(
            300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
        )
        canvas.drawCentredString(300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL")
        canvas.drawCentredString(300, 685, "POLITECNICA DE LAS FUERZAS ARMADAS")
        canvas.drawCentredString(300, 670, "NUCLEO PTO. CABELLO - EDO. CARABOBO")
        canvas.drawImage(imagen1, 30, 670, width=100, height=100)
        canvas.drawImage(imagen2, 470, 670, width=100, height=100)
        canvas.setFont("Helvetica-Bold", 20)
        canvas.drawCentredString(300, 630, "ESTUDIANTES POR MATERIA")
        canvas.setFont("Helvetica", 12)
        now = datetime.datetime.now()
        fecha_actual = now.strftime("%Y-%m-%d")
        hora_actual = now.strftime("%H:%M:%S")
        canvas.drawString(30, 600, f"Fecha: {fecha_actual}")
        canvas.drawString(30, 580, f"Hora: {hora_actual}")
        canvas.drawString(
            30, 560, f"Usuario: {usuario}"
        )  # Cambia tipo_usuario por el usuario actual
        canvas.drawString(30, 540, "Tipo de Reporte: Estudiantes por Materia")
        total_estudiantes = len(resultado)
        canvas.drawString(30, 520, f"Total de Estudiantes: {total_estudiantes}")
        canvas.restoreState()

    def sin_encabezado(canvas, doc):
        pass

    elements = []
    elements.append(Spacer(1, 220))
    elements.append(table)

    # --- TABLA RESUMEN POR CARRERA EN LA ÚLTIMA HOJA ---
    resumen_data = [["Materia", "Cantidad de Estudiantes"]]
    for materia, cantidad in materias_conteo.items():
        resumen_data.append([materia, cantidad])

    resumen_table = Table(resumen_data, colWidths=[220, 180])
    resumen_style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]
    )
    resumen_table.setStyle(resumen_style)

    elements.append(PageBreak())
    elements.append(Spacer(1, 40))
    elements.append(resumen_table)

    doc = SimpleDocTemplate(fileName, pagesize=letter)
    doc.build(elements, onFirstPage=encabezado, onLaterPages=sin_encabezado)

    os.startfile(fileName)


def materiasPorCarrera(self, fileName, usuario):
    carreras = database.get_carreras()
    materias_por_carrera = {}
    total_general = 0
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        for carrera in carreras:
            cursor.execute(
                """
                SELECT codigo, nombre, semestre, requisitos, creditos
                FROM materias
                WHERE carrera = ?
                ORDER BY semestre, nombre
                """,
                (carrera,),
            )
            materias = cursor.fetchall()
            materias_por_carrera[carrera] = materias
            total_general += len(materias)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    imagen1 = os.path.join(BASE_DIR, "..", "img", "logo1.jpeg")
    imagen2 = os.path.join(BASE_DIR, "..", "img", "logo3.jpeg")

    def encabezado(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(300, 730, "REPUBLICA BOLIVARIANA DE VENEZUELA")
        canvas.drawCentredString(
            300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
        )
        canvas.drawCentredString(300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL")
        canvas.drawCentredString(300, 685, "POLITECNICA DE LAS FUERZAS ARMADAS")
        canvas.drawCentredString(300, 670, "NUCLEO PTO. CABELLO - EDO. CARABOBO")
        canvas.drawImage(imagen1, 30, 670, width=100, height=100)
        canvas.drawImage(imagen2, 470, 670, width=100, height=100)
        canvas.setFont("Helvetica-Bold", 22)
        canvas.setFillColor(colors.HexColor("#1e293b"))
        canvas.drawCentredString(300, 630, "REPORTE DE MATERIAS POR CARRERA")
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica", 12)
        now = datetime.datetime.now()
        fecha_actual = now.strftime("%Y-%m-%d")
        hora_actual = now.strftime("%H:%M:%S")
        canvas.drawString(30, 600, f"Fecha: {fecha_actual}")
        canvas.drawString(30, 580, f"Hora: {hora_actual}")
        canvas.drawString(30, 560, f"Usuario: {usuario}")
        canvas.drawString(30, 540, "Tipo de Reporte: Materias por Carrera")
        canvas.restoreState()

    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            570, 20, f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        canvas.restoreState()

    elements = []
    elements.append(Spacer(1, 220))

    # Estilo para requisitos con salto de línea
    requisitos_style = ParagraphStyle(
        name="Requisitos",
        fontName="Helvetica",
        fontSize=8,
        alignment=1,  # center
        leading=9,
        wordWrap="CJK",
    )

    for carrera in carreras:
        materias = materias_por_carrera[carrera]
        # Agrupar materias por semestre
        materias_por_semestre = {}
        for mat in materias:
            semestre = mat[2]
            if semestre not in materias_por_semestre:
                materias_por_semestre[semestre] = []
            materias_por_semestre[semestre].append(mat)

        # Título de la carrera
        titulo_table = Table(
            [[f"{carrera} (Total de Materias: {len(materias)})"]],
            colWidths=[600],
            style=[
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 15),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ],
            hAlign="CENTER",
        )
        elements.append(titulo_table)
        elements.append(Spacer(1, 10))

        # Por cada semestre, una tabla
        for semestre in sorted(materias_por_semestre.keys()):
            # Subtítulo del semestre
            elements.append(
                Table(
                    [[f"Semestre {semestre}"]],
                    colWidths=[600],
                    style=[
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 12),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ],
                    hAlign="CENTER",
                )
            )
            elements.append(Spacer(1, 3))

            data = [
                [
                    Paragraph("Código", requisitos_style),
                    Paragraph("Nombre", requisitos_style),
                    Paragraph("Créditos", requisitos_style),
                    Paragraph("Requisitos", requisitos_style),
                ]
            ]
            for materia in materias_por_semestre[semestre]:
                requisitos = materia[3] if materia[3] else "Ninguno"
                # Usar Paragraph para salto de línea en requisitos largos
                requisitos_paragraph = Paragraph(requisitos, requisitos_style)
                data.append(
                    [
                        materia[0],  # Código
                        materia[1],  # Nombre
                        materia[4] if materia[4] is not None else "-",  # Créditos
                        requisitos_paragraph,
                    ]
                )
            mat_style = TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Código
                    ("ALIGN", (1, 1), (1, -1), "LEFT"),  # Nombre
                    ("ALIGN", (2, 1), (2, -1), "CENTER"),  # Créditos
                    ("ALIGN", (3, 1), (3, -1), "CENTER"),  # Requisitos
                ]
                + [
                    (
                        "BACKGROUND",
                        (0, i),
                        (-1, i),
                        colors.whitesmoke if i % 2 == 0 else colors.lightgrey,
                    )
                    for i in range(1, len(data))
                ]
            )
            mat_table = Table(data, colWidths=[75, 260, 50, 200], hAlign="CENTER")
            mat_table.setStyle(mat_style)
            elements.append(mat_table)
            elements.append(Spacer(1, 15))

    # Total general de materias
    total_general_table = Table(
        [[f"TOTAL GENERAL DE MATERIAS: {total_general}"]],
        colWidths=[600],
        style=[
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 14),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f39c12")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ],
        hAlign="CENTER",
    )
    elements.append(Spacer(1, 40))
    elements.append(total_general_table)

    doc = SimpleDocTemplate(fileName, pagesize=letter, rightMargin=20, leftMargin=20)
    doc.build(elements, onFirstPage=encabezado, onLaterPages=pie_pagina)
    os.startfile(fileName)


def generar_comprobante_inscripcion_pdf(
    file_path, materias, cedula, nombre, apellido, carrera
):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        Table,
        TableStyle,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime
    import uuid

    styles = getSampleStyleSheet()

    # Estilos
    unefa_title_style = ParagraphStyle(
        "UNEFATitle",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=2,
        alignment=1,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        leading=16,
    )
    header_info_style = ParagraphStyle(
        "HeaderInfo",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=2,
        alignment=1,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        leading=12,
    )
    doc_title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=5,
        alignment=1,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        leading=16,
    )
    student_info_style = ParagraphStyle(
        "StudentInfo",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=2,
        alignment=0,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        leading=12,
    )
    resumen_style = ParagraphStyle(
        "Resumen",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=8,
        alignment=1,
        fontName="Helvetica-Bold",
        textColor=colors.black,
    )
    legal_style = ParagraphStyle(
        "Legal",
        parent=styles["Normal"],
        fontSize=8,
        spaceAfter=8,
        alignment=4,
        fontName="Helvetica",
        textColor=colors.black,
        leading=9,
    )
    verificacion_style = ParagraphStyle(
        "Verificacion",
        parent=styles["Normal"],
        fontSize=8,
        spaceAfter=3,
        alignment=0,
        fontName="Helvetica",
        textColor=colors.black,
    )
    pie_style = ParagraphStyle(
        "Pie",
        parent=styles["Normal"],
        fontSize=7,
        alignment=1,
        fontName="Helvetica",
        textColor=colors.black,
        leading=8,
    )

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
    )
    elements = []

    # Cargar imágenes
    imagen1 = "img/logo1.jpeg"
    imagen2 = "img/logo3.jpeg"

    # --- Encabezado y Pie de Página ---
    def header_footer(canvas, doc):
        canvas.saveState()
        # Solo mostrar encabezado en la primera página
        if doc.page == 1:
            # Logos
            canvas.drawImage(
                imagen1,
                doc.leftMargin - 20,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawImage(
                imagen2,
                doc.width + doc.leftMargin - 60,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Pie de página (en todas las páginas)
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, f"Página {doc.page}")
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            30,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    # Encabezado UNEFA serio
    elements.append(
        Paragraph("UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA", unefa_title_style)
    )
    elements.append(
        Paragraph("DE LA FUERZA ARMADA NACIONAL BOLIVARIANA", unefa_title_style)
    )
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("NÚCLEO CARABOBO - PUERTO CABELLO", header_info_style))
    elements.append(Paragraph("PERÍODO ACADÉMICO 1-2025", header_info_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("COMPROBANTE DE INSCRIPCIÓN", doc_title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"CÉDULA DE IDENTIDAD: V-{cedula}", student_info_style))
    elements.append(
        Paragraph(
            f"ESTUDIANTE: {nombre.upper()} {apellido.upper()}", student_info_style
        )
    )
    elements.append(Paragraph(f"CARRERA: {carrera}", student_info_style))

    codigo_documento = str(uuid.uuid4()).replace("-", "").upper()[:12]
    elements.append(
        Paragraph(f"CÓDIGO DE VERIFICACIÓN: {codigo_documento}", student_info_style)
    )
    elements.append(Spacer(1, 15))

    # Tabla de materias
    data = [["Nº", "CÓDIGO", "ASIGNATURA", "UC", "SECCIÓN", "DOCENTE"]]
    total_creditos = 0
    for idx, materia in enumerate(materias, start=1):
        codigo, nombre_materia, creditos, numero_seccion, profesor = materia
        total_creditos += int(creditos)
        seccion_formato = f"D{numero_seccion}"
        data.append(
            [
                f"{idx:02d}",
                codigo,
                nombre_materia.upper(),
                str(creditos),
                seccion_formato,
                profesor.upper(),
            ]
        )
    materias_table = Table(
        data,
        colWidths=[
            0.4 * inch,
            1 * inch,
            3.2 * inch,
            0.4 * inch,
            0.8 * inch,
            2.2 * inch,
        ],
    )
    materias_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (5, 1), (5, -1), "CENTER"),  # Docente
                ("ALIGN", (4, 1), (4, -1), "CENTER"),  # Sección
                ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Código
                ("ALIGN", (1, 1), (1, -1), "CENTER"),  # Nombre
                ("ALIGN", (2, 1), (2, -1), "LEFT"),  # Créditos
                ("ALIGN", (3, 1), (3, -1), "CENTER"),  # Requisitos
            ]
        )
    )
    elements.append(materias_table)
    elements.append(Spacer(1, 12))
    elements.append(
        Paragraph(
            f"TOTAL DE MATERIAS: {len(materias)} | TOTAL DE CRÉDITOS: {total_creditos} UC",
            resumen_style,
        )
    )
    elements.append(Spacer(1, 15))
    texto_legal = "La UNEFA, conforme con lo establecido en el artículo 46 del Decreto con rango, valor y fuerza de Ley de Simplificación de trámites Administrativos, debidamente publicado en la Gaceta Oficial de la República Bolivariana de Venezuela Nº 40.549, de fecha 26 de noviembre de 2014, hace constar que el ciudadano mencionado en este documento es estudiante activo para el período académico señalado."
    elements.append(Paragraph(texto_legal, legal_style))
    elements.append(
        Paragraph(
            "Para la autenticación del presente documento consultar: verificacioninscripcion@unefa.edu.ve",
            verificacion_style,
        )
    )
    from datetime import datetime

    fecha_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    elements.append(Paragraph(f"Fecha de emisión: {fecha_actual}", verificacion_style))
    elements.append(Paragraph("Página 1/1", verificacion_style))
    elements.append(Spacer(1, 8))
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)


def generar_reporte_notas_profesor(
    file_path,
    estudiantes_notas,
    nombre_materia,
    display_materia,
    profesor_nombre,
    profesor_apellido,
    seccion_info,
):
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime

    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(letter),
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=1.1 * inch,
        bottomMargin=0.8 * inch,
    )

    elements = []

    # --- Estilos Profesionales ---
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=23,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor("#1e293b"),
        leading=28,
    )
    style_label = ParagraphStyle(
        "Label",
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=2,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=0,
        leading=16,
    )
    style_value = ParagraphStyle(
        "Value",
        fontName="Helvetica",
        fontSize=12,
        alignment=0,
        textColor=colors.black,
        spaceAfter=0,
        leading=16,
    )
    style_table_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=1,
        textColor=colors.white,
    )
    style_cell = ParagraphStyle("Cell", fontName="Helvetica", fontSize=9, alignment=1)
    style_cell_left = ParagraphStyle(
        "CellLeft", fontName="Helvetica", fontSize=9, alignment=0
    )
    style_firma = ParagraphStyle(
        "Firma", fontName="Helvetica-Bold", fontSize=11, alignment=1
    )

    # --- Encabezado y Pie de Página ---
    def header_footer(canvas, doc):
        canvas.saveState()
        # Solo mostrar encabezado en la primera página
        if doc.page == 1:
            # Encabezado institucional grande
            canvas.setFont("Helvetica-Bold", 13)
            canvas.drawCentredString(415, 555, "REPÚBLICA BOLIVARIANA DE VENEZUELA")
            canvas.drawCentredString(
                415, 537, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
            )
            canvas.drawCentredString(
                415, 519, "UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA"
            )
            canvas.drawCentredString(
                415, 501, "DE LA FUERZA ARMADA NACIONAL BOLIVARIANA"
            )
            canvas.drawCentredString(415, 483, "NÚCLEO CARABOBO - SEDE PUERTO CABELLO")
            # Logos grandes y alineados
            canvas.drawImage(
                imagen1,
                doc.leftMargin - 20,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawImage(
                imagen2,
                doc.width + doc.leftMargin - 60,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Pie de página
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, f"Página {doc.page}")
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            30,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    # --- Título ---
    elements.append(Spacer(1, 70))
    elements.append(Paragraph("PLANILLA DE REGISTRO DE CALIFICACIONES", style_title))
    elements.append(Spacer(1, 30))

    # --- Datos de la materia y docente en una sola fila, centrados ---
    seccion = f"D{seccion_info.get('numero_seccion', '')}"
    periodo = seccion_info.get("periodo", "")

    datos_table = Table(
        [
            [
                Paragraph("<b>MATERIA:</b>", style_label),
                Paragraph(nombre_materia.upper(), style_value),
                Paragraph("<b>DOCENTE:</b>", style_label),
                Paragraph(
                    f"{profesor_nombre.upper()} {profesor_apellido.upper()}",
                    style_value,
                ),
                Paragraph("<b>SECCIÓN:</b>", style_label),
                Paragraph(seccion, style_value),
                Paragraph("<b>PERÍODO:</b>", style_label),
                Paragraph(periodo, style_value),
            ]
        ],
        colWidths=[
            1.2 * inch,
            2.2 * inch,
            1.1 * inch,
            2.2 * inch,
            1.1 * inch,
            0.8 * inch,
            1.1 * inch,
            1.1 * inch,
        ],
        hAlign="CENTER",
        style=[
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ],
    )
    elements.append(datos_table)
    elements.append(Spacer(1, 22))

    # --- Tabla de Calificaciones (columnas de cortes más anchas y ordenadas) ---
    headers = [
        "Nº",
        "C.I.",
        "APELLIDOS Y NOMBRES",
        "Corte 1",
        "Firma",
        "Corte 2",
        "Firma",
        "Corte 3",
        "Firma",
        "Corte 4",
        "Firma",
        "Def.",
        "Firma",
    ]
    data = [[Paragraph(h, style_table_header) for h in headers]]

    for idx, est in enumerate(estudiantes_notas, 1):
        full_name = (
            f"{est.get('apellidos', '').upper()}, {est.get('nombres', '').upper()}"
        )
        data.append(
            [
                Paragraph(str(idx), style_cell),
                Paragraph(f"V-{est.get('ci', '')}", style_cell),
                Paragraph(full_name, style_cell_left),
                Paragraph(str(est.get("corte1", "0")), style_cell),
                Paragraph("", style_cell),
                Paragraph(str(est.get("corte2", "0")), style_cell),
                Paragraph("", style_cell),
                Paragraph(str(est.get("corte3", "0")), style_cell),
                Paragraph("", style_cell),
                Paragraph(str(est.get("corte4", "0")), style_cell),
                Paragraph("", style_cell),
                Paragraph(f"<b>{est.get('nota_def', '0')}</b>", style_cell),
                Paragraph("", style_cell),
            ]
        )

    # Columnas de cortes más anchas y tabla centrada
    col_widths = [
        0.38 * inch,  # Nº
        0.95 * inch,  # C.I.
        2.3 * inch,  # Apellidos y Nombres
        0.78 * inch,  # Corte 1
        0.65 * inch,  # Firma 1
        0.78 * inch,  # Corte 2
        0.65 * inch,  # Firma 2
        0.78 * inch,  # Corte 3
        0.65 * inch,  # Firma 3
        0.78 * inch,  # Corte 4
        0.65 * inch,  # Firma 4
        0.7 * inch,  # Def.
        0.65 * inch,  # Firma Def.
    ]

    table = Table(data, colWidths=col_widths, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#1e293b")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (2, -1), "LEFT"),
                ("LEFTPADDING", (2, 1), (2, -1), 6),
                ("BACKGROUND", (4, 1), (4, -1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (6, 1), (6, -1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (8, 1), (8, -1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (10, 1), (10, -1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (12, 1), (12, -1), colors.HexColor("#f1f5f9")),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 45))

    # Firma del Docente
    firma_data = [
        [None, Paragraph("_" * 32, style_firma), None],
        [None, Paragraph("Firma del Docente", style_firma), None],
    ]
    firma_table = Table(firma_data, colWidths=[3.5 * inch, 3 * inch, 3.5 * inch])
    elements.append(firma_table)

    # --- Construir PDF ---
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    os.startfile(file_path)


def generate_record_academico_report(
    file_path, student_data, academic_records, usuario
):
    """
    Genera un reporte de record académico completo para un estudiante.

    Args:
        file_path: Ruta donde guardar el PDF
        student_data: Diccionario con datos del estudiante (cedula, nombre, apellido, carrera, semestre)
        academic_records: Lista de tuplas con registros académicos (codigo, materia, creditos, periodo, nota_def, estado)
        usuario: Usuario que genera el reporte
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=1.1 * inch,
        bottomMargin=0.8 * inch,
    )

    elements = []

    # --- Estilos Profesionales ---
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=20,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor("#1e293b"),
        leading=24,
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=1,
        spaceAfter=15,
        textColor=colors.HexColor("#1e293b"),
        leading=16,
    )
    style_label = ParagraphStyle(
        "Label",
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=2,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=0,
        leading=13,
    )
    style_value = ParagraphStyle(
        "Value",
        fontName="Helvetica",
        fontSize=11,
        alignment=0,
        textColor=colors.black,
        spaceAfter=0,
        leading=13,
    )
    style_table_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=1,
        textColor=colors.white,
    )
    style_cell = ParagraphStyle("Cell", fontName="Helvetica", fontSize=9, alignment=1)
    style_cell_left = ParagraphStyle(
        "CellLeft", fontName="Helvetica", fontSize=9, alignment=0
    )
    style_summary = ParagraphStyle(
        "Summary",
        fontName="Helvetica-Bold",
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10,
    )

    # --- Encabezado y Pie de Página ---
    def header_footer(canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            # Encabezado institucional
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawCentredString(300, 730, "REPÚBLICA BOLIVARIANA DE VENEZUELA")
            canvas.drawCentredString(
                300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
            )
            canvas.drawCentredString(
                300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA"
            )
            canvas.drawCentredString(
                300, 685, "DE LA FUERZA ARMADA NACIONAL BOLIVARIANA"
            )
            canvas.drawCentredString(300, 670, "NÚCLEO CARABOBO - SEDE PUERTO CABELLO")

            # Logos
            canvas.drawImage(
                imagen1,
                doc.leftMargin - 20,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawImage(
                imagen2,
                doc.width + doc.leftMargin - 60,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Pie de página (en todas las páginas)
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, f"Página {doc.page}")
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            30,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    # --- Título Principal ---
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("RECORD ACADÉMICO", style_title))
    elements.append(Spacer(1, 20))

    # --- Información del Estudiante ---
    student_info_data = [
        [
            Paragraph("<b>CÉDULA:</b>", style_label),
            Paragraph(f"V-{student_data['cedula']}", style_value),
            Paragraph("<b>ESTUDIANTE:</b>", style_label),
            Paragraph(
                f"{student_data['nombre'].upper()} {student_data['apellido'].upper()}",
                style_value,
            ),
        ],
        [
            Paragraph("<b>CARRERA:</b>", style_label),
            Paragraph(student_data["carrera"], style_value),
            Paragraph("<b>SEMESTRE ACTUAL:</b>", style_label),
            Paragraph(str(student_data["semestre"]), style_value),
        ],
    ]

    student_info_table = Table(
        student_info_data,
        colWidths=[1.2 * inch, 2.8 * inch, 1.5 * inch, 1.5 * inch],
        hAlign="CENTER",
        style=[
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e293b")),
        ],
    )
    elements.append(student_info_table)
    elements.append(Spacer(1, 25))

    # --- Información del Reporte ---
    report_info_data = [
        [
            Paragraph("<b>FECHA DE EMISIÓN:</b>", style_label),
            Paragraph(datetime.now().strftime("%d/%m/%Y"), style_value),
            Paragraph("<b>USUARIO:</b>", style_label),
            Paragraph(usuario, style_value),
        ],
    ]

    report_info_table = Table(
        report_info_data,
        colWidths=[1.5 * inch, 1.5 * inch, 1.2 * inch, 2.8 * inch],
        hAlign="CENTER",
        style=[
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e293b")),
        ],
    )
    elements.append(report_info_table)
    elements.append(Spacer(1, 25))

    # --- Tabla de Registros Académicos ---
    if academic_records:
        elements.append(Paragraph("HISTORIAL ACADÉMICO", style_subtitle))
        elements.append(Spacer(1, 10))

        # Headers de la tabla
        headers = [
            "Nº",
            "CÓDIGO",
            "ASIGNATURA",
            "UC",
            "PERÍODO",
            "NOTA",
            "ESTADO",
        ]
        data = [[Paragraph(h, style_table_header) for h in headers]]

        # Datos de las materias
        total_creditos = 0
        materias_aprobadas = 0
        materias_reprobadas = 0
        promedio_general = 0
        suma_notas = 0
        materias_con_nota = 0

        for idx, record in enumerate(academic_records, 1):
            codigo, materia, creditos, periodo, nota_def, estado = record

            # Calcular estadísticas
            total_creditos += int(creditos)
            if estado == "APROBÓ":
                materias_aprobadas += 1
            elif estado == "REPROBÓ":
                materias_reprobadas += 1

            if nota_def is not None:
                suma_notas += float(nota_def)
                materias_con_nota += 1

            # Formatear nota
            nota_str = f"{nota_def:.2f}" if nota_def is not None else "-"

            data.append(
                [
                    Paragraph(str(idx), style_cell),
                    Paragraph(codigo, style_cell),
                    Paragraph(materia.upper(), style_cell_left),
                    Paragraph(str(creditos), style_cell),
                    Paragraph(periodo, style_cell),
                    Paragraph(nota_str, style_cell),
                    Paragraph(estado if estado else "-", style_cell),
                ]
            )

        # Calcular promedio general
        promedio_general = (
            suma_notas / materias_con_nota if materias_con_nota > 0 else 0
        )

        # Crear tabla
        col_widths = [
            0.4 * inch,  # Nº
            1.0 * inch,  # CÓDIGO
            2.5 * inch,  # ASIGNATURA
            0.5 * inch,  # UC
            1.0 * inch,  # PERÍODO
            0.6 * inch,  # NOTA
            0.8 * inch,  # ESTADO
        ]

        table = Table(data, colWidths=col_widths, hAlign="CENTER")
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#1e293b")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),
                    ("ALIGN", (2, 1), (2, -1), "LEFT"),
                    ("LEFTPADDING", (2, 1), (2, -1), 6),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 25))

        # --- Resumen Académico ---
        elements.append(Paragraph("RESUMEN ACADÉMICO", style_subtitle))
        elements.append(Spacer(1, 15))

        # Tabla de resumen
        summary_data = [
            [
                Paragraph("<b>Total de Materias Cursadas:</b>", style_label),
                Paragraph(str(len(academic_records)), style_value),
                Paragraph("<b>Total de Créditos:</b>", style_label),
                Paragraph(str(total_creditos), style_value),
            ],
            [
                Paragraph("<b>Materias Aprobadas:</b>", style_label),
                Paragraph(str(materias_aprobadas), style_value),
                Paragraph("<b>Materias Reprobadas:</b>", style_label),
                Paragraph(str(materias_reprobadas), style_value),
            ],
            [
                Paragraph("<b>Promedio General:</b>", style_label),
                Paragraph(f"{promedio_general:.2f}", style_value),
                Paragraph("<b>Porcentaje de Aprobación:</b>", style_label),
                Paragraph(
                    (
                        f"{(materias_aprobadas / len(academic_records) * 100):.1f}%"
                        if len(academic_records) > 0
                        else "0%"
                    ),
                    style_value,
                ),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[2.0 * inch, 1.0 * inch, 2.0 * inch, 1.0 * inch],
            hAlign="CENTER",
            style=[
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#041825")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ],
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 30))

        # --- Leyenda de Estados ---
        legend_data = [
            [
                Paragraph("<b>LEYENDA:</b>", style_label),
                Paragraph("APROBÓ: Nota ≥ 10 puntos", style_value),
                Paragraph("REPROBÓ: Nota < 10 puntos", style_value),
            ],
        ]

        legend_table = Table(
            legend_data,
            colWidths=[1.0 * inch, 2.0 * inch, 2.0 * inch],
            hAlign="CENTER",
            style=[
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e293b")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ],
        )
        elements.append(legend_table)

    else:
        # Si no hay registros académicos
        elements.append(Paragraph("HISTORIAL ACADÉMICO", style_subtitle))
        elements.append(Spacer(1, 20))
        elements.append(
            Paragraph(
                "El estudiante no tiene registros académicos disponibles.",
                ParagraphStyle(
                    "NoData",
                    fontName="Helvetica",
                    fontSize=12,
                    alignment=1,
                    textColor=colors.grey,
                ),
            )
        )

    # --- Construir PDF ---
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    os.startfile(file_path)


def generate_constancia_estudio_report(file_path, student_data, usuario):
    """
    Genera una constancia de estudio para un estudiante.

    Args:
        file_path: Ruta donde guardar el PDF
        student_data: Diccionario con datos del estudiante (cedula, nombre, apellido, carrera, semestre)
        usuario: Usuario que genera el reporte
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=1.1 * inch,
        bottomMargin=0.8 * inch,
    )

    elements = []

    # --- Estilos Profesionales ---
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor("#1e293b"),
        leading=22,
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=1,
        spaceAfter=15,
        textColor=colors.HexColor("#1e293b"),
        leading=16,
    )
    style_label = ParagraphStyle(
        "Label",
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=2,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=0,
        leading=13,
    )
    style_value = ParagraphStyle(
        "Value",
        fontName="Helvetica",
        fontSize=11,
        alignment=0,
        textColor=colors.black,
        spaceAfter=0,
        leading=13,
    )
    style_legal = ParagraphStyle(
        "Legal",
        fontName="Helvetica",
        fontSize=10,
        alignment=4,  # Justified
        textColor=colors.black,
        spaceAfter=12,
        leading=14,
    )
    style_signature = ParagraphStyle(
        "Signature",
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=1,
        textColor=colors.black,
        spaceAfter=5,
    )

    # --- Encabezado y Pie de Página ---
    def header_footer(canvas, doc):
        canvas.saveState()
        # Solo mostrar encabezado en la primera página
        if doc.page == 1:
            # Encabezado institucional
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawCentredString(300, 730, "REPÚBLICA BOLIVARIANA DE VENEZUELA")
            canvas.drawCentredString(
                300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
            )
            canvas.drawCentredString(
                300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA"
            )
            canvas.drawCentredString(
                300, 685, "DE LA FUERZA ARMADA NACIONAL BOLIVARIANA"
            )
            canvas.drawCentredString(300, 670, "NÚCLEO CARABOBO - SEDE PUERTO CABELLO")

            # Logos
            canvas.drawImage(
                imagen1,
                doc.leftMargin - 20,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawImage(
                imagen2,
                doc.width + doc.leftMargin - 60,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Pie de página
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, f"Página {doc.page}")
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            30,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    # --- Título Principal ---
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("CONSTANCIA DE ESTUDIO", style_title))
    elements.append(Spacer(1, 30))

    # --- Información del Estudiante ---
    student_info_data = [
        [
            Paragraph("<b>CÉDULA DE IDENTIDAD:</b>", style_label),
            Paragraph(f"V-{student_data['cedula']}", style_value),
        ],
        [
            Paragraph("<b>NOMBRES Y APELLIDOS:</b>", style_label),
            Paragraph(
                f"{student_data['nombre'].upper()} {student_data['apellido'].upper()}",
                style_value,
            ),
        ],
        [
            Paragraph("<b>CARRERA:</b>", style_label),
            Paragraph(student_data["carrera"], style_value),
        ],
        [
            Paragraph("<b>SEMESTRE ACTUAL:</b>", style_label),
            Paragraph(str(student_data["semestre"]), style_value),
        ],
    ]

    student_info_table = Table(
        student_info_data,
        colWidths=[2.5 * inch, 4.5 * inch],
        hAlign="LEFT",
        style=[
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ],
    )
    elements.append(student_info_table)
    elements.append(Spacer(1, 30))

    # --- Texto de la Constancia ---
    constancia_text = f"""
    Por medio de la presente se hace constar que el ciudadano <b>V-{student_data['cedula']}</b>, 
    <b>{student_data['nombre'].upper()} {student_data['apellido'].upper()}</b>, es estudiante activo de esta 
    casa de estudios, cursando actualmente el <b>{student_data['semestre']}° semestre</b> de la carrera 
    <b>{student_data['carrera']}</b>.
    """

    elements.append(Paragraph(constancia_text, style_legal))
    elements.append(Spacer(1, 20))

    # --- Texto Legal Adicional ---
    # Mapeo de meses en español
    meses_espanol = {
        "January": "ENERO",
        "February": "FEBRERO",
        "March": "MARZO",
        "April": "ABRIL",
        "May": "MAYO",
        "June": "JUNIO",
        "July": "JULIO",
        "August": "AGOSTO",
        "September": "SEPTIEMBRE",
        "October": "OCTUBRE",
        "November": "NOVIEMBRE",
        "December": "DICIEMBRE",
    }

    mes_ingles = datetime.now().strftime("%B")
    mes_espanol = meses_espanol.get(mes_ingles, mes_ingles.upper())

    legal_text = """
    Esta constancia se expide a solicitud del interesado, para los fines que estime conveniente, 
    en la ciudad de Puerto Cabello, Estado Carabobo, República Bolivariana de Venezuela, 
    a los <b>{}</b> días del mes de <b>{}</b> del año <b>{}</b>.
    """.format(
        datetime.now().strftime("%d"), mes_espanol, datetime.now().strftime("%Y")
    )

    elements.append(Paragraph(legal_text, style_legal))
    elements.append(Spacer(1, 40))

    # --- Espacio para Firma ---
    signature_data = [
        [None, Paragraph("_" * 32, style_signature), None],
        [None, Paragraph("Firma y Sello", style_signature), None],
        [None, Paragraph("Autoridad Universitaria", style_signature), None],
    ]

    signature_table = Table(
        signature_data,
        colWidths=[2.5 * inch, 3 * inch, 2.5 * inch],
        hAlign="CENTER",
    )
    elements.append(signature_table)

    # --- Construir PDF ---
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    os.startfile(file_path)


def generate_students_by_semester_report(
    file_path, students_by_semester, carrera, usuario
):
    """
    Genera un reporte de estudiantes agrupados por semestre, filtrado por carrera.

    Args:
        file_path: Ruta donde guardar el PDF
        students_by_semester: Diccionario con semestres como claves y listas de estudiantes como valores
        carrera: Nombre de la carrera del coordinador
        usuario: Usuario que genera el reporte
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime
    import os

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    elements = []

    # Cargar imágenes
    imagen1 = "img/logo1.jpeg"
    imagen2 = "img/logo3.jpeg"

    # Estilos
    style_title = ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=16,
        alignment=1,
        spaceAfter=8,
        textColor=colors.HexColor("#1e293b"),
        leading=22,
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=1,
        spaceAfter=15,
        textColor=colors.HexColor("#1e293b"),
        leading=16,
    )
    style_table_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=1,
        textColor=colors.white,
    )
    style_cell = ParagraphStyle(
        "Cell",
        fontName="Helvetica",
        fontSize=9,
        alignment=1,
        textColor=colors.black,
        spaceAfter=0,
        leading=11,
    )
    style_cell_left = ParagraphStyle(
        "CellLeft",
        fontName="Helvetica",
        fontSize=9,
        alignment=0,
        textColor=colors.black,
        spaceAfter=0,
        leading=11,
    )

    # --- Encabezado y Pie de Página ---
    def header_footer(canvas, doc):
        canvas.saveState()
        # Solo mostrar encabezado en la primera página
        if doc.page == 1:
            # Encabezado institucional
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawCentredString(300, 730, "REPÚBLICA BOLIVARIANA DE VENEZUELA")
            canvas.drawCentredString(
                300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
            )
            canvas.drawCentredString(
                300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA"
            )
            canvas.drawCentredString(
                300, 685, "DE LA FUERZA ARMADA NACIONAL BOLIVARIANA"
            )
            canvas.drawCentredString(
                300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA"
            )
            canvas.drawCentredString(
                300, 685, "DE LA FUERZA ARMADA NACIONAL BOLIVARIANA"
            )
            canvas.drawCentredString(300, 670, "NÚCLEO CARABOBO - SEDE PUERTO CABELLO")

            # Logos
            canvas.drawImage(
                imagen1,
                doc.leftMargin - 20,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawImage(
                imagen2,
                doc.width + doc.leftMargin - 60,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Pie de página (en todas las páginas)
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, f"Página {doc.page}")
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            30,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    # --- Título Principal ---
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("REPORTE DE ESTUDIANTES POR SEMESTRE", style_title))
    elements.append(Paragraph(f"CARRERA: {carrera.upper()}", style_subtitle))
    elements.append(Spacer(1, 20))

    # --- Tablas por Semestre ---
    for semestre in sorted(students_by_semester.keys()):
        estudiantes = students_by_semester[semestre]

        # Título del semestre
        elements.append(
            Paragraph(
                f"{semestre}° SEMESTRE - {len(estudiantes)} ESTUDIANTES", style_subtitle
            )
        )
        elements.append(Spacer(1, 10))

        if estudiantes:
            # Headers de la tabla
            headers = [
                "Nº",
                "CÉDULA",
                "NOMBRES Y APELLIDOS",
                "CARRERA",
                "SEMESTRE",
            ]
            data = [[Paragraph(h, style_table_header) for h in headers]]

            # Datos de los estudiantes
            for idx, estudiante in enumerate(estudiantes, 1):
                data.append(
                    [
                        Paragraph(str(idx), style_cell),
                        Paragraph(f"V-{estudiante['cedula']}", style_cell),
                        Paragraph(
                            f"{estudiante['nombre'].upper()} {estudiante['apellido'].upper()}",
                            style_cell_left,
                        ),
                        Paragraph(estudiante["carrera"], style_cell),
                        Paragraph(str(estudiante["semestre"]), style_cell),
                    ]
                )

            # Crear tabla
            col_widths = [
                0.4 * inch,  # Nº
                1.0 * inch,  # CÉDULA
                3.0 * inch,  # NOMBRES Y APELLIDOS
                1.5 * inch,  # CARRERA
                1.0 * inch,  # SEMESTRE
            ]

            table = Table(data, colWidths=col_widths, hAlign="CENTER")
            table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#1e293b")),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("ALIGN", (0, 1), (0, -1), "CENTER"),
                        ("ALIGN", (2, 1), (2, -1), "LEFT"),
                        ("LEFTPADDING", (2, 1), (2, -1), 6),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            elements.append(table)
        else:
            # Si no hay estudiantes en este semestre
            elements.append(
                Paragraph(
                    "No hay estudiantes registrados en este semestre.",
                    ParagraphStyle(
                        "NoData",
                        fontName="Helvetica",
                        fontSize=10,
                        alignment=1,
                        textColor=colors.grey,
                    ),
                )
            )

        elements.append(Spacer(1, 20))

    # --- Construir PDF ---
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    os.startfile(file_path)


def generate_professors_by_courses_report(
    file_path, professors_by_courses, carrera, usuario
):
    """
    Genera un reporte de profesores agrupados por materias, filtrado por carrera.

    Args:
        file_path: Ruta donde guardar el PDF
        professors_by_courses: Diccionario con materias como claves y listas de profesores como valores
        carrera: Nombre de la carrera del coordinador
        usuario: Usuario que genera el reporte
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime
    import os

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    elements = []

    # Cargar imágenes
    imagen1 = "img/logo1.jpeg"
    imagen2 = "img/logo3.jpeg"

    # Estilos
    style_title = ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=16,
        alignment=1,
        spaceAfter=8,
        textColor=colors.HexColor("#1e293b"),
        leading=22,
    )
    style_subtitle = ParagraphStyle(
        "Subtitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        alignment=1,
        spaceAfter=15,
        textColor=colors.HexColor("#1e293b"),
        leading=16,
    )
    style_table_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=1,
        textColor=colors.white,
    )
    style_cell = ParagraphStyle(
        "Cell",
        fontName="Helvetica",
        fontSize=9,
        alignment=1,
        textColor=colors.black,
        spaceAfter=0,
        leading=11,
    )
    style_cell_left = ParagraphStyle(
        "CellLeft",
        fontName="Helvetica",
        fontSize=9,
        alignment=0,
        textColor=colors.black,
        spaceAfter=0,
        leading=11,
    )

    # --- Encabezado y Pie de Página ---
    def header_footer(canvas, doc):
        canvas.saveState()
        # Solo mostrar encabezado en la primera página
        if doc.page == 1:
            # Encabezado institucional
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawCentredString(300, 730, "REPÚBLICA BOLIVARIANA DE VENEZUELA")
            canvas.drawCentredString(
                300, 715, "MINISTERIO DEL PODER POPULAR PARA LA DEFENSA"
            )
            canvas.drawCentredString(
                300, 700, "UNIVERSIDAD NACIONAL EXPERIMENTAL POLITÉCNICA"
            )
            canvas.drawCentredString(
                300, 685, "DE LA FUERZA ARMADA NACIONAL BOLIVARIANA"
            )
            canvas.drawCentredString(300, 670, "NÚCLEO CARABOBO - SEDE PUERTO CABELLO")

            # Logos
            canvas.drawImage(
                imagen1,
                doc.leftMargin - 20,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas.drawImage(
                imagen2,
                doc.width + doc.leftMargin - 60,
                680,
                width=80,
                height=80,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Pie de página (en todas las páginas)
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc.leftMargin, 30, f"Página {doc.page}")
        canvas.drawRightString(
            doc.width + doc.leftMargin,
            30,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    # --- Título Principal ---
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("REPORTE DE PROFESORES Y SUS MATERIAS", style_title))
    elements.append(Paragraph(f"CARRERA: {carrera.upper()}", style_subtitle))
    elements.append(Spacer(1, 20))

    # --- Tabla de Profesores y Materias ---
    if professors_by_courses:
        # Headers de la tabla
        headers = [
            "Nº",
            "CÉDULA",
            "NOMBRES Y APELLIDOS",
            "MATERIA",
            "SECCIÓN",
            "CARRERA",
            "FECHA CONTRATACIÓN",
        ]
        data = [[Paragraph(h, style_table_header) for h in headers]]

        # Datos de los profesores
        idx = 1
        for materia, profesores in sorted(professors_by_courses.items()):
            for profesor in profesores:
                numero_seccion = (
                    profesor.get("numero_seccion")
                    or profesor.get("seccion_materias")
                    or ""
                )
                seccion = f"D{numero_seccion}" if numero_seccion else "-"
                data.append(
                    [
                        Paragraph(str(idx), style_cell),
                        Paragraph(f"V-{profesor['cedula']}", style_cell),
                        Paragraph(
                            f"{profesor['nombre'].upper()} {profesor['apellido'].upper()}",
                            style_cell,
                        ),
                        Paragraph(materia.upper(), style_cell),
                        Paragraph(seccion, style_cell),
                        Paragraph(profesor["carrera"], style_cell),
                        Paragraph(profesor["fecha_contratacion"], style_cell),
                    ]
                )
                idx += 1

        # Crear tabla
        col_widths = [
            0.4 * inch,  # Nº
            0.9 * inch,  # CÉDULA
            2.5 * inch,  # NOMBRES Y APELLIDOS
            1.5 * inch,  # MATERIA
            0.7 * inch,  # SECCIÓN
            1.1 * inch,  # CARRERA
            1.1 * inch,  # FECHA CONTRATACIÓN
        ]

        table = Table(data, colWidths=col_widths, hAlign="CENTER")
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#1e293b")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),
                    ("ALIGN", (2, 1), (2, -1), "LEFT"),
                    ("LEFTPADDING", (2, 1), (2, -1), 6),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        elements.append(table)
    else:
        # Si no hay profesores
        elements.append(
            Paragraph(
                "No hay profesores asignados a materias en esta carrera.",
                ParagraphStyle(
                    "NoData",
                    fontName="Helvetica",
                    fontSize=10,
                    alignment=1,
                    textColor=colors.grey,
                ),
            )
        )

    # --- Construir PDF ---
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    os.startfile(file_path)
