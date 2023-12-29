# What is this?
A framework for building [multi-user dungeons](https://en.wikipedia.org/wiki/Multi-user_dungeon). It currently handles:
- client connections
- global events
- command parsing
- data persistence

# Getting Started
## Requirements
- docker
- docker-compose

```
# Add user to docker group
~/PyMUD$: sudo gpasswd -a $USER docker

# Start the dev environment
~/PyMUD$: make dev

# Connect
~/PyMUD$: telnet localhost 5000
```

# Future Work
- Finish validation of targetting
- Fix room descriptions
- Build commands
- Containers
- Character Creation & Authentication
- Character advancement plugins
- Combat system plugins
