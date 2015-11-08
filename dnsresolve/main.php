<?php
    if($_SERVER['HTTP_X_APPENGINE_INBOUND_APPID'] !== 'dnstwister') {
        header('Location:https://dnstwister.appspot.com');
    }
    else {

        $ip = null;

        try {
            // Grab the domain
            $domain = trim(substr($_GET['d'], 0, 255));

            // If we have a testable domain request passed in
            if (strlen($domain) > 0) {

                // Attempt a gethostbyname()
                $ip_str = substr(gethostbyname($domain), 0, 15);

                // Check we got an actual valid IP address
                if (filter_var($ip_str, FILTER_VALIDATE_IP) !== false) {
                    $ip = $ip_str;
                }
            }
        }
        catch (Exception $e)
        {
            //no-op
        }

        echo json_encode(array('ip'=>$ip));

    }
?>
