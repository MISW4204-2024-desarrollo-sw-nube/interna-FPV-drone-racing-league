# Internal-FPV-drone-racing-league
Desarrollo de software en la nube - 2024 - 12

# Instrucciones
1. Clonar el repositorio de acuerdo al metodo de su preferencia (HTTP, SSH).
2. Para desplegar la aplicación, deber abrir una terminal y ubicarse en la raiz del proyecto
3. A continuación debera ejecutar el siguiente comando: docker compose up --build. Este comando instanciara nuevamente cada imagen y generarà los contenedores asociados.
4. En caso de obtener el siguiente error: psycopg2.errors.UndefinedTable debera realizar los siguientes pasos:

   4.1 Debe eliminar la carpeta ifpvdl que se encuentra en la carpeta postgres-db en la raiz del proyecto.
   
   4.2 Debe eliminar todos los volúmenes creados anteriormente. Para ello debe ejectuar en la terminal: docker-compose down -v
   
   4.3 Debe ejecutar nuevamente docker compose up --build


### Integrantes
Andres Felipe Lozada Luna (af.losada@uniandes.edu.co) 

Cristian Pinzon Hernández (cc.pinzonh1@uniandes.edu.co)

Juan Carlos De Jesus (j.dejesus@uniandes.edu.co)

Santiago Alvarez (s.alvarez112@uniandes.edu.co)
