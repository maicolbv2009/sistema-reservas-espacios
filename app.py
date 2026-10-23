
import flet as ft
from datetime import date
from database import obtener_conexion


def main(page: ft.Page):
    page.title = "Sistema de Reservas de Espacios"
    page.window.width = 1000
    page.window.height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    titulo = ft.Text(
        "Sistema de reservas de espacios",
        size=26,
        weight=ft.FontWeight.BOLD,
    )

    descripcion = ft.Text(
        "Administración de Bases de Datos - 4° Medio Técnico Profesional"
    )

    mensaje = ft.Text("Sistema listo para utilizar.", size=16)

    # Campos del formulario
    campo_docente = ft.TextField(
        label="ID del docente",
        hint_text="Ejemplo: 1",
        width=280,
    )

    campo_espacio = ft.TextField(
        label="ID del espacio",
        hint_text="Ejemplo: 1",
        width=280,
    )

    campo_fecha = ft.TextField(
        label="Fecha (AAAA-MM-DD)",
        hint_text="2026-11-10",
        width=280,
    )

    campo_inicio = ft.TextField(
        label="Hora de inicio (HH:MM)",
        hint_text="09:00",
        width=280,
    )

    campo_termino = ft.TextField(
        label="Hora de término (HH:MM)",
        hint_text="10:00",
        width=280,
    )

    campo_reserva = ft.TextField(
        label="ID de la reserva para cancelar",
        hint_text="Consulta el ID en la lista de reservas",
        width=280,
    )

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Datos de la reserva")),
        ],
        rows=[],
    )

    # Consultar reservas
    def consultar_reservas(e=None):
        conexion = None
        cursor = None

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.callproc("listar_reservas")

            filas = []
            for conjunto in cursor.stored_results():
                filas.extend(conjunto.fetchall())

            tabla.rows.clear()

            if filas:
                for fila in filas:
                    tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text(
                                        " | ".join(str(dato) for dato in fila)
                                    )
                                )
                            ]
                        )
                    )

                mensaje.value = f"Reservas encontradas: {len(filas)}"
            else:
                mensaje.value = "No se encontraron reservas."

        except Exception as error:
            mensaje.value = f"Error al consultar reservas: {error}"

        finally:
            if cursor is not None:
                cursor.close()

            if conexion is not None and conexion.is_connected():
                conexion.close()

            page.update()

    # Crear una reserva
    def crear_reserva(e):
        conexion = None
        cursor = None

        try:
            if not all([
                campo_docente.value,
                campo_espacio.value,
                campo_fecha.value,
                campo_inicio.value,
                campo_termino.value,
            ]):
                mensaje.value = "Completa todos los campos de la reserva."
                page.update()
                return

            id_docente = int(campo_docente.value)
            id_espacio = int(campo_espacio.value)
            fecha_reserva = date.fromisoformat(
                campo_fecha.value.strip()
            )
            hora_inicio = campo_inicio.value.strip()
            hora_termino = campo_termino.value.strip()

            if hora_termino <= hora_inicio:
                mensaje.value = (
                    "La hora de término debe ser posterior al inicio."
                )
                page.update()
                return

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.callproc(
                "crear_reserva",
                [
                    id_docente,
                    id_espacio,
                    fecha_reserva,
                    hora_inicio,
                    hora_termino,
                ],
            )

            conexion.commit()
            mensaje.value = "Reserva creada correctamente."

            consultar_reservas()

        except Exception as error:
            if conexion is not None:
                conexion.rollback()

            mensaje.value = f"No se pudo crear la reserva: {error}"

        finally:
            if cursor is not None:
                cursor.close()

            if conexion is not None and conexion.is_connected():
                conexion.close()

    # Comprobar disponibilidad
    def comprobar_disponibilidad(e):
        conexion = None
        cursor = None

        try:
            if not all([
                campo_espacio.value,
                campo_fecha.value,
                campo_inicio.value,
                campo_termino.value,
            ]):
                mensaje.value = (
                    "Completa el ID del espacio, la fecha y las horas."
                )
                page.update()
                return

            id_espacio = int(campo_espacio.value)
            fecha_reserva = date.fromisoformat(
                campo_fecha.value.strip()
            )
            hora_inicio = campo_inicio.value.strip()
            hora_termino = campo_termino.value.strip()

            if hora_termino <= hora_inicio:
                mensaje.value = (
                    "La hora de término debe ser posterior al inicio."
                )
                page.update()
                return

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.callproc(
                "comprobar_disponibilidad",
                [
                    id_espacio,
                    fecha_reserva,
                    hora_inicio,
                    hora_termino,
                ],
            )

            encontrado = False

            for conjunto in cursor.stored_results():
                for fila in conjunto.fetchall():
                    mensaje.value = f"Disponibilidad: {fila[-1]}"
                    encontrado = True

            if not encontrado:
                mensaje.value = (
                    "El procedimiento no devolvió información."
                )

        except Exception as error:
            mensaje.value = (
                f"Error al comprobar disponibilidad: {error}"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexion is not None and conexion.is_connected():
                conexion.close()

            page.update()

    # Cancelar una reserva
    def cancelar_reserva(e):
        conexion = None
        cursor = None

        try:
            if not campo_reserva.value:
                mensaje.value = "Ingresa el ID de la reserva."
                page.update()
                return

            id_reserva = int(campo_reserva.value)

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.callproc(
                "cancelar_reserva",
                [id_reserva],
            )

            conexion.commit()
            mensaje.value = "Reserva cancelada correctamente."

            campo_reserva.value = ""
            consultar_reservas()

        except Exception as error:
            if conexion is not None:
                conexion.rollback()

            mensaje.value = f"No se pudo cancelar la reserva: {error}"

        finally:
            if cursor is not None:
                cursor.close()

            if conexion is not None and conexion.is_connected():
                conexion.close()

            page.update()

    # Botones
    boton_crear = ft.Button(
        "Crear reserva",
        on_click=crear_reserva,
    )

    boton_disponibilidad = ft.Button(
        "Comprobar disponibilidad",
        on_click=comprobar_disponibilidad,
    )

    boton_consultar = ft.Button(
        "Consultar reservas",
        on_click=consultar_reservas,
    )

    boton_cancelar = ft.Button(
        "Cancelar reserva",
        on_click=cancelar_reserva,
    )

    # Interfaz
    page.add(
        titulo,
        descripcion,
        ft.Divider(),
        ft.Text(
            "Registrar una nueva reserva",
            size=20,
            weight=ft.FontWeight.BOLD,
        ),
        campo_docente,
        campo_espacio,
        campo_fecha,
        campo_inicio,
        campo_termino,
        ft.Row(
            controls=[
                boton_crear,
                boton_disponibilidad,
                boton_consultar,
            ],
            wrap=True,
        ),
        ft.Divider(),
        ft.Text(
            "Cancelar una reserva",
            size=20,
            weight=ft.FontWeight.BOLD,
        ),
        campo_reserva,
        boton_cancelar,
        ft.Divider(),
        mensaje,
        tabla,
    )


ft.run(main)
