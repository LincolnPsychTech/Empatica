function msg = epsubscribe(sock, varargin)
for s = varargin
    s = lower(s{:});
    fprintf(sock, ['device_subscribe ' s ' ON\r']); % Send request to socket
    msg.(s) = fscanf(sock); % Get data back from socket
    if contains(msg.(s), 'device_subscribe') && contains(msg.(s), 'OK')
        disp(['Successfully subscribed to ' s])
    else
        warning(['Unable to subscribe to ' s])
    end    
end