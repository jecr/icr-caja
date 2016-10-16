<!DOCTYPE html>
<html>
<head>
	<title></title>
	<script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
</head>
<body>
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
</body>
</html>