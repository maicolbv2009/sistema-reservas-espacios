
from database import obtener_conexion


def listar_reservas():
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.callproc("listar_reservas")

        for resultado in cursor.stored_results():
            filas = resultado.fetchall()

            if not filas:
                print("No hay reservas para mostrar.")
            else:
                for fila in filas:
                    print(fila)

    except Exception as error:
        print("Error al listar reservas:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()


if __name__ == "__main__":
    listar_reservas()
