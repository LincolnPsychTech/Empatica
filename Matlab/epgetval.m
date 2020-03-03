function val = epgetval(sock)
if strcmp(sock.Status, 'closed')
    error('Socket is closed. Use @epconnect to open socket.');
end
try
    raw = fscanf(sock); % Get data back from socket
    
    
    parsed = jsondecode(raw); % Parse json data to a structure
    val = parsed.values.frame; % Remove extraneous layers
    val.timestamp = datetime(val.timestamp); % Convert timestamps to datetime format
catch % If request fails...
    val = NaN; % Set value to NaN
    warning('Could not get value from sensor.') % Issue warning
end