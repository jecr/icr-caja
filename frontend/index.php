<?php
if (!isset($_GET['project'])) {
    echo 'PROYECTO INDEFINIDO<br>';
    echo '<a href="../backend/">Volver</a>';
} else { ?>
<script>
<?php
$projectName = $_GET['project'];
$projectName = str_replace(' ', '_', $projectName);
echo 'var proyecto = "' . $projectName . '";';
?>
</script>
<!DOCTYPE html>
<html lang="es">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <head>
        <title>Grafo <?php echo strtoupper($_GET['project']); ?></title>
        
        <link rel="stylesheet" type="text/css"
            href="http://getbootstrap.com/dist/css/bootstrap.css">
        <link rel="stylesheet" type="text/css"
            href="http://www.bootstrap-switch.org/dist/css/bootstrap3/bootstrap-switch.css">
        <link rel="stylesheet" type="text/css" href="css/graphStyles.css">

        <script>
              function openNav() {
                  document.getElementById("mySidenav").style.width = "330px";
                  // document.getElementById("mySidenav").style.padding.left = "20px";
                  // document.getElementById("main").style.marginLeft = "330px";
              }

              function closeNav() {
                  document.getElementById("mySidenav").style.width = "0";
                  // document.getElementById("main").style.marginLeft= "0";
              }
        </script>
    </head>

    <body>

        <div id="mySidenav" class="sidenav">
            <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>

            <p class="head">NODOS</p>

            <div class="empty">

                <p class="italic">Se muestran interacciones de:</p>

                <div id="selectorsNodes">

                    <div id="ck2-button">
                        <label>
                            <input type="checkbox" id="Ciudadanos" checked><span>Ciudadanos</span>
                        </label>
                    </div>

                    <div id="ck2-button">
                        <label>
                            <input type="checkbox" id="Politicos" checked><span>Políticos</span>
                        </label>
                    </div>

                    <div id="ck2-button">
                        <label>
                            <input type="checkbox" id="Medios" checked><span>Medios</span>
                        </label>
                    </div>

                </div>
                <br><br>

                <p class="italic">El tama&ntilde;o de los nodos refleja:</p>

                <!-- <button id="degree">In/Out-Degree</button><br> -->
                <div id="degree">
                    <input type="radio" name="nodeSize" id="inDegree" checked />
                    <label for="inDegree" style="font-size:1em;">Grado de entrada</label><br>
                    <input type="radio" name="nodeSize" id="outDegree" />
                    <label for="outDegree" style="font-size:1em;">Grado de salida</label><br>
                </div>
                <br>

                <button id="tamanio">Igualar el tama&ntilde;o de los nodos</button>

                <br><br>    

                <button id="et">Mostrar nombres del Top 10</button>
                

                <div id="filtros">
                      <!-- <button id="nc">ColorNodos</button>&nbsp;&nbsp; -->
                </div>

            </div>
            <br>

            <hr>

            <br>

            <p class="head">ENLACES</p>

            <div class="empty">
                <p class="italic">Se muestran estos tipos de interacci&oacute;n:</p>
                <div id="selectors">
                        
                    <div id="ck-button">
                           <label>
                              <input type="checkbox" id="Retweets" checked><span>Retuits</span>
                           </label>
                    </div>

                    <div id="ck-button">
                           <label>
                              <input type="checkbox" id="Mentions" checked><span>Menciones</span>
                           </label>
                    </div>

                    <div id="ck-button">
                           <label>
                              <input type="checkbox" id="Replies" checked><span>Respuestas</span>
                           </label>
                    </div>

                </div>

                <br>

                <div>
                    <label class="switch">
                        <input id="enlaces2" type="checkbox" checked>
                        <div class="slider round"></div>
                    </label>
                </div>

                <br><br>

                <button id="bidirect">Ver solo interacciones bidireccionales</button>

                <br><br>

                <button id="background">Cambiar el color del fondo</button>

            </div>

        </div>

        <div>

            &nbsp;&nbsp;<span style="font-size:30px;color:white;cursor:pointer" onclick="openNav()">&#9776;</span>
        
        </div>


        <div id="bsc" class="ui-widget" style="position:absolute;right:0px;">
            <input type="text" id="buscador" name="buscador" />
            <button id="buscar">Buscar Nodo</button>
        </div>

        <script src='http://code.jquery.com/jquery-2.0.2.js'></script>
        <script src="lib/d3/d3.min.js"></script>
        <script src="lib/d3-tip-master/index.js"></script>
        <script src="lib/jquery/jquery-ui.js"></script>
        <script type="text/javascript" src="js/graphCode.js"></script>
        <script>
          $(function() {
            $( "#check" ).button();
            $( "#format" ).buttonset();
            // $( "#selectors" ).buttonset();
          });
        </script>
    <div class='boton'>Centrar</div>
    </body>

</html>
<?php } ?>