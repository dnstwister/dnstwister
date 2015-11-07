<?php
    header('Content-type:application/json;charset=utf-8');
    // Grab the ip as a string (max 15 chars).
    $ip = substr(gethostbyname($_GET['domain']), 0, 15);
    echo json_encode(array('ip'=>$ip));
?>
