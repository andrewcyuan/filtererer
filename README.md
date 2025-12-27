# System Level Network Filtering

I kept on getting distracted while working so I made a system level filter for distracting websites. It runs automatically upon startup using a macOS LaunchDaemon.

## Copies folder
the plist is in `/Library/LaunchDaemons` folder.

## Gotchas

* Add mitmdump .pem certificate to system keychain
* chmod +x on every .sh script
* python and mitmdump are not accessible to the LaunchDaemon, but root access is needed to change network settings, so run the network setting commands in the Daemon, then call a script as user to use mitmdump and python.