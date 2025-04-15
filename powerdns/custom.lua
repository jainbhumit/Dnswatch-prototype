function preresolve(dq)
    local clientIP = dq.remoteaddr:toString()
    local queryName = dq.qname:toString()
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    local action = "Allowed"
    local response = ""
    local queryType = "UNKNOWN"

    -- Safely get query type
    if dq and dq.qtype then
        queryType = tostring(dq.qtype)
    end

    -- Check if the requested domain is "example.com"
    if dq.qname:equal("example.com.") then
        dq:addAnswer(pdns.CNAME, "piyush.com.")
        action = "Blocked"
        response = "Redirected to piyush.com"
    end

    -- Create log message (JSON format recommended)
    local logMessage = string.format(
        '{"timestamp":"%s","client_ip":"%s","query":"%s","type":"%s","action":"%s","response":"%s"}',
        timestamp, clientIP, queryName, queryType, action, response
    )

    -- Option 1: Use built-in pdnslog (recommended)
    pdnslog(logMessage, pdns.loglevels.Info)

    if queryName ~= "." then
        local socket_ok, socket = pcall(require, "socket")
        if socket_ok then
            local tcp = socket.tcp()
            tcp:settimeout(2) -- 100ms timeout
            local ok, err = tcp:connect("127.0.0.1", 5170)
            if ok then
                tcp:send(logMessage .. "\n")
                tcp:close()
            else
                pdnslog("TCP log failed: " .. err, pdns.loglevels.Warning)
            end
        end
    end
 
    return action == "Blocked"
end
