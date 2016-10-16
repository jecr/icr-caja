<?php
ini_set('max_execution_time', 0);

if ( (isset($_GET['query']) && isset($_GET['project'])) && ( trim($_GET['query']) != '' && trim($_GET['project']) != '' ) ) {

	// Obtiene los datos de las cajas de input
	$theQuery = trim($_GET['query']);
	$theProject = trim($_GET['project']);

	// Comprueba si hay espacios en la cadena, de haberlos, encierra el texto entre comillas para agruparlo
	if (strpos($theQuery, ' ') !== false) {
		$theQuery = '"' . $theQuery . '"';
	}

	// Reemplaza los paréntesis con comillas escapadas
	$theQuery = str_replace('(', '\\"', $theQuery);
	$theQuery = str_replace(')', '\\"', $theQuery);

	// En el nombre de proyecto, cambia los espacios vacíos por guiones bajos (esto es el nombre de carpeta)
	$theProject = str_replace(' ', '_', $theProject);

	// Ejecuta el comando, guarda el resultado en un archivo de log
	// exec('python hola.py ' . $theQuery . ' > ' . $theProject . '.log');
	exec('python recupera.py ' . $theQuery . ' ' . $theProject . ' > ' . $theProject .'.log');
}
?>