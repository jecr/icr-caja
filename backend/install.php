<?php

ini_set('max_execution_time', 0);
exec('python -m textblob.download_corpora > install.log');

?>