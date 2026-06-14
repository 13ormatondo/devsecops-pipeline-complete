pipeline {
    agent any

    environment {
        SONAR_HOST_URL = "http://sonarqube:9000"
        SONAR_AUTH_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQubeServer') {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=vulnerable-app \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.login=${SONAR_AUTH_TOKEN}
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("vulnerable-app:latest", "./vulnerable-app")
                }
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                    docker stop vulnerable-app || true
                    docker rm vulnerable-app || true
                    docker run -d --name vulnerable-app -p 5000:5000 vulnerable-app:latest
                    sleep 10
                '''
            }
        }

        stage('Initialize Database') {
            steps {
                sh 'curl -s http://localhost:5000/init-db'
                sleep 2
            }
        }

        stage('Postman API Security Tests') {
            steps {
                sh '''
                    docker run --network host -v $PWD/postman:/etc/newman \
                      postman/newman:latest run /etc/newman/collection.json || true
                '''
            }
        }

        stage('OWASP ZAP DAST Scan') {
            steps {
                sh '''
                    docker run --network host -v $PWD:/zap/wrk \
                      owasp/zap2docker-stable zap-api-scan.py \
                      -t http://localhost:5000/openapi.yaml \
                      -f openapi \
                      -r zap_report.html || true
                '''
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: false,
                    keepAll: false,
                    reportDir: '.',
                    reportFiles: 'zap_report.html',
                    reportName: 'OWASP ZAP Security Report'
                ])
            }
        }
    }

    post {
        always {
            sh '''
                docker stop vulnerable-app || true
                docker rm vulnerable-app || true
            '''
            cleanWs()
        }
    }
}
