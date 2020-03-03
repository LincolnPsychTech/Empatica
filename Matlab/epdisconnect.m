function outcome = epdisconnect(sock)

fprintf(sock, 'device_list localhost'); % Request device list
rawdev = fscanf(sock); % Receive device list
if contains(rawdev, 'Empatica_E4')
    devices = split(rawdev, {'\n', ' '}); % Split device list at every new line or space
    i = find(contains(devices, 'Empatica_E4')) - 1; % Find cell containing Empatica name and get the cell before it (i.e. its ID)
    ID = devices{i}; % Isolate Empatica E4 device
    fprintf(sock, ['device_disconnect ' ID]); % Send disconnection request
    outcome = fscanf(sock); % Receive response
    if contains(outcome, 'device_disconnect OK') % If connection was successful...
        disp('Successfully disconnected from to Empatica E4 device') % Report success
    else % If connection was unsuccessful
        error(['Could not disconnect from Empatica E4 device, response received was: ' outcome]) % Report failure
    end
elseif contains(rawdev, 'E4_')
    epunsubscribe(sock, 'acc', 'bvp', 'gsr', 'ibi', 'tmp', 'tag')
    disp('Device was still subscribed to feeds. Device has now been unsubscribed, please try disconnecting again.');
else
    error(['Could not disconnect device, data received: ' rawdev]);
end



