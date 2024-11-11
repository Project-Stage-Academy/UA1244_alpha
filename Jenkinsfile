pipeline {
    agent any

    environment {
        COMPOSE_FILE = 'docker/docker-compose.yml'
    }

    stages {
        // stage('Clean Up Old Containers and Images') {
        //     steps {
        //         script {
        //             sh 'sudo docker-compose -f $COMPOSE_FILE down'
        //             sh 'sudo docker rm -f $(sudo docker ps -aq) || true'
        //             sh 'sudo docker rmi -f $(sudo docker images -aq) || true'
        //         }
        //     }
        // }

        stage('Checkout') {
            steps {
                git branch: 'develop', url: 'https://github.com/Project-Stage-Academy/UA1244_alpha.git'
            }
        }
        stage('Debug') {
            steps {
                script {
                    sh 'ls -l /var'
                    sh 'ls -l /var/lib/jenkins/workspace/backend'
                }
            }
        }

        stage('Copy Env Files') {
            steps {
                script {
                    sh 'sudo touch /var/lib/jenkins/workspace/Forum/.env'
                    sh 'sudo cp /var/.env /var/lib/jenkins/workspace/Forum/.env'
                }
            }
        }

        stage('Build and Deploy') {
            steps {
                script {
                    sh 'sudo docker-compose -f $COMPOSE_FILE build'
                    sh 'sudo docker-compose -f $COMPOSE_FILE up -d'
                }
            }
        }
    }
}
