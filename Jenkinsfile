properties([
    parameters ([
        string(name: 'BUILD_NODE', defaultValue: 'omar-build', description: 'The build node to run on'),
        booleanParam(name: 'CLEAN_WORKSPACE', defaultValue: true, description: 'Clean the workspace at the end of the run')
    ]),
    pipelineTriggers([
            [$class: "GitHubPushTrigger"]
    ]),
    [$class: 'GithubProjectProperty', displayName: '', projectUrlStr: 'https://github.com/ossimlabs/gmt-offset-service'],
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '3', daysToKeepStr: '', numToKeepStr: '20')),
    disableConcurrentBuilds()
])

node("${BUILD_NODE}"){

    stage("Checkout branch $BRANCH_NAME")
    {
        checkout(scm)
    }
    
    stage ("Build Docker App")
    {
        withCredentials([[$class: 'UsernamePasswordMultiBinding',
                        credentialsId: 'dockerCredentials',
                        usernameVariable: 'DOCKER_REGISTRY_USERNAME',
                        passwordVariable: 'DOCKER_REGISTRY_PASSWORD']])
        {
            // Run all tasks on the app. This includes pushing to OpenShift and S3.
            sh """
            docker build ${DOCKER_REGISTRY_PUBLIC_UPLOAD_URL}/omar-timeserver
            """
        }
    }

    stage ("Publish Docker App")
    {
        withCredentials([[$class: 'UsernamePasswordMultiBinding',
                        credentialsId: 'dockerCredentials',
                        usernameVariable: 'DOCKER_REGISTRY_USERNAME',
                        passwordVariable: 'DOCKER_REGISTRY_PASSWORD']])
        {
            // Run all tasks on the app. This includes pushing to OpenShift and S3.
            sh """
            docker push ${DOCKER_REGISTRY_PUBLIC_UPLOAD_URL}/omar-timeserver
            """
        }
    }
    
    try {
        stage ("OpenShift Tag Image")
        {
            withCredentials([[$class: 'UsernamePasswordMultiBinding',
                            credentialsId: 'openshiftCredentials',
                            usernameVariable: 'OPENSHIFT_USERNAME',
                            passwordVariable: 'OPENSHIFT_PASSWORD']])
            {
                // Run all tasks on the app. This includes pushing to OpenShift and S3.
                sh """
                    ./gradlew openshiftTagImage \
                        -PossimMavenProxy=${MAVEN_DOWNLOAD_URL}
                """
            }
        }
    } catch (e) {
        echo e.toString()
    }

    stage("Clean Workspace")
    {
        if ("${CLEAN_WORKSPACE}" == "true")
            step([$class: 'WsCleanup'])
    }
}
