pipeline {
    agent any
    environment { COMPOSE_PROJECT_NAME = 'oaps' }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Validate') {
            steps { sh 'docker compose config -q' }
        }
        stage('Build') {
            steps { sh 'docker compose build app' }
        }
        stage('Deploy') {
            steps { sh 'docker compose up -d' }
        }
        stage('Smoke test') {
            steps {
                sh """
                  for i in \$(seq 1 30); do
                    if curl -fsS http://localhost:\${APP_HOST_PORT:-8081}/health; then exit 0; fi
                    sleep 2
                  done
                  docker compose logs
                  exit 1
                """
            }
        }
    }
    post { always { sh 'docker compose ps' } }
}
