# Sistema de reservas de espacios del establecimiento

## Descripción
Este proyecto permite administrar las reservas de espacios del establecimiento educacional, como laboratorios, salas audiovisuales y salas de clases.

## Objetivo
Evitar que dos docentes reserven el mismo espacio en horarios que se superponen.

## Tecnologías utilizadas
- MySQL para almacenar los datos.
- DBeaver para administrar y consultar la base de datos.
- Python para conectar con MySQL.
- Flet para crear la interfaz gráfica.
- Visual Studio Code para desarrollar el proyecto.

## Tablas de la base de datos
- `docentes`: almacena los datos de los docentes.
- `tipos_espacios`: registra los tipos de espacios.
- `espacios`: guarda los espacios disponibles.
- `reservas`: almacena las reservas, sus horarios y sus estados.

## Procedimientos almacenados
- `registrar_docente`: registra docentes.
- `registrar_espacio`: registra espacios.
- `crear_reserva`: crea reservas y evita cruces de horarios.
- `listar_reservas`: consulta las reservas.
- `cancelar_reserva`: cancela una reserva.
- `modificar_reserva`: modifica una reserva.
- `comprobar_disponibilidad`: comprueba si un espacio está disponible.

## Funcionamiento
La aplicación permite crear reservas, consultar su disponibilidad, listar las reservas y cancelar reservas existentes.

## Instalación
1. Instalar Python.
2. Instalar las dependencias con `python -m pip install -r requirements.txt`.
3. Configurar las variables de conexión en el archivo `.env`.
4. Crear las tablas y los procedimientos en MySQL.
5. Ejecutar la aplicación con `python app.py`.

## Seguridad
Las credenciales de conexión se guardan en el archivo `.env`. Este archivo no debe subirse a GitHub.

## Autor
Estudiante de 4° Medio Técnico Profesional.
