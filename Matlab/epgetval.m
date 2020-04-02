function val = epgetval(sock)
if strcmp(sock.Status, 'closed')
    error('Socket is closed. Use @epconnect to open socket.');
end
try
    raw = fscanf(sock); % Get data back from socket
    val = raw;
catch % If request fails...
    val = NaN; % Set value to NaN
    warning('Could not get value from sensor.') % Issue warning
end