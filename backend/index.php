<!DOCTYPE html>
<html>
<head>
	<title>Administrador de proyectos</title>
	<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
	<link rel="stylesheet" type="text/css" href="util/style.css">
</head>
<body>
<div class="main-div">
<form action="" method="get">
	<p>
		<label for="query">Query:</label>
		<input type="text" name="query">
	</p>
	<p>
		<label for="project">Project</label>
		<input type="text" name="project">
	</p>
	<input type="submit">
</form>

<?php
if ( (isset($_GET['query']) && isset($_GET['project'])) && ( trim($_GET['query']) != '' && trim($_GET['project']) != '' ) ) {
?>

<script>
	$(document).ready(function(){
		loaDoc();
		window.location.replace('index.php');
	});
</script>


<script>
function loaDoc() {
	var jqxhr = $.get("exec.php",{query:<?php echo "'".$_GET['query']."'"; ?>, project:<?php echo "'".$_GET['project']."'"; ?>})
	.done(function() {
		console.log( "success" );
	})
	.fail(function() {
		console.log( "error" );
	})
	.always(function() {
		console.log( "complete" );
	});	
}
</script>

<?php
}
?>

<span class="proyect">
	Proyectos almacenados
</span>

<?php
$files = scandir('.');
echo '<table>';
	foreach ($files as $value) {
		if (strpos($value, '.') > 0){
			$cosa = explode('.', $value);
			if ($cosa[1] == 'prj'){
				$parsedLines = array();
				$fileLoaded = fopen($value, "r") or die("Archivo inaccesible: " . $value);
				if ($fileLoaded) {
					while (($line = fgets($fileLoaded)) !== false) {
						array_push($parsedLines, $line);
					}
				}
				fclose($fileLoaded);
				echo "<tr>";
					echo "<td>" . $parsedLines[0] . "</td>";
					echo "<td>" . $parsedLines[1] . "</td>";
					echo '<td><a href="../frontend/index.php?project=' . $parsedLines[1] . '" target="blank">Ver red</a></td>';
				echo "</tr>";
			}
		}
	}
echo "</table>";
?>

</div>
</body>
</html>