@echo off
REM Fix para el error de encoding de psycopg2 en Windows
REM Deshabilita la lectura de archivos de configuración de PostgreSQL

SET PGPASSFILE=NUL
SET PGSERVICEFILE=NUL
SET PGSYSCONFDIR=NUL
SET LANG=en_US.UTF-8
SET PYTHONIOENCODING=utf-8:replace

REM Ejecuta el programa Python con los argumentos pasados
python %*
