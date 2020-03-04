function msg = epsubscribe(sock, varargin)
for s = varargin
    s = lower(s{:}); % Convert to lowercase
    fprintf(sock, ['device_subscribe ' s ' ON\r']); % Send request to socket
    msg.(s) = fscanf(sock); % Get data back from socket
    if contains(msg.(s), 'device_subscribe') && contains(msg.(s), 'OK') % If successsful
        disp(['Successfully subscribed to ' s]) % Notify user
    else % If unsuccessful
        warning(['Unable to subscribe to ' s]) % Notify user
    end    
end