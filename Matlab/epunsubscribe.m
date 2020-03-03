function msg = epunsubscribe(sock, varargin)

for s = varargin
    s = lower(s{:});
    fprintf(sock, ['device_subscribe ' s ' OFF']); % Send request to socket
    pause(0.1); % Protection from invalid loop
    msg.(s) = fscanf(sock); % Get data back from socket 
end