function sock = epconnect(port)


if ~exist('port', 'var') % If no value is given for port
    port = 28000; % Default to 28000
end

%% Establish socket
sock = tcpip('localhost', port, 'NetworkRole', 'client'); % Create tcpip object
sock.Timeout = 1; % Set it to time out if no response after 1s
fopen(sock); % Open connection

%% Get device ID
fprintf(sock, 'device_list localhost'); % Request device list
rawdev = fscanf(sock); % Receive device list
if contains(rawdev, 'Empatica_E4')
devices = split(rawdev, {'\n', ' '}); % Split device list at every new line or space
i = find(contains(devices, 'Empatica_E4')) - 1; % Find cell containing Empatica name and get the cell before it (i.e. its ID)
ID = devices{i}; % Isolate Empatica E4 device
elseif contains(rawdev, 'E4_')
    error('Device already connected and subscribed to streams.');
else
    error('Could not connect')
end
    
%% Connect
fprintf(sock, ['device_connect ' ID]); % Send connection request
outcome = fscanf(sock); % Receive response
if contains(outcome, 'device_connect OK') % If connection was successful...
    disp('Successfully connected to Empatica E4 device') % Report success
else % If connection was unsuccessful
    error(['Could not connect to Empatica E4 device, response received was: ' outcome]) % Report failure
end

