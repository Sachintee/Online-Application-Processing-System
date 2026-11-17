# Online Application Processing System (OAPS)
## Docker + Docker Compose + Jenkins CI/CD

A local deployment simulation with a Flask REST API and PostgreSQL database.
Docker packages the API; Compose creates the services, network, dependency order,
and persistent volume; Jenkins automates validation, build, deployment, and smoke test.

### Components and dependencies
| Component | Purpose | Dependency |
|---|---|---|
| Flask API (`app`) | Submit, list, update applications | PostgreSQL |
| PostgreSQL (`db`) | Persistent application records | Docker volume |
| Docker Engine | Builds and runs containers | Host OS |
| Docker Compose | Orchestrates app and DB | Docker Engine |
| Jenkins | CI/CD automation | Git, Docker CLI, Compose, curl |

### Environment variables
| Variable | Purpose | Example |
|---|---|---|
| POSTGRES_DB | Database name | applications |
| POSTGRES_USER | Database user | appuser |
| POSTGRES_PASSWORD | Database password | Set your own secret |
| DB_HOST | API database hostname | db |
| DB_PORT | Database port | 5432 |
| APP_PORT | API container port | 8000 |
| APP_HOST_PORT | Host published port | 8081 |

### Local repeatable deployment
Prerequisite: Docker Engine/Desktop and Docker Compose plugin.

PowerShell:
```powershell
Copy-Item .env.example .env
# Edit .env and replace POSTGRES_PASSWORD
docker compose config
docker compose up -d --build
docker compose ps
```

Linux/macOS:
```bash
cp .env.example .env
# Edit .env and replace POSTGRES_PASSWORD
docker compose config
docker compose up -d --build
docker compose ps
```

Open http://localhost:8081/health. Port 8081 is used to avoid a common Jenkins
port 8080 conflict.

### Demonstrate the API
```bash
curl http://localhost:8081/health

curl -X POST http://localhost:8081/api/applications \
  -H "Content-Type: application/json" \
  -d '{"applicant_name":"Aarav Sharma","email":"aarav@example.com","program":"MCA"}'

curl http://localhost:8081/api/applications

curl -X PATCH http://localhost:8081/api/applications/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"UNDER_REVIEW"}'
```

### CI/CD using Jenkins
The included `Jenkinsfile` checks out source, validates Compose configuration,
builds the image, deploys with Compose, then calls `/health` as a smoke test.
Create a Jenkins Pipeline job pointing to this repository and use “Pipeline script
from SCM”. The Jenkins agent needs Git, Docker CLI, Docker Compose plugin, curl,
and permission to access the Docker daemon.

### Useful commands
```bash
docker compose logs -f
docker compose ps
docker compose restart app
docker compose down
docker compose down -v  # Deletes database volume and its data
```

### Production hardening
This is a lab-ready local simulation, not a hardened public production service.
Before internet exposure, add HTTPS/reverse proxy, authentication/authorization,
rate limiting, backups, monitoring, database migrations, secrets management,
and a restricted database account/network. Do not commit `.env` to Git.
