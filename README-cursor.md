# SP33D C0D3R 🚀

A competitive coding platform that measures and tracks your coding speed while solving algorithmic challenges. Race against the clock, track your performance, and compete with others in real-time coding challenges.

## 🎯 What is SP33D C0D3R?

SP33D C0D3R is a web-based coding competition platform that:

- **Measures coding speed** - Tracks time from challenge start to successful completion
- **Provides real-time feedback** - Run tests instantly and see results immediately
- **Tracks assistance usage** - Monitors copy-paste events and character counts
- **Supports multiple challenges** - Currently includes FizzBuzz and Two Sum challenges
- **Secure execution** - Runs code in isolated Docker containers with resource limits

## 🏗️ Architecture

The project consists of several components:

- **Frontend**: Next.js web application with Monaco Editor for code editing
- **Backend API**: FastAPI service for managing users, runs, and challenge execution
- **Database**: PostgreSQL for storing user data, run results, and performance metrics
- **Code Runner**: Docker-based Python execution environment with security constraints
- **Challenges**: Algorithmic problems with test suites and starter code

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SP33D-C0D3R
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Web UI: http://localhost:3000
   - API: http://localhost:8000
   - Database: localhost:5432

## 🎮 How to Use

### Starting a Challenge

1. Navigate to a challenge (e.g., `/challenge/fizzbuzz`)
2. The timer starts automatically when you begin
3. Write your solution in the Monaco code editor
4. Click "Run tests" to execute your code
5. View test results and logs in real-time
6. Complete the challenge to see your final time!

### Available Challenges

#### FizzBuzz
Write a function that returns a list from 1 to n where:
- Multiples of 3 are replaced with "Fizz"
- Multiples of 5 are replaced with "Buzz"
- Multiples of both are replaced with "FizzBuzz"
- Other numbers remain as integers

#### Two Sum
Given a list of integers and a target sum, return the indices of two numbers that add up to the target. Return indices in ascending order.

## 🔧 Development

### Project Structure

```
SP33D-C0D3R/
├── api/                 # FastAPI backend service
├── challenges/          # Coding challenge definitions
├── infra/              # Database initialization
├── runner/             # Code execution environment
├── web/                # Next.js frontend application
└── docker-compose.yml  # Service orchestration
```

### Adding New Challenges

1. Create a new directory in `challenges/`
2. Add a `manifest.yaml` file with challenge metadata
3. Create a `prompt.md` with the problem description
4. Provide `starter.py` with initial code template
5. Add test files in `tests_public/` and `tests_hidden/`

### Local Development

```bash
# Start only specific services
docker-compose up db api

# View logs
docker-compose logs -f api

# Rebuild services
docker-compose build web
```

## 🛡️ Security Features

- **Container isolation**: Code runs in isolated Docker containers
- **Resource limits**: 512MB memory limit per execution
- **Network disabled**: Containers cannot access external networks
- **Read-only mounts**: Challenge files are mounted as read-only

## 📊 Performance Tracking

The platform tracks various metrics:
- **Completion time**: From start to successful test pass
- **Attempt count**: Number of test runs
- **Assistance usage**: Copy-paste events and character counts
- **Code execution logs**: Test results and error messages

## 🐛 Troubleshooting

### Common Issues

**Service won't start**: Ensure Docker is running and ports 3000, 8000, and 5432 are available

**Database connection errors**: Wait for PostgreSQL to fully initialize, or restart the db service

**Code execution fails**: Check that the runner container built successfully and Docker socket is accessible

### Logs and Debugging

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs api

# Access database directly
docker-compose exec db psql -U speed -d speed
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the terms specified in the LICENSE file.

## 🚀 Future Enhancements

- [ ] Support for multiple programming languages
- [ ] Leaderboards and rankings
- [ ] Custom challenge creation
- [ ] Real-time multiplayer competitions
- [ ] Performance analytics dashboard
- [ ] Code quality metrics

---

**Happy coding and may the fastest coder win!** ⚡ 