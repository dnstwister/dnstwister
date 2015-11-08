<?php
    if($_SERVER['HTTP_X_APPENGINE_INBOUND_APPID'] !== 'dnstwister') {
        header('Location:https://dnstwister.appspot.com');
    }
    else {

        $ip = null;

        try {
            // Grab the domain
            $domain = trim(substr($_GET['domain'], 0, 255));

            // If we have a testable domain passed in
            if (strlen($domain) > 0) {

                // Attempt a gethostbyname()
                $ip_str = substr(gethostbyname($_GET['domain']), 0, 15);

                // Check we got an actual valid IP address
                if (filter_var($ip_str, FILTER_VALIDATE_IP, FILTER_VALID_IPV4) !== false) {
                    $ip = $ip_str;
                }
            }
            else {
                echo 'invalid url';
            }
        }
        catch (Exception $e)
        {
            //no-op
        }

        echo json_encode(array('ip'=>$ip));

    }
?>
