# Prueba técnica
## Alcance
El objetivo es desarrollar un inventario de licencias de software en tipologías utilizando técnicas de procesamiento de lenguaje natural (NLP) o un modelo de lenguaje grande (LLM), explicando las decisiones tomadas y el paso a paso.

## Requerimientos
- Código
	- Backend
		- Tests
			- [x] Endpoint de listado
			- [x] Endpoint de resumen
			- [ ] Endpoint de actualización
			- [x] Correcta clasificación de licencias
		- [x] Endpoint de listado
		- [x] Endpoint de resumen
		- [x] Endpoint de actualización de licencia
	- Frontend
		- [x] Página para listar licencias (clasificadas)
		- [x] Página para ver resumen por tipología
		- [ ] Componente para edición de tipologías
	- Exportado
		- [x] Exportar clasificaciones en un nuevo archivo Excel
	- [x] Dockerizar

## Desarrollo
En la consigna no queda clara cuál es el uso que se le daría a esta aplicación. Naturalmente, surgen algunas preguntas:
- ¿Cómo se obtiene el Excel? ¿Qué propósito tiene?
  - ¿Los nombres de las aplicaciones serán siempre iguales? ¿Puede pasar que una vez el ID 1 esté asociado a 
  la descripción "Microsoft Word" y otra vez a "MS Word"? ¿Debería considerarse que es la misma aplicación u otra?
  Si debieran considerarse como la misma aplicación, ¿qué identificador debería mostrarse al usuario en el frontend? 
  ¿El usuario conoce los IDs de las aplicaciones? ¿Le interesan?
- Los IDs del Excel, ¿son únicos? ¿De dónde salen?
- ¿Puede aparecer dos veces el mismo ID? ¿Puede cambiar el nombre asociado a un ID?
- ¿Cómo accederían los usuarios a la aplicación? ¿Van a obtener un fichero Excel de otra aplicación o 
se plantea la posibilidad como un mero sustituto de otra acción (como leer datos de una base de datos)?
- ¿Cómo van a interactuar los usuarios con la aplicación? ¿Cómo harán para clasificar las aplicaciones? 
- Hacia el final de la consigna se habla de la posibilidad de que haya diez mil licencias diarias, ¿irían todas en un Excel?
¿Cómo se distribuirían, se harían todas juntas o a lo largo del día? 

Como no era fácil resolver todas estas preguntas, ni había suficiente tiempo para contemplar todas las implicancias
que pudieran desprenderse de sus respuestas. Para la lectura del fichero
opté por lo más sencillo: leer y escribir datos directamente del filesystem. 
En una aplicación real esto sería imposible o indeseable, pero lo consideré suficiente a los propósitos de esta demo.

Tampoco sabía cómo un usuario haría para acceder a los datos contenidos en el Excel. ¿Podría ejecutar un script?
¿Debería crear una página en el front-end para que suba el archivo? Opté por lo más sencillo otra vez: un endpoint
que un usuario autorizado pudiera ejecutar para iniciar el proceso de clasificación.

La celeridad de la sencillez es la respuesta a muchas de los problemas que me fui encontrando y posiblemente también
a bastantes de los problemas que fui introduciendo. Otro caso en el que se verifica esto: la base de datos. Para 
tráficos bajos, sqlite puede funcionar bien, pero podría haber complicaciones conforme aumentara. Una de sus grandes
ventajas, sin embargo, es que en un simplísimo fichero puedo incluir los datos de la aplicación y cualquiera que clone
el repositorio podrá navegar por la web viendo datos lo suficientemente verosímiles.

Aunque el tiempo me pareciera demasiado limitado, me pareció pertinente incluir un módulo en el front-end para mostrar
las aplicaciones de cada categoría. La demora en la que incurrí fue mínima y me permitió hacer un poco más intuitiva la interfaz. 
Así, cuando un usuario vea una categoría en algún lado puede hacer clic sobre ella y ver qué otras aplicaciones son como esa.

### Cómo hacer la clasificación
No hay suficiente tiempo ni suficientes datos como para hacer el fine-tuning de un model pre-entrenado. Por tanto, creo que lo mejor sería construir un prompt con algunos ejemplos representativos de las distintas categorías antes de pedir la clasificación de nuevas licencias. Evidentemente, no se podrán usar todas en el prompt por varias razones: la clasificación tiene que ser extrapolable a softwares que no estén incluidos en la lista inicial y tengo que poder probar de alguna manera que lo que hago funciona como quiero (si todos los softwares a clasificar están en el prompt es imposible que haya un error, no se hace ningúna "predicción").


## Cómo montar la aplicación
1. Clonar repositorio
2. Modificar el .env file y completar la api key de groq a usar:
```
GROQ_API_KEY=xxxx....
```
3. Levantar con docker compose. En la raíz del proyecto, ejecutar:
```shell
docker compose up
```
Esto levantará dos servicios:
- la api en http://localhost:8000/ y
- el front-end, que estará disponible en http://localhost:3000/

La aplicación contará con los datos incluidos en la db de sqlite incluída en el código.

### Cómo categorizar aplicaciones
Las aplicaciones se pueden clasificar (o _re_-clasificar) mediante la api. Para esto, está el endpoint `/applications/classify`. 
Por ejemplo, con la api montada en el puerto por defecto, se podría hacer:
```shell
curl -X POST http://localhost:8000/applications/classify
```

#### Cómo funciona la categorización
1. Del `input.xlsx` se toman las aplicaciones con sus correspondientes IDs
2. Tomando los IDs cómo únicos, se crean en la base de datos aquellas aplicaciones que no estuvieran ya creadas
3. Usando la api de groq, se clasifican todas las aplicaciones de la base de datos que no tengan aún una clasificación
4. Las clasificaciones de las aplicaciones del `input.xlsx` se guardan en un `output.xlsx` donde, además, se incluye la motivación
del agente para escoger la clasificación resultante.

Si se quiere reclasificar todas las aplicaciones en la DB, se puede pasar un query parameter adicional a este endpoint: `force_reclassify`:

```shell
curl -X POST http://localhost:8000/applications/classify\?force_reclassify=true
```

### Uso de los datos iniciales
El Excel (que no es un Excel) lo tomaré como los datos iniciales de una base de datos que habrá que ir completando con las clasificaciones y sus potenciales modificaciones. Esta decisión parte de la presunción de que este sistema podría usarse para llevar un registro de los softwares empleados en una compañnía determinada. Es decir, 
## Q&A
### ¿Cómo escalarías la solución a 10K licencias diarias?
### ¿Cómo versionarías el servicio?
### ¿Qué se podría mejorar con más tiempo?
Muy probablemente: todo. El tiempo estipulado es demasiado escaso para un prototipo que tenga una cantidad razonable de las 
funcionalidades deseadas, dudo de que sirva como una prueba de las habilidades técnicas de un candidato.

De cualquier manera, considero que hay algunos puntos a mejorar que son más urgentes que otros:
- El manejo de errores. Con cómo está planteada la API ahora mismo, es probable que algunos errores
no se controlen correctamente y acarreen más problemas de los debidos.
- De la mano con el punto anterior: la actualización del tipo de las aplicaciones se podría ir haciendo
a medida que se obtienen, en lugar de hacerlas todas al final. En algunos casos la comunicación con la API
de groq podría fallar (o la respuesta ser inválida) y habría que volver a comenzar el proceso desde el principio.
Si sólo son 40 aplicaciones no es muy grave, pero si hubiera más, esto sería absolutamente innecesario.
- El archivo de salida `output.xlsx` tiene un formato muy rudimentario. Se podría establecer un ancho para las columnas,
dar formato a los encabezados y traducirlos, etc.
- De momento, la motivación para las clasificaciones sólo se guardan en el archivo Excel. O sea, que se perderán con cualquier
nueva clasificación que se haga, ya que quedan totalmente excluidas de la base de datos. 
Según el uso que se le quiera dar, sería razonable almacenar también esta información. El modelo para ello 
también podría servir para las actualizaciones de categoría que pudiera realizar un usuario, quien debería aportar,
al momento de actualizar una clasificación, su motivación para hacerlo. Esto permitiría tener una suerte de bitácora
que podría resultar útil.
- Es fundamental añadir logs. De momento, sólo se pueden ver algunos errores por consola, lo que dificultaría
a cualquier usuario entender los problemas con los que podría encontrarse durante el uso de la aplicación y, 
a quien deba mantenerla, solucionarlos. A este propósito, también podría resultar útil tener logs de debug
que pudieran activarse cambiando una variable de entorno, por ejemplo.
- La lectura (y escritura) de los ficheros de Excel debería abstraerse para funcionar en entornos
mas parecidos a los de un entorno productivo real. Podrian enviarse como binarios, almacenarse en una base de datos
o cualquier otra cosa, según lo que los usuarios requieran.
- Hay bastantes refactors que podrían hacerse para mantener el código más legible, fácil de entender y, así, de mantener. 
Lo primero que haría en este sentido sería mover las interacciones con la base de datos a un módulo aparte, para quitar esa lógica
de las otras partes del código. No tiene sentido que la clase encargada de clasificar las aplicaciones sea también la encargada de 
hacer las queries a la DB (en última instancia, lo que se haga desde esa clase necesariamente deberá afectar a la base de datos, 
pero su implementación debería hacerse por separado).
- En la misma línea que el punto anterior: la obtención de parámetros globales para el backend no debería hacerse 
desde cualquier sitio. Debería existir un módulo para cargar las configuraciones del entorno (el token de la api, los nombres
de los ficheros Excel, etc). Para esto, se podría usar el módulo de settings de Pydantic, que ya se usa en otras partes del backend.
- Agregar autenticado y sistemas de permisos para la API. Es probable que no se quiera que todos los usuarios puedan clasificar 
aplicaciones aunque tengan acceso al portal para ver las que ya están clasificadas.
- En lugar de hacer varios llamados a la API de groq, se podrían enviar batches de aplicaciones. Esto sería particularmente útil
en los casos en los que haya muchas aplicaciones por actualizar, se agilizaría el proceso.
- Falta implementar el componente en el front-end para actualizar las clasificaciones de las aplicaciones 
y los tests del endpoint correspondiente. 
- Hay algunos parámetros hardcodeados que deberían pasar a ser variables de entorno o ser configurables de alguna manera. Por ejemplo en lo referido 
a políticas de CORS o a la URL de la API que consume el front-end.