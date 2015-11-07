<?php
    if($_SERVER['HTTP_X_APPENGINE_INBOUND_APPID'] != 'dnstwister') {
        header('Location:https://dnstwister.appspot.com');
    }
    else {
        // Grab the ip as a string (max 15 chars).
        $ip = substr(gethostbyname($_GET['domain']), 0, 15);
        header('Content-type:application/json;charset=utf-8');
        echo json_encode(array('ip'=>$ip));
    }
?>
