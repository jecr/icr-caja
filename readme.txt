Proceso para la generación de la visualización de un evento:

Requisitos:
Instalar mediante terminal los siguientes

Python 2.7 ^ (incluído de fábrica en MacOS, en windows descargar e instalar)
Tweepy
	Instalación: easy_install tweepy
NLTK
	easy_install nltk
Textblob
	pip install -U textblob
	python -m textblob.download_corpora
	Nota: al parecer la ejecución web requiere de la instalación del corpus de nltk, para esto, es necesario acceder a install.php, el script se ejecutará y habrá un resúmen del log en install.log, si no es solicitada esta librería, hacer caso omiso de esta nota
WAMP (Windows) o MAMP (Mac):
	http://www.wampserver.com/en/
	Nota: NO descargar o ejecutar MAMP PRO (Al instalar MAMP se instala por default un acceso a MAMP PRO, ignorar)
	https://www.mamp.info/en/

=============================================

1. Ejecución de recupera.py:
	python recupera.py [términos_de_búsqueda] [nombre_de_proyecto]
	Nota 1: Los términos de búsqueda aceptan operadores AND y OR.
	Nota 2: Si la cadena de términos incluye espacios, es necesario agruparla entre comillas ""
	Nota 3: Los términos agrupados mediante operadores deben estar agrupados entre comillas "", si se incluyen muchos grupos de términos, es necesario escapar las comillas ""\Ejemplo de grupo"\ OR termino"

a) Ejecución de plataforma web:
	Ejecutar MAMP PRO, abrir Preferences > Web Server > Document Root
	Elegir directorio en que se encuentra la carpeta icr-caja, (Si fue clonado mediante GitHub, este es el directorio a elegir)
	Aceptar

	Abrir navegador, ingresar a localhost:8888 (puerto por default de MAMP)
	Navegar a icr-caja/backend/

	Campo query:
		Los términos de búsqueda aceptan operadores AND y OR.
		Si la cadena de términos incluye espacios, es necesario agruparla entre paréntesis ( )

	Campo Project:
		Acepta únicamente caracteres afabéticos y espacios

Nota1: La ejecución inicial puede ser muy tardada debido al entrenamiento del clasificador (dependiendo de la capacidad de procesamiento del sistema puede llegar a tomar ~1 hora)
Nota2: La ejecución subsecuente toma de 1 a 5 minutos para devolver los primeros enlaces
Nota3: La ejecución del script está configurada para un tiempo de recuperación de ~30 minutos, posterior a este tiempo es necesario volver a ingresar query y nombre de proyecto, la recuperación se continuará (Este paso se encuentra en revisión para mejora)