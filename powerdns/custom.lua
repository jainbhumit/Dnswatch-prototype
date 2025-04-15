local redis = require 'redis'

-- Redis and FluentBit connection clients
local tcp = nil
local client = nil

-- Connect to FluentBit TCP logging
function make_tcp_connection()
    local socket_ok, socket = pcall(require, "socket")
    if not socket_ok then
        pdnslog("Failed to load socket module", pdns.loglevels.Warning)
        return
    end

    tcp = socket.tcp()
    tcp:settimeout(5)

    local ok, err = tcp:connect("127.0.0.1", 5170)
    if not ok then
        pdnslog("Failed to connect to FluentBit TCP: " .. tostring(err), pdns.loglevels.Warning)
        tcp = nil
    end
end

function send_fluentbit_log(log_message)
    local retries = 3
    while tcp == nil and retries > 0 do
        make_tcp_connection()
        retries = retries - 1
    end

    if tcp then
        tcp:send(log_message .. "\n")
    else
        pdnslog("Failed to log to FluentBit after retries", pdns.loglevels.Warning)
    end
end

-- Redis connection
function make_redis_connection()
    local ok, rclient = pcall(redis.connect, 'clustercfg.bhumit-dns-db.9plkke.memorydb.ap-south-1.amazonaws.com', 6379, 2, true)
    if not ok then
        pdnslog("Redis connection failed", pdns.loglevels.Warning)
        return
    end

    client = rclient
end

-- Normalize domain format (add dot if missing)
local function normalize_domain(domain)
    if not domain:match("%.$") then
        return domain .. "."
    end
    return domain
end

-- Query Redis for domain block decision
function get_domain_action(domain_name)
    if client == nil then
        make_redis_connection()
    end

    if client == nil then
        pdnslog("Redis client not available", pdns.loglevels.Warning)
        return "allow"
    end

    local ok, value = pcall(client.get, client, domain_name)
    if ok and value then
        return value
    else
        return "allow"
    end
end

-- Main DNS hook
function preresolve(dq)
    local clientIP = dq.remoteaddr:toString()
    local queryName = dq.qname:toString()
    local queryType = tostring(dq.qtype)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")

    local domain = normalize_domain(queryName)
    local domain_action = get_domain_action(domain)

    local action = "allow"

    if domain_action ~= "allow" then
        dq:addAnswer(pdns.CNAME, domain_action)
        action = "block"
    end

    local logMessage = string.format(
        '{"timestamp":"%s","client_ip":"%s","query":"%s","type":"%s","action":"%s"}',
        timestamp, clientIP, queryName, queryType, action
    )

    pdnslog(logMessage, pdns.loglevels.Info)
    send_fluentbit_log(logMessage)

    return action == "block"
end
