d3.json( "../backend/" + proyecto + "/" + proyecto + "_network_vis.json", function ( data ) {


    /*======================================================================
    INFORMACION SOBRE LOS NODOS Y LOS ENLACES
    ======================================================================*/


    var totalGraphNodes = data.nodes,
        totalGraphInteractions = data.links,
        nodes = data.node_sample,
        links = data.total_interactions;

    console.log( "Número de cuentas (total): " + totalGraphNodes.length + " , Número de interacciones (total): " + totalGraphInteractions.length );
    console.log( "Número de cuentas (filtrado): " + nodes.length + " , Número de interacciones (filtrado): " + links.length );

    //Calcula grado de entrada, grado de entrada y grado de cada nodo en la muestra final
    nodes.forEach( function ( d ) {
        d.inDegree = 0;
        links.forEach( function ( d1 ) {
            if ( d.name === d1.target )
                d.inDegree++;
        } );
        d.outDegree = 0;
        links.forEach( function ( d1 ) {
            if ( d.name === d1.source )
                d.outDegree++;
        } );
        d.Degree = d.inDegree + d.outDegree;
    } );

    //Ordena los nodos según su grado de salida y crea una lista con los diez primeros
    function top10OutDegree() {
        degreeNodes = nodes.sort( function ( a, b ) {
            if ( a.outDegree < b.outDegree ) {
                return 1;
            } else if ( a.outDegree > b.outDegree ) {
                return -1;
            } else {
                return 0;
            }
        } );
        var nodeList = [];
        for ( var i = 0; i < 10; i++ ) {
            var este = degreeNodes[ i ];
            nodeList.push( este );
        }
        return nodeList;
    }
    topOutDegree = top10OutDegree();

    //Ordena los nodos según su grado y crea una lista con los diez primeros
    function top10Degree() {
        degreeNodes = nodes.sort( function ( a, b ) {
            if ( a.Degree < b.Degree ) {
                return 1;
            } else if ( a.Degree > b.Degree ) {
                return -1;
            } else {
                return 0;
            }
        } );
        var nodeList = [];
        for ( var i = 0; i < 10; i++ ) {
            var este = degreeNodes[ i ];
            nodeList.push( este );
        }
        return nodeList;
    }
    topDegree = top10Degree();

    //Ordena los nodos según su grado de entrada y crea una lista con los diez primeros
    function top10InDegree() {
        degreeNodes = nodes.sort( function ( a, b ) {
            if ( a.inDegree < b.inDegree ) {
                return 1;
            } else if ( a.inDegree > b.inDegree ) {
                return -1;
            } else {
                return 0;
            }
        } );
        var nodeList = [];
        for ( var i = 0; i < 10; i++ ) {
            var este = degreeNodes[ i ];
            nodeList.push( este );
        }
        return nodeList;
    }
    topInDegree = top10InDegree();

    //Obtiene el número de interacciones por tipo de interacción
    var numRT = 0,
        numRP = 0,
        numMen = 0;
    links.forEach( function ( l ) {
        if ( l.interaction === "retweet" ) {
            numRT++;
        } else if ( l.interaction === "reply" ) {
            numRP++;
        }
        if ( l.interaction === "mention" ) {
            numMen++;
        }
    } );

    // Ordena los enlaces por origen, por destino y por tipo de interacción
    links.sort( function ( a, b ) {
        if ( a.source > b.source ) {
            return 1;
        } else if ( a.source < b.source ) {
            return -1;
        } else if ( a.target > b.target ) {
            return 1;
        } else if ( a.target < b.target ) {
            return -1;
        } else {
            if ( a.interaction > b.interaction ) {
                return 1;
            }
            if ( a.interaction < b.interaction ) {
                return -1;
            } else {
                return 0;
            }
        }
    } );

    // Establece el número de enlaces entre dos nodos, inicia en 1
    links.forEach( function ( d ) {
        d.linknum = 1;
    } );
    // Aumenta el número de enlaces si hay más de un tipo de interacción
    for ( var i = 0; i < links.length; i++ ) {
        if ( i !== 0 &&
            links[ i ].source === links[ i - 1 ].source &&
            links[ i ].target === links[ i - 1 ].target )
            if ( links[ i ].interaction !== links[ i - 1 ].interaction ) {
                links[ i ].linknum = links[ i - 1 ].linknum + 1;
            } else if ( links[ i ].interaction === links[ i - 1 ].interaction ) {
            links[ i ].linknum = links[ i - 1 ].linknum;
        }
    }

    // Determina si el enlace será recto o curvo
    links.forEach( function ( d ) {
        d.straight = 1;
        if ( d.linknum === 2 || d.linknum === 3 ) {
            d.straight = 0;
        }
        links.forEach( function ( d1 ) {
            if ( d.source === d1.target && d1.source === d.target )
                d.straight = 0;
            else if ( d.linknum === 1 && d.source === d1.source && d.target === d1.target && d1.linknum >= 2 )
                d.straight = 0;
        } );
    } );

    //Calcula la frecuencia de un tipo de interacción
    for ( var i = 0; i < links.length; i++ ) {
        if ( i !== 0 &&
            links[ i ].source === links[ i - 1 ].source &&
            links[ i ].target === links[ i - 1 ].target )
            if ( links[ i ].interaction === "mention" && links[ i ].interaction === links[ i - 1 ].interaction ) {
                links[ i ].mentions = links[ i - 1 ].mentions + 1;
            } else if ( links[ i ].interaction === "reply" && links[ i ].interaction === links[ i - 1 ].interaction ) {
            links[ i ].replies = links[ i - 1 ].replies + 1;
        } else if ( links[ i ].interaction === "retweet" && links[ i ].interaction === links[ i - 1 ].interaction ) {
            links[ i ].retuits = links[ i - 1 ].retuits + 1;
        }
    }

    //Creamos una muestra de enlaces, solo conservamos el enlace con mayor peso
    linksSample = [];
    links.forEach( function ( l ) {
        linksSample.push( l );
    } );

    for ( var i = 0; i < linksSample.length; i++ ) {
        if ( i !== 0 &&
            linksSample[ i ].source === linksSample[ i - 1 ].source &&
            linksSample[ i ].target === linksSample[ i - 1 ].target &&
            linksSample[ i ].interaction === linksSample[ i - 1 ].interaction ) {
            linksSample.splice( i - 1, 1 );
            i -= 1;
        }
    }

    //Asigna a cada nodo un atributo por tipo de interacción. Valor inicial es false
    nodes.forEach( function ( d ) {
        d.retweeting = false;
        d.replying = false;
        d.mentioning = false;
    } );
    //Busca el tipo de interacción de cada enlace, y cambia el atributo de los nodos asignado en el paso anterior
    links.forEach( function ( d ) {
        if ( d.interaction === "reply" ) {
            nodes.forEach( function ( e ) {
                if ( e.name === d.target || e.name === d.source ) {
                    e.replying = true;
                }
            } );
        } else if ( d.interaction === "mention" ) {
            nodes.forEach( function ( e ) {
                if ( e.name === d.target || e.name === d.source ) {
                    e.mentioning = true;
                }
            } );
        } else if ( d.interaction === "retweet" ) {
            nodes.forEach( function ( e ) {
                if ( e.name === d.target || e.name === d.source ) {
                    e.retweeting = true;
                }
            } );
        }
    } );

    // Establece el radio de cada nodo con base en su grado de entrada
    baseRadius = ( Math.sqrt( 1 / Math.PI ) ) * 5;
    baseNodeArea = Math.PI * ( baseRadius * baseRadius );
    nodes.forEach( function ( d ) {
        if ( d.inDegree > 0 ) {
            d.radius = Math.sqrt( ( baseNodeArea * ( d.inDegree * 1.7 ) ) / Math.PI );
        } else {
            d.radius = baseRadius;
        }
    } );

    //Cuantifica el número de cuentas según su clasificación
    var numCiu = 0,
        numMed = 0,
        numPol = 0;
    nodes.forEach( function ( n ) {
        if ( n.class === "ciudadano" ) {
            numCiu++;
        } else if ( n.class === "medio" ) {
            numMed++;
        } else if ( n.class === "politico" ) {
            numPol++;
        }
    } );

    //Distribución de nodos en RETUITS
    var nodesRT = 0,
        rtMedios = 0,
        rtPoliticos = 0,
        rtCiudadanos = 0;
    nodes.forEach( function ( n ) {
        if ( n.retweeting ) {
            nodesRT++;
            if ( n.class === "medio" ) {
                rtMedios++;
            } else if ( n.class === "politico" ) {
                rtPoliticos++;
            } else if ( n.class === "ciudadano" ) {
                rtCiudadanos++;
            }
        }
    } );

    //Distribución de nodos en REPLIES
    var nodesRP = 0,
        rpMedios = 0,
        rpPoliticos = 0,
        rpCiudadanos = 0;
    nodes.forEach( function ( n ) {
        if ( n.replying ) {
            nodesRP++;
            if ( n.class === "medio" ) {
                rpMedios++;
            } else if ( n.class === "politico" ) {
                rpPoliticos++;
            } else if ( n.class === "ciudadano" ) {
                rpCiudadanos++;
            }
        }
    } );

    //Distribución de nodos en MENCIONES
    var nodesMn = 0,
        mnMedios = 0,
        mnPoliticos = 0,
        mnCiudadanos = 0;
    nodes.forEach( function ( n ) {
        if ( n.mentioning ) {
            nodesMn++;
            if ( n.class === "medio" ) {
                mnMedios++;
            } else if ( n.class === "politico" ) {
                mnPoliticos++;
            } else if ( n.class === "ciudadano" ) {
                mnCiudadanos++;
            }
        }
    } );

    //Añade los nodos completos (i.e.toda la info, no solo el nombre) a source y target en los enlaces
    links.forEach( function ( l ) {
        nodes.forEach( function ( n ) {
            if ( l.source === n.name ) {
                l.source = n;
            } else if ( l.target === n.name ) {
                l.target = n;
            }
        } );
    } );

    // Cuantifica interacciones inter e intra; y cada una la divide por tipo de interacción
    var intraActores = [],
        interActores = [];
    var intraRt = 0,
        intraRp = 0,
        intraMn = 0;
    var interRt = 0,
        interRp = 0,
        interMn = 0;

    links.forEach( function ( l ) {
        if ( l.source.class === l.target.class ) {
            intraActores.push( l );
            if ( l.interaction === "retweet" ) {
                intraRt++;
            } else if ( l.interaction === "reply" ) {
                intraRp++;
            } else if ( l.interaction === "mention" ) {
                intraMn++;
            }
        } else if ( l.source.class !== l.target.class ) {
            interActores.push( l );
            if ( l.interaction === "retweet" ) {
                interRt++;
            } else if ( l.interaction === "reply" ) {
                interRp++;
            } else if ( l.interaction === "mention" ) {
                interMn++;
            }
        }
    } );

    //Divide las interacciones intra por tipo de actor
    var intraC = 0,
        intraP = 0,
        intraM = 0;
    var intraCRt = 0,
        intraCRp = 0;
    intraCM = 0;
    var intraMRt = 0,
        intraMRp = 0;
    intraMM = 0;
    var intraPRt = 0,
        intraPRp = 0;
    intraPM = 0;
    intraActores.forEach( function ( l ) {
        if ( l.source.class === "ciudadano" && l.target.class === "ciudadano" ) {
            intraC++;
            if ( l.interaction === "retweet" ) {
                intraCRt++;
            } else if ( l.interaction === "reply" ) {
                intraCRp++;
            } else if ( l.interaction === "mention" ) {
                intraCM++;
            }
        } else if ( l.source.class === "medio" && l.target.class === "medio" ) {
            intraM++;
            if ( l.interaction === "retweet" ) {
                intraMRt++;
            } else if ( l.interaction === "reply" ) {
                intraMRp++;
            } else if ( l.interaction === "mention" ) {
                intraMM++;
            }
        } else if ( l.source.class === "politico" && l.target.class === "politico" ) {
            intraP++;
            if ( l.interaction === "retweet" ) {
                intraPRt++;
            } else if ( l.interaction === "reply" ) {
                intraPRp++;
            } else if ( l.interaction === "mention" ) {
                intraPM++;
            }
        }
    } );

    //Divide las interacciones inter por pares de actores
    var interCM = 0,
        interCP = 0,
        interPM = 0;
    var interCMRt = 0,
        interCMRp = 0,
        interCMM = 0;
    var interCPRt = 0,
        interCPRp = 0,
        interCPM = 0;
    var interPMRt = 0,
        interPMRp = 0,
        interPMM = 0;
    interActores.forEach( function ( l ) {
        if ( ( l.source.class === "ciudadano" && l.target.class === "medio" ) || ( l.source.class === "medio" && l.target.class === "ciudadano" ) ) {
            interCM++;
            if ( l.interaction === "retweet" ) {
                interCMRt++;
            } else if ( l.interaction === "reply" ) {
                interCMRp++;
            } else if ( l.interaction === "mention" ) {
                interCMM++;
            }
        } else if ( ( l.source.class === "ciudadano" && l.target.class === "politico" ) || ( l.source.class === "politico" && l.target.class === "ciudadano" ) ) {
            interCP++;
            if ( l.interaction === "retweet" ) {
                interCPRt++;
            } else if ( l.interaction === "reply" ) {
                interCPRp++;
            } else if ( l.interaction === "mention" ) {
                interCPM++;
            }
        } else if ( ( l.source.class === "politico" && l.target.class === "medio" ) || ( l.source.class === "medio" && l.target.class === "politico" ) ) {
            interPM++;
            if ( l.interaction === "retweet" ) {
                interPMRt++;
            } else if ( l.interaction === "reply" ) {
                interPMRp++;
            } else if ( l.interaction === "mention" ) {
                interPMM++;
            }
        }
    } );

    //Imprime en consola datos cuantitativos sobre el grafo
    console.log( "Número de enlaces: " + linksSample.length );
    console.log( "Ciudadanos: " + numCiu + "(" + porcentaje( numCiu, nodes.length ) + "%)" + ", Medios: " + numMed + "(" + porcentaje( numMed, nodes.length ) + "%)" + ", Politicos: " + numPol + "(" + porcentaje( numPol, nodes.length ) + "%)" );
    console.log( "Retuits: " + numRT + "(" + porcentaje( numRT, links.length ) + "%)" + ", Respuestas: " + numRP + "(" + porcentaje( numRP, links.length ) + "%)" + ", Menciones: " + numMen + "(" + porcentaje( numMen, links.length ) + "%)" );
    console.log( " " );
    console.log( "NODOS CON MAYOR GRADO" );
    topDegree.forEach( function ( n ) {
        console.log( n.name + ", " + n.class + ", G:" + n.Degree );
    } );
    console.log( " " );
    console.log( "NODOS CON MAYOR GRADO DE ENTRADA" );
    topInDegree.forEach( function ( n ) {
        console.log( n.name + ", " + n.class + ", GE:" + n.inDegree + ", GS: " + n.outDegree );
    } );
    console.log( " " );
    console.log( "NODOS CON MAYOR GRADO DE SALIDA" );
    topOutDegree.forEach( function ( n ) {
        console.log( n.name + ", " + n.class + ", G:" + n.outDegree );
    } );
    console.log( " " );
    console.log( "DISTRIBUCIÓN DE NODOS POR TIPO DE INTERACCION" );
    console.log( "Retuits: " + "C=" + porcentaje( rtCiudadanos, nodesRT ) + "%(" + rtCiudadanos + "), SM=" + porcentaje( rtMedios, nodesRT ) + "%(" + rtMedios + "), SP=" + porcentaje( rtPoliticos, nodesRT ) + "%(" + rtPoliticos + ")" );
    console.log( "Respuestas: " + "C=" + porcentaje( rpCiudadanos, nodesRP ) + "%(" + rpCiudadanos + "), SM=" + porcentaje( rpMedios, nodesRP ) + "%(" + rpMedios + "), SP=" + porcentaje( rpPoliticos, nodesRP ) + "%(" + rpPoliticos + ")" );
    console.log( "Menciones: " + "C=" + porcentaje( mnCiudadanos, nodesMn ) + "%(" + mnCiudadanos + "), SM=" + porcentaje( mnMedios, nodesMn ) + "%(" + mnMedios + "), SP=" + porcentaje( mnPoliticos, nodesMn ) + "%(" + mnPoliticos + ")" );
    console.log( " " );
    console.log( "INTRA-ACTORES: " + intraActores.length + "(" + porcentaje( intraActores.length, links.length ) + "% del total de interacciones)" );
    console.log( "Retuits: " + intraRt + ", Respuestas: " + intraRp + ", Menciones: " + intraMn );
    console.log( "Intra-Ciudadanos: " + intraC + " (Retuits: " + intraCRt + ", Respuestas: " + intraCRp + ", Menciones: " + intraCM + ")" );
    console.log( "Intra-Medios: " + intraM + " (Retuits: " + intraMRt + ", Respuestas: " + intraMRp + ", Menciones: " + intraMM + ")" );
    console.log( "Intra-Politicos: " + intraP + " (Retuits: " + intraPRt + ", Respuestas: " + intraPRp + ", Menciones: " + intraPM + ")" );
    console.log( " " );
    console.log( "INTER-ACTORES: " + interActores.length + "(" + porcentaje( interActores.length, links.length ) + "% del total de interacciones)" );
    console.log( "Retuits: " + interRt + ", Respuestas: " + interRp + ", Menciones: " + interMn );
    console.log( "Inter Ciudadanos-Medios: " + interCM + " (Retuits: " + interCMRt + ", Respuestas: " + interCMRp + ", Menciones: " + interCMM + ")" );
    console.log( "Inter Ciudadanos-Politicos: " + interCP + " (Retuits: " + interCPRt + ", Respuestas: " + interCPRp + ", Menciones: " + interCPM + ")" );
    console.log( "Inter Politicos-Medios: " + interPM + " (Retuits: " + interPMRt + ", Respuestas: " + interPMRp + ", Menciones: " + interPMM + ")" );


    /*======================================================================
        PARAMETROS VISUALES DEL GRAFO
    ======================================================================*/


    // Tamaño del SVG
    var width = $( window )
        .width();
    height = $( window )
        .height();

    // Tipo de visualización
    var force = d3.layout.force()
        .charge( function ( d ) {
            return ( d.inDegree + 1 ) * ( -180 );
        } )
        .linkDistance( 40 )
        .gravity( .3 )
        .size( [ width, height ] );

    // Dibuja el tooltip con info del nodo señalado
    var tip = d3.tip()
        .attr( 'class', 'd3-tip' )
        .offset( [ -10, 0 ] )
        .html( function ( d ) {
            return "<span style='color:white'>" + d.name + " | GE:" + d.inDegree + " GS:" + d.outDegree + "</span>";
        } );

    var zoom = d3.behavior.zoom()
        .scaleExtent( [ .1, 8 ] )
        .on( "zoom", redraw );

    // Se inicializa el svg
    var vis = d3.select( "body" ).append( "svg" )
        .attr( "width", width )
        .attr( "height", height )
        .attr( "pointer-events", "all" )
        .call( zoom )
        .append( "g" )
        .call( tip );

    $( 'g' ).attr( 'id', 'grafo' );
    grafo = document.getElementById( 'grafo' );

    // Zoom
    function redraw() {
        vis.attr( "transform",
            "translate(" + d3.event.translate + ")" +
            " scale(" + d3.event.scale + ")" );
        // console.log(((grafo.transform.animVal[1].matrix.a) * 100).toFixed(2))
        // console.log( grafo.transform.animVal[ 0 ].matrix.e + ', ' + grafo.transform.animVal[ 0 ].matrix.f );
        grafox = grafo.transform.animVal[ 0 ].matrix.e;
        grafoy = grafo.transform.animVal[ 0 ].matrix.f;
    }

    $( '.boton' ).on( 'click', function () {
        var dcx = ( window.innerWidth / 2 - grafox * zoom.scale() );
        var dcy = ( window.innerHeight / 2 - grafoy * zoom.scale() );
        zoom.translate( [ dcx, dcy ] );
        vis.attr( "transform", "translate(" + dcx + "," + dcy + ") scale(" + zoom.scale() + ")" );
    } );

    force
        .nodes( nodes )
        .links( linksSample )
        .start();

    var link = vis.selectAll( ".link" )
        .data( linksSample )
        .enter()
        .append( "path" )
        .attr( "class", function ( d ) {
            return d.interaction;
        } )
        .attr( "fill", "none" )
        .style( "stroke-width", function ( d ) {
            if ( d.interaction === "reply" ) {
                return d.replies;
            } else if ( d.interaction === "retweet" ) {
                return d.retuits;
            } else {
                return d.mentions;
            }
        } )
        .style( "marker-end", "url(#flecha)" );

    var linkLabel = vis.selectAll( ".label" )
        .data( linksSample )
        .enter()
        .append( "text" )
        .attr( "dx", 0 )
        .attr( "dy", 0 )
        .attr( "class", "label" )
        .text( function ( d ) {
            if ( d.replies > 1 ) {
                return d.replies;
            } else if ( d.retuits > 1 ) {
                return d.retuits;
            } else if ( d.mentions > 1 ) {
                return d.mentions;
            }
        } )
        .style( "opacity", 0 );

    var marker = vis.selectAll( "marker" )
        .data( linksSample )
        .enter()
        .append( "marker" )
        .attr( "id", "flecha" )
        .attr( "viewBox", "0 -8 16 16" )
        .attr( "refX", 15 )
        .attr( "markerUnits", "userSpaceOnUse" )
        .attr( "markerWidth", 10 )
        .attr( "markerHeight", 15 )
        .attr( "orient", "auto" )
        .append( "path" )
        .attr( "stroke", "#14141c" )
        .attr( "fill", "#F2F3F4" )
        .attr( "stroke-width", 1 )
        .attr( "d", "M0,-5 L 14,0 L0,5 L4,0 Z" );

    var drag = force.drag()
        .on( "dragstart", function ( d ) {
            d3.event.sourceEvent.stopPropagation();
            d3.event.sourceEvent.preventDefault();
        } );

    var node = vis.selectAll( ".node" )
        .data( nodes )
        .enter()
        .append( "circle" )
        .attr( "id", function ( d ) {
            return "c" + d.name;
        } )
        .attr( "r", function ( d ) {
            return d.radius;
        } )
        .attr( "class", function ( d ) {
            return d.class;
        } )
        .on( "mouseover", tip.show )
        .on( "mouseout", tip.hide )
        .on( 'click', function ( d ) {
            if ( d3.event.defaultPrevented === false ) {
                connectedNodes( d );
                d3.selectAll( "#selectors input[type=checkbox]" )
                    .property( "checked", true );
                howMany = 3;
            }
        } );

    var text = vis.selectAll( ".text" )
        .data( nodes )
        .enter()
        .append( "text" )
        .attr( "dx", 16 )
        .attr( "dy", 6 )
        .attr( "class", "text" )
        .attr( "font-size", function ( d ) {
            return Math.sqrt( ( d.inDegree + 10 ) * 25 ) + "px";
        } )
        .text( function ( d ) {
            for ( var i = 0; i < topInDegree.length; i++ ) {
                name = topInDegree[ i ].name;
                if ( d.name === name ) {
                    return d.name;
                }
            }
        } )
        .style( "opacity", 0 );

    force.on( "tick", function () {
        link.attr( "d", function ( d ) {

            //Enlaces bidireccionales curvos, unidireccionales rectos
            diffX = d.target.x - d.source.x;
            diffY = d.target.y - d.source.y;

            // Length of path from center of source node to center of target node
            pathLength = Math.sqrt( ( diffX * diffX ) + ( diffY * diffY ) );

            // x and y distances from center to outside edge of target node
            if ( pathLength === 0 ) {
                pathLength = 0.01;
            }

            offsetX = ( diffX * d.target.radius ) / pathLength;
            offsetY = ( diffY * d.target.radius ) / pathLength;

            dr = ( d.straight === 1 ) ? 0 : Math.sqrt( diffX * diffX + diffY * diffY ) * d.linknum;


            return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1" + ( d.target.x - offsetX ) + "," + ( d.target.y - offsetY );
        } );

        node.attr( "cx", function ( d ) {
                return d.x;
            } )
            .attr( "cy", function ( d ) {
                return d.y;
            } );

        text.attr( "x", function ( d ) {
                return d.x;
            } )
            .attr( "y", function ( d ) {
                return d.y;
            } );

        linkLabel.attr( "x", function ( d ) {
                return ( d.source.x + d.target.x ) / 2;
            } )
            .attr( "y", function ( d ) {
                return ( d.source.y + d.target.y ) / 2;
            } );
    } );


    /*======================================================================
        FILTROS Y FUNCIONES INTERACTIVAS
    ======================================================================*/

    // Almacena las conexiones entre nodos
    var linkedByIndex = {};
    links.forEach( function ( d ) {
        linkedByIndex[ d.source.name + "," + d.target.name ] = 1;
    } );

    // Verifica si un par de nodos son vecinos
    function neighboring( a, b ) {
        return linkedByIndex[ a.name + "," + b.name ] || a.name === b.name;
    }

    // Crea una lista de adyacencia: {[Nodo1: vecino1,..., vecino n],...,[Nodon]}
    adjacencyList = {};
    nodes.forEach( function ( d ) {
        neighborhood = [];
        adjacencyList[ d.name ] = neighborhood;
        nodes.forEach( function ( n ) {
            if ( neighboring( d, n ) | neighboring( n, d ) && n !== d ) {
                neighborhood.push( n.name );
            }
        } );
    } );

    // Establece si un nodo es vecino de medio, de ciudadano o de politico
    nodes.forEach( function ( n ) {
        Object.keys( adjacencyList )
            .forEach( function ( v ) {
                if ( n.name === v && n.class === "medio" ) {
                    adjacencyList[ v ].forEach( function ( d ) {
                        nodes.forEach( function ( e ) {
                            if ( e.name === d ) {
                                e.vDeM = true;
                            }
                        } );
                    } );
                } else if ( n.name === v && n.class === "ciudadano" ) {
                    adjacencyList[ v ].forEach( function ( d ) {
                        nodes.forEach( function ( e ) {
                            if ( e.name === d ) {
                                e.vDeC = true;
                            }
                        } );
                    } );
                } else if ( n.name === v && n.class === "politico" ) {
                    adjacencyList[ v ].forEach( function ( d ) {
                        nodes.forEach( function ( e ) {
                            if ( e.name === d ) {
                                e.vDeP = true;
                            }
                        } );
                    } );
                }
            } );
    } );

    // Subconjuntos de nodos por tipo de interacción
    var RtRpM = [],
        RtRp = [],
        RtM = [],
        RpM = [],
        Rp = [],
        Rt = [],
        M = [];
    nodes.forEach( function ( d ) {
        //Retuits+Replies+Menciones
        if ( d.retweeting === true && d.replying === true && d.mentioning === true ) {
            RtRpM.push( d );
        }
        //Retuits+Replies-Menciones
        if ( ( d.retweeting === true && d.replying === true && d.mentioning === false ) || ( d.replying === true && d.mentioning === false && d.retweeting === false ) || ( d.retweeting === true && d.replying === false && d.mentioning === false ) ) {
            RtRp.push( d );
        }
        //Retuits+Menciones-Replies
        if ( ( d.retweeting === true && d.replying === false && d.mentioning === false ) || ( d.retweeting === true && d.mentioning === true && d.replying === false ) || ( d.mentioning === true && d.retweeting === false && d.replying === false ) ) {
            RtM.push( d );
        }
        //Replies+Menciones-Retuits
        if ( ( d.replying === true && d.mentioning === true && d.retweeting === false ) || ( d.replying === true && d.mentioning === false && d.retweeting === false ) || ( d.mentioning === true && d.retweeting === false && d.replying === false ) ) {
            RpM.push( d );
        }
        if ( d.replying === true && d.mentioning === false && d.retweeting === false ) {
            Rp.push( d );
        }
        if ( d.retweeting === true && d.replying === false && d.mentioning === false ) {
            Rt.push( d );
        }
        if ( d.mentioning === true && d.retweeting === false && d.replying === false ) {
            M.push( d );
        }
    } );

    // Subconjuntos de enlaces
    var eRpRt = [],
        eRpM = [],
        eRtM = [];
    links.forEach( function ( d ) {
        if ( d.interaction === "retweet" || d.interaction === "reply" ) {
            eRpRt.push( d );
        }
        if ( d.interaction === "reply" || d.interaction === "mention" ) {
            eRpM.push( d );
        }
        if ( d.interaction === "retweet" || d.interaction === "mention" ) {
            eRtM.push( d );
        }
    } );

    //Checa cuántos checkboxes de tipos de interacción están activos y ejecuta una función para mostrar/esconder interacciones
    var howMany = 3;
    d3.selectAll( "#selectors input[type=checkbox]" )
        .on( "click", function () {
            if ( this.checked === true ) {
                howMany++;
            } else if ( this.checked === false && howMany > 0 ) {
                howMany--;
            } else if ( howMany < 0 ) {
                howMany = 0;
            }
            hideElements();
        } );

    //Checa qué checkboxes están seleccionados y oculta enlaces, con sus respectivos nodos, según tipo de interacción
    function hideElements() {
        d3.selectAll( "#selectors input[type=checkbox]" )
            .each( function ( d ) {
                // if(howMany===3){
                //   node.style("opacity",1);
                //   link.style("opacity",1);
                // }
                switch ( howMany ) {
                    case 0:
                        node.style( "opacity", 0 );
                        link.style( "opacity", 0 );
                        d3.selectAll( "#enlaces2" )
                            .property( "checked", false );
                        cambio = 1;
                    case 1:
                        if ( d3.select( "#Retweets" )
                            .property( "checked" ) === true ) {
                            link.filter( function ( d ) {
                                    for ( var i = 0; i < eRpM.length; i++ ) {
                                        if ( d === eRpM[ i ] ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                            node.filter( function ( d ) {
                                    for ( var i = 0; i < RpM.length; i++ ) {
                                        if ( d.name === RpM[ i ].name ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                        }
                        if ( d3.select( "#Replies" )
                            .property( "checked" ) === true ) {
                            link.filter( function ( d ) {
                                    for ( var i = 0; i < eRtM.length; i++ ) {
                                        if ( d === eRtM[ i ] ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                            node.filter( function ( d ) {
                                    for ( var i = 0; i < RtM.length; i++ ) {
                                        var nodo = RtM[ i ];
                                        if ( d.name === RtM[ i ].name ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                        }
                        if ( d3.select( "#Mentions" )
                            .property( "checked" ) === true ) {
                            link.filter( function ( d ) {
                                    for ( var i = 0; i < eRpRt.length; i++ ) {
                                        if ( d === eRpRt[ i ] ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                            node.filter( function ( d ) {
                                    for ( var i = 0; i < RtRp.length; i++ ) {
                                        var nodo = RtRp[ i ];
                                        if ( d.name === RtRp[ i ].name ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                        }
                    case 2:
                        if ( d3.select( "#Replies" )
                            .property( "checked" ) === true && d3.select( "#Retweets" )
                            .property( "checked" ) === true ) {
                            link.filter( function ( d ) {
                                    return d.interaction === "mention";
                                } )
                                .style( "opacity", 0 );
                            node.filter( function ( d ) {
                                    for ( var i = 0; i < M.length; i++ ) {
                                        var nodo = M[ i ];
                                        if ( d.name === M[ i ].name ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                        }
                        if ( d3.select( "#Replies" )
                            .property( "checked" ) === true && d3.select( "#Mentions" )
                            .property( "checked" ) === true ) {
                            link.filter( function ( d ) {
                                    return d.interaction === "retweet";
                                } )
                                .style( "opacity", 0 );
                            node.filter( function ( d ) {
                                    for ( var i = 0; i < Rt.length; i++ ) {
                                        var nodo = Rt[ i ];
                                        if ( d.name === Rt[ i ].name ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                        }
                        if ( d3.select( "#Retweets" )
                            .property( "checked" ) === true && d3.select( "#Mentions" )
                            .property( "checked" ) === true ) {
                            link.filter( function ( d ) {
                                    return d.interaction === "reply";
                                } )
                                .style( "opacity", 0 );
                            node.filter( function ( d ) {
                                    for ( var i = 0; i < Rp.length; i++ ) {
                                        var nodo = Rp[ i ];
                                        if ( d.name === Rp[ i ].name ) {
                                            return d;
                                        }
                                    }
                                } )
                                .style( "opacity", 0 );
                        }
                }
            } );
    }

    //Checa qué checkboxes se desactivan y muestra enlaces, con sus respectivos nodos, según tipo de interacción
    d3.selectAll( "#selectors label" )
        .on( "mouseup", function ( d ) {
            if ( d3.select( "#Mentions" )
                .property( "checked" === true ) ) {
                link.filter( function ( d ) {
                        for ( var i = 0; i < eRpRt.length; i++ ) {
                            if ( d === eRpRt[ i ] ) {
                                return d;
                            }
                        }
                    } )
                    .style( "opacity", 1 );
                node.filter( function ( d ) {
                        for ( var i = 0; i < RtRp.length; i++ ) {
                            var nodo = RtRp[ i ];
                            if ( d.name === RtRp[ i ].name ) {
                                return d;
                            }
                        }
                        for ( var i = 0; i < RtRpM.length; i++ ) {
                            var nodo = RtRpM[ i ];
                            if ( d.name === RtRpM[ i ].name ) {
                                return d;
                            }
                        }
                    } )
                    .style( "opacity", 1 );
                d3.selectAll( "#enlaces2" )
                    .property( "checked", true );
                cambio = 0;
            }
            if ( d3.select( "#Retweets" )
                .property( "checked" === true ) ) {
                link.filter( function ( d ) {
                        for ( var i = 0; i < eRpM.length; i++ ) {
                            if ( d === eRpM[ i ] ) {
                                return d;
                            }
                        }
                    } )
                    .style( "opacity", 1 );
                node.filter( function ( d ) {
                        for ( var i = 0; i < RpM.length; i++ ) {
                            var nodo = RpM[ i ];
                            if ( d.name === RpM[ i ].name ) {
                                return d;
                            }
                        }
                        for ( var i = 0; i < RtRpM.length; i++ ) {
                            var nodo = RtRpM[ i ];
                            if ( d.name === RtRpM[ i ].name ) {
                                return d;
                            }
                        }
                    } )
                    .style( "opacity", 1 );
                d3.selectAll( "#enlaces2" )
                    .property( "checked", true );
                cambio = 0;
            }
            if ( d3.select( "#Replies" )
                .property( "checked" === true ) ) {
                link.filter( function ( d ) {
                        for ( var i = 0; i < eRtM.length; i++ ) {
                            if ( d === eRtM[ i ] ) {
                                return d;
                            }
                        }
                    } )
                    .style( "opacity", 1 );
                node.filter( function ( d ) {
                        for ( var i = 0; i < RtM.length; i++ ) {
                            var nodo = RtM[ i ];
                            if ( d.name === RtM[ i ].name ) {
                                return d;
                            }
                        }
                        for ( var i = 0; i < RtRpM.length; i++ ) {
                            var nodo = RtRpM[ i ];
                            if ( d.name === RtRpM[ i ].name ) {
                                return d;
                            }
                        }
                    } )
                    .style( "opacity", 1 );
                d3.selectAll( "#enlaces2" )
                    .property( "checked", true );
                cambio = 0;
            }
        } );

    //Checa cuántos checkboxes de nodos están activos y ejecuta una función para mostrar/esconder nodos
    var howManyNodes = 3;
    d3.selectAll( "#selectorsNodes input[type=checkbox]" )
        .on( "click", function () {
            if ( this.checked === true ) {
                howManyNodes++;
            } else if ( this.checked === false && howManyNodes > 0 ) {
                howManyNodes--;
            } else if ( howManyNodes < 0 ) {
                howManyNodes = 0;
            }
            hidingNodes();
        } );

    var cambiaTamanio = 0;
    d3.selectAll( "#degree input" )
        .on( "click", function ( d ) {
            if ( d3.select( "#inDegree" )
                .property( "checked" ) === true ) {
                nodes.forEach( function ( d ) {
                    baseRadius = ( Math.sqrt( 1 / Math.PI ) ) * 5;
                    baseNodeArea = Math.PI * ( baseRadius * baseRadius );
                    if ( d.inDegree > 0 ) {
                        d.radius = Math.sqrt( ( baseNodeArea * ( d.inDegree * 1.7 ) ) / Math.PI );
                    } else {
                        d.radius = baseRadius;
                    }
                } );
                node.attr( "r", function ( n ) {
                    return n.radius;
                } );
                link.attr( "d", function ( d ) {

                    //Enlaces bidireccionales curvos, unidireccionales rectos
                    diffX = d.target.x - d.source.x;
                    diffY = d.target.y - d.source.y;

                    // Length of path from center of source node to center of target node
                    pathLength = Math.sqrt( ( diffX * diffX ) + ( diffY * diffY ) );

                    // x and y distances from center to outside edge of target node
                    if ( pathLength === 0 ) {
                        pathLength = 0.01;
                    }

                    offsetX = ( diffX * d.target.radius ) / pathLength;
                    offsetY = ( diffY * d.target.radius ) / pathLength;

                    dr = ( d.straight === 1 ) ? 0 : Math.sqrt( diffX * diffX + diffY * diffY ) * d.linknum;


                    return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1" + ( d.target.x - offsetX ) + "," + ( d.target.y - offsetY );
                } );
                cambiaTamanio = 0;
                tamanio = 0;
            } else if ( d3.select( "#outDegree" )
                .property( "checked" ) === true ) {
                nodes.forEach( function ( d ) {
                    baseRadius = ( Math.sqrt( 1 / Math.PI ) ) * 5;
                    baseNodeArea = Math.PI * ( baseRadius * baseRadius );
                    if ( d.outDegree > 0 ) {
                        d.radius = Math.sqrt( ( baseNodeArea * ( d.outDegree * 1.7 ) ) / Math.PI );
                    } else {
                        d.radius = baseRadius;
                    }
                } );
                node.attr( "r", function ( n ) {
                    return n.radius;
                } );
                link.attr( "d", function ( d ) {

                    //Enlaces bidireccionales curvos, unidireccionales rectos
                    diffX = d.target.x - d.source.x;
                    diffY = d.target.y - d.source.y;

                    // Length of path from center of source node to center of target node
                    pathLength = Math.sqrt( ( diffX * diffX ) + ( diffY * diffY ) );

                    // x and y distances from center to outside edge of target node
                    if ( pathLength === 0 ) {
                        pathLength = 0.01;
                    }

                    offsetX = ( diffX * d.target.radius ) / pathLength;
                    offsetY = ( diffY * d.target.radius ) / pathLength;

                    dr = ( d.straight === 1 ) ? 0 : Math.sqrt( diffX * diffX + diffY * diffY ) * d.linknum;


                    return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1" + ( d.target.x - offsetX ) + "," + ( d.target.y - offsetY );
                } );
                cambiaTamanio = 1;
                tamanio = 0;
            }
        } );

    //Verifica qué checkboxes están activos y solo muestra enlaces/nodos de las categorías seleccionadas
    function hidingNodes() {
        d3.selectAll( "#selectorsNodes input" )
            .each( function ( d ) {
                if ( howManyNodes === 0 ) {
                    node.style( "opacity", 0 );
                    link.style( "opacity", 0 );
                } else if ( howManyNodes === 2 && d3.select( "#Politicos" )
                    .property( "checked" ) === true && d3.select( "#Medios" )
                    .property( "checked" ) === true ) {
                    link.filter( function ( l ) {
                            if ( l.source.class === "ciudadano" || l.target.class === "ciudadano" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 0 );
                    node.filter( function ( n ) {
                            if ( n.class === "ciudadano" ) {
                                return n;
                            } else if ( n.class === "medio" && n.vDeC === true && n.vDeM === undefined && n.vDeP === undefined ) {
                                return n;
                            } else if ( n.class === "politico" && n.vDeC === true && n.vDeM === undefined && n.vDeP === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 0 );
                    text.style( "opacity", 0 );
                    top10Labels = 0;
                } else if ( howManyNodes === 2 && d3.select( "#Politicos" )
                    .property( "checked" ) === true && d3.select( "#Ciudadanos" )
                    .property( "checked" ) === true ) {
                    link.filter( function ( l ) {
                            if ( l.source.class === "medio" || l.target.class === "medio" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 0 );
                    node.filter( function ( n ) {
                            if ( n.class === "medio" ) {
                                return n;
                            } else if ( n.class === "ciudadano" && n.vDeM === true && n.vDeC === undefined && n.vDeP === undefined ) {
                                return n;
                            } else if ( n.class === "politico" && n.vDeM === true && n.vDeC === undefined && n.vDeP === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 0 );
                    text.style( "opacity", 0 );
                    top10Labels = 0;
                } else if ( howManyNodes === 2 && d3.select( "#Medios" )
                    .property( "checked" ) === true && d3.select( "#Ciudadanos" )
                    .property( "checked" ) === true ) {
                    link.filter( function ( l ) {
                            if ( l.source.class === "politico" || l.target.class === "politico" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 0 );
                    node.filter( function ( n ) {
                            if ( n.class === "politico" ) {
                                return n;
                            } else if ( n.class === "ciudadano" && n.vDeP === true && n.vDeC === undefined && n.vDeM === undefined ) {
                                return n;
                            } else if ( n.class === "medio" && n.vDeP === true && n.vDeC === undefined && n.vDeM === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 0 );
                    text.style( "opacity", 0 );
                    top10Labels = 0;
                } else if ( howManyNodes === 1 && d3.select( "#Medios" )
                    .property( "checked" ) === true ) {
                    link.filter( function ( l ) {
                            if ( l.source.class === "medio" && l.target.class === "medio" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 1 );
                    link.filter( function ( l ) {
                            if ( l.source.class !== "medio" || l.target.class !== "medio" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 0 );
                    node.filter( function ( n ) {
                            if ( n.class === "medio" && n.vDeP === undefined && n.vDeC === undefined && n.vDeM === true ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 1 );
                    node.filter( function ( n ) {
                            if ( n.class !== "medio" ) {
                                return n;
                            } else if ( n.class === "medio" && n.vDeP === true && n.vDeC === true && n.vDeM === undefined ) {
                                return n;
                            } else if ( n.class === "medio" && n.vDeP === true && n.vDeC === undefined && n.vDeM === undefined ) {
                                return n;
                            } else if ( n.class === "medio" && n.vDeP === undefined && n.vDeC === true && n.vDeM === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 0 );
                    text.style( "opacity", 0 );
                    top10Labels = 0;
                } else if ( howManyNodes === 1 && d3.select( "#Politicos" )
                    .property( "checked" ) === true ) {
                    link.filter( function ( l ) {
                            if ( l.source.class === "politico" && l.target.class === "politico" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 1 );
                    link.filter( function ( l ) {
                            if ( l.source.class !== "politico" || l.target.class !== "politico" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 0 );
                    node.filter( function ( n ) {
                            if ( n.class === "politico" && n.vDeP === true && n.vDeC === undefined && n.vDeM === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 1 );
                    node.filter( function ( n ) {
                            if ( n.class !== "politico" ) {
                                return n;
                            } else if ( n.class === "politico" && n.vDeP === undefined && n.vDeC === true && n.vDeM === true ) {
                                return n;
                            } else if ( n.class === "politico" && n.vDeP === undefined && n.vDeC === undefined && n.vDeM === true ) {
                                return n;
                            } else if ( n.class === "politico" && n.vDeP === undefined && n.vDeC === true && n.vDeM === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 0 );
                    text.style( "opacity", 0 );
                    top10Labels = 0;
                } else if ( howManyNodes === 1 && d3.select( "#Ciudadanos" )
                    .property( "checked" ) === true ) {
                    link.filter( function ( l ) {
                            if ( l.source.class === "ciudadano" && l.target.class === "ciudadano" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 1 );
                    link.filter( function ( l ) {
                            if ( l.source.class !== "ciudadano" || l.target.class !== "ciudadano" ) {
                                return l;
                            }
                        } )
                        .style( "opacity", 0 );
                    node.filter( function ( n ) {
                            if ( n.class === "ciudadano" && n.vDeP === undefined && n.vDeC === true && n.vDeM === undefined ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 1 );
                    node.filter( function ( n ) {
                            if ( n.class !== "ciudadano" ) {
                                return n;
                            } else if ( n.class === "ciudadano" && n.vDeP === true && n.vDeC === undefined && n.vDeM === true ) {
                                return n;
                            } else if ( n.class === "ciudadano" && n.vDeP === true && n.vDeC === undefined && n.vDeM === undefined ) {
                                return n;
                            } else if ( n.class === "ciudadano" && n.vDeP === undefined && n.vDeC === undefined && n.vDeM === true ) {
                                return n;
                            }
                        } )
                        .style( "opacity", 0 );
                    text.style( "opacity", 0 );
                    top10Labels = 0;
                }
            } );
    }

    //Muestra los nodos ocultados con la función hidingNodes()
    d3.selectAll( "#selectorsNodes label" )
        .on( "mousedown", function ( d ) {
            if ( d3.select( "#Ciudadanos" )
                .property( "checked" === false && howManyNodes === 2 ) ) {
                link.filter( function ( l ) {
                        if ( l.source.class === "ciudadano" || l.target.class === "ciudadano" ) {
                            return l;
                        }
                    } )
                    .style( "opacity", 1 );
                node.style( "opacity", 1 );
            }
            if ( d3.select( "#Medios" )
                .property( "checked" === false && howManyNodes === 2 ) ) {
                link.filter( function ( l ) {
                        if ( l.source.class === "medio" || l.target.class === "medio" ) {
                            return l;
                        }
                    } )
                    .style( "opacity", 1 );
                node.style( "opacity", 1 );
            }
            if ( d3.select( "#Politicos" )
                .property( "checked" === false && howManyNodes === 2 ) ) {
                link.filter( function ( l ) {
                        if ( l.source.class === "politico" || l.target.class === "politico" ) {
                            return l;
                        }
                    } )
                    .style( "opacity", 1 );
                node.style( "opacity", 1 );
            }

        } );

    // Destaca vecinos cuando se da clic en un nodo
    var toggle = 0;

    function connectedNodes( d ) {
        if ( toggle === 0 ) {
            node.style( "opacity", function ( o ) {
                return neighboring( d, o ) | neighboring( o, d ) ? 1 : 0;
            } );
            link.style( "opacity", function ( o ) {
                return d.index === o.source.index | d.index === o.target.index ? 1 : 0;
            } );
            text.style( "opacity", 0 );
            linkLabel.style( "opacity", function ( o ) {
                return d.index === o.source.index | d.index === o.target.index ? 1 : 0;
            } );
            toggle = 1;
        } else {
            node.style( "opacity", 1 );
            link.style( "opacity", 1 );
            // text.style("opacity", 1);
            linkLabel.style( "opacity", 0 );
            toggle = 0;
        }
    }

    //Ejecuta la búsqueda de un nodo al hace clic en el botón Buscar
    d3.select( "#buscar" )
        .on( "click", function ( d ) {
            buscar();
        } );

    //Encuentra el nodo solicitado por el usuario y lo selecciona junto con su vecindario
    function buscar() {
        nodes.forEach( function ( d ) {
            var userInput = document.getElementById( "buscador" );
            var str1 = d.name,
                str2 = userInput.value;
            if ( str1.toLowerCase() === str2.toLowerCase() ) {
                connectedNodes( d );
            }
        } );
    }

    //Sugiere opciones a partir de lo escrito en el input de búsqueda
    $( function () {
        var tags = [];
        nodes.forEach( function ( d ) {
            tags.push( d.name );
            return tags;
        } );
        $( '#buscador' )
            .autocomplete( {
                source: tags
            } );
    } );

    // BOTON: Asigna el mismo tamaño a todos los nodos
    d3.select( "#tamanio" )
        .on( "click", function ( d ) {
            sameSize();
        } );
    var tamanio = 0;

    function sameSize() {
        if ( tamanio === 0 ) {
            nodes.forEach( function ( d ) {
                baseRadius = ( Math.sqrt( 1 / Math.PI ) ) * 5;
                d.radius = baseRadius;
            } );
            node.attr( "r", function ( n ) {
                return n.radius;
            } );
            link.attr( "d", function ( d ) {

                //Enlaces bidireccionales curvos, unidireccionales rectos
                diffX = d.target.x - d.source.x;
                diffY = d.target.y - d.source.y;

                // Length of path from center of source node to center of target node
                pathLength = Math.sqrt( ( diffX * diffX ) + ( diffY * diffY ) );

                // x and y distances from center to outside edge of target node
                if ( pathLength === 0 ) {
                    pathLength = 0.01;
                }

                offsetX = ( diffX * d.target.radius ) / pathLength;
                offsetY = ( diffY * d.target.radius ) / pathLength;

                dr = ( d.straight === 1 ) ? 0 : Math.sqrt( diffX * diffX + diffY * diffY ) * d.linknum;


                return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1" + ( d.target.x - offsetX ) + "," + ( d.target.y - offsetY );
            } );
            tamanio = 1;
        } else if ( tamanio = 1 && cambiaTamanio === 0 ) {
            nodes.forEach( function ( d ) {
                baseRadius = ( Math.sqrt( 1 / Math.PI ) ) * 5;
                baseNodeArea = Math.PI * ( baseRadius * baseRadius );
                if ( d.inDegree > 0 ) {
                    d.radius = Math.sqrt( ( baseNodeArea * ( d.inDegree * 1.7 ) ) / Math.PI );
                } else {
                    d.radius = baseRadius;
                }
            } );
            node.attr( "r", function ( n ) {
                return n.radius;
            } );
            link.attr( "d", function ( d ) {

                //Enlaces bidireccionales curvos, unidireccionales rectos
                diffX = d.target.x - d.source.x;
                diffY = d.target.y - d.source.y;

                // Length of path from center of source node to center of target node
                pathLength = Math.sqrt( ( diffX * diffX ) + ( diffY * diffY ) );

                // x and y distances from center to outside edge of target node
                if ( pathLength === 0 ) {
                    pathLength = 0.01;
                }

                offsetX = ( diffX * d.target.radius ) / pathLength;
                offsetY = ( diffY * d.target.radius ) / pathLength;

                dr = ( d.straight === 1 ) ? 0 : Math.sqrt( diffX * diffX + diffY * diffY ) * d.linknum;


                return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1" + ( d.target.x - offsetX ) + "," + ( d.target.y - offsetY );
            } );
            cambiaTamanio = 0;
            tamanio = 0;
        } else if ( tamanio = 1 && cambiaTamanio === 1 ) {
            nodes.forEach( function ( d ) {
                baseRadius = ( Math.sqrt( 1 / Math.PI ) ) * 5;
                baseNodeArea = Math.PI * ( baseRadius * baseRadius );
                if ( d.outDegree > 0 ) {
                    d.radius = Math.sqrt( ( baseNodeArea * ( d.outDegree * 1.7 ) ) / Math.PI );
                } else {
                    d.radius = baseRadius;
                }
            } );
            node.attr( "r", function ( n ) {
                return n.radius;
            } );
            link.attr( "d", function ( d ) {

                //Enlaces bidireccionales curvos, unidireccionales rectos
                diffX = d.target.x - d.source.x;
                diffY = d.target.y - d.source.y;

                // Length of path from center of source node to center of target node
                pathLength = Math.sqrt( ( diffX * diffX ) + ( diffY * diffY ) );

                // x and y distances from center to outside edge of target node
                if ( pathLength === 0 ) {
                    pathLength = 0.01;
                }

                offsetX = ( diffX * d.target.radius ) / pathLength;
                offsetY = ( diffY * d.target.radius ) / pathLength;

                dr = ( d.straight === 1 ) ? 0 : Math.sqrt( diffX * diffX + diffY * diffY ) * d.linknum;


                return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1" + ( d.target.x - offsetX ) + "," + ( d.target.y - offsetY );
            } );
            tamanio = 0;
        }
    }

    // BOTON: Cambia el fondo negro o blanco
    d3.select( "#background" )
        .on( "click", function ( d ) {
            changeBackground();
        } );

    var cambiaFondo = 0;

    function changeBackground() {
        if ( cambiaFondo === 0 ) {
            d3.select( "body" )
                .style( "background-color", "#F2F3F4" );
            marker.attr( "stroke", "#fff" )
                .attr( "fill", "#000" );
            linkLabel.attr( "class", "label2" );
            text.attr( "class", "text2" );
            cambiaFondo = 1;
        } else if ( cambiaFondo === 1 ) {
            d3.select( "body" )
                .style( "background-color", "#14141c" );
            marker.attr( "stroke", "#14141c" )
                .attr( "fill", "#F2F3F4" );
            linkLabel.attr( "class", "label" );
            text.attr( "class", "text" );
            cambiaFondo = 0;
        }
    }

    // BOTON: Muestra/oculta los nombres enlaces bidireccionales
    d3.select( "#bidirect" )
        .on( "click", function ( d ) {
            muestraEnlacesBi();
        } );
    var enlacesBi = 0;

    function muestraEnlacesBi() {
        if ( enlacesBi === 0 ) {
            link.style( "opacity", 0 );
            var linksCurvos = [];
            var linksBi = [];
            links.forEach( function ( l ) {
                if ( l.straight === 0 ) {
                    linksCurvos.push( l );
                }
            } );
            link.filter( function ( l ) {
                    for ( var i = 0; i < linksCurvos.length; i++ ) {
                        if ( l.source === linksCurvos[ i ].target && l.target === linksCurvos[ i ].source ) {
                            linksBi.push( l );
                            return l;
                        }
                    }
                } )
                .style( "opacity", 1 );
            node.style( "opacity", 0 );
            node.filter( function ( n ) {
                    for ( var i = 0; i < linksBi.length; i++ ) {
                        if ( n.name === linksBi[ i ].source.name || n.name === linksBi[ i ].target.name ) {
                            return n;
                        }
                    }
                } )
                .style( "opacity", 1 );
            enlacesBi = 1;
        } else if ( enlacesBi === 1 ) {
            link.style( "opacity", 1 );
            node.style( "opacity", 1 );
            enlacesBi = 0;
        }

    }

    // BOTON: Muestra/oculta los nombres del top10
    var top10Labels = 0;
    d3.select( "#et" )
        .on( "click", function ( d ) {
            if ( top10Labels === 0 && howManyNodes === 3 ) {
                // text.transition(350)
                text.style( "opacity", 1 );
                top10Labels = 1;
            } else if ( top10Labels === 1 ) {
                // text.transition(350)
                text.style( "opacity", 0 );
                top10Labels = 0;
            }
        } );

    // BOTON: Quita o devuelve los colores por categoría de todos los nodos
    var cambioColor = 0;
    d3.select( "#nc" )
        .on( "click", function ( d ) {
            if ( cambioColor === 0 ) {
                node.attr( "class", "node" );
                cambioColor = 1;
            } else if ( cambioColor === 1 ) {
                node.attr( "class", function ( d ) {
                    return d.class;
                } );
                cambioColor = 0;
            }
        } );

    // BOTON: Muestra/oculta todos los enlaces
    var cambio = 0;
    d3.select( "#enlaces2" )
        .on( "click", function ( d ) {
            if ( cambio === 0 && howMany === 3 ) {
                link.style( "opacity", 0 );
                cambio = 1;
                d3.selectAll( "#selectors input[type=checkbox]" )
                    .property( "checked", false );
                howMany = 0;
            } else if ( ( cambio === 1 && ( howMany === 0 | howMany === 3 ) ) ) {
                link.style( "opacity", 1 );
                node.style( "opacity", 1 );
                cambio = 0;
                d3.selectAll( "#selectors input[type=checkbox]" )
                    .property( "checked", true );
                howMany = 3;
            }
        } );

    function porcentaje( d, total ) {
        return ( ( d * 100 ) / total )
            .toFixed( 2 );
    }

} );