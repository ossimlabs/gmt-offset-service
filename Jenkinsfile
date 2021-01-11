properties([
    parameters ([
        string(name: 'BUILD_NODE', defaultValue: 'POD_LABEL', description: 'The build node to run on'),
        booleanParam(name: 'CLEAN_WORKSPACE', defaultValue: true, description: 'Clean the workspace at the end of the run'),
        string(name: 'DOCKER_REGISTRY_DOWNLOAD_URL', defaultValue: 'nexus-docker-private-group.ossim.io', description: 'Repository of docker images')
    ]),
    pipelineTriggers([
            [$class: "GitHubPushTrigger"]
    ]),
    [$class: 'GithubProjectProperty', displayName: '', projectUrlStr: 'https://github.com/ossimlabs/gmt-offset-service'],
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '3', daysToKeepStr: '', numToKeepStr: '20')),
    disableConcurrentBuilds()
])
podTemplate(
  containers: [
    containerTemplate(
      name: 'docker',
      image: 'docker:19.03.11',
      ttyEnabled: true,
      command: 'cat',
      privileged: true
    ),
      containerTemplate(
      image: "${DOCKER_REGISTRY_DOWNLOAD_URL}/omar-builder:1.0.0",
      name: 'builder',
      command: 'cat',
      ttyEnabled: true
    ),
    containerTemplate(
      image: "${DOCKER_REGISTRY_DOWNLOAD_URL}/alpine/helm:3.2.3",
      name: 'helm',
      command: 'cat',
      ttyEnabled: true
    ),
    containerTemplate(
      image: "${DOCKER_REGISTRY_DOWNLOAD_URL}/centos:8",
      name: 'curl',
      command: 'cat',
      ttyEnabled: true
    ),
      containerTemplate(
      image: "${DOCKER_REGISTRY_DOWNLOAD_URL}/kubectl-aws-helm:latest",
      name: 'kubectl-aws-helm',
      command: 'cat',
      ttyEnabled: true,
      alwaysPullImage: true
    )
  ],
  volumes: [
    hostPathVolume(
      hostPath: '/var/run/docker.sock',
      mountPath: '/var/run/docker.sock'
    )
  ]
)
{
node(POD_LABEL){

    stage("Checkout branch")
    {
        scmVars = checkout(scm)
        GIT_BRANCH_NAME = scmVars.GIT_BRANCH
        BRANCH_NAME = """${sh(returnStdout: true, script: "echo ${GIT_BRANCH_NAME} | awk -F'/' '{print \$2}'").trim()}"""
        
//        sh """
//        touch buildVersion.txt
//        grep buildVersion gradle.properties | cut -d "=" -f2 > "buildVersion.txt"
//           """
        
        preVERSION = readFile "BuildVersion.txt"
        VERSION = preVERSION.substring(0, preVERSION.indexOf('\n'))

        GIT_TAG_NAME = "gmt-offset-service" + "-" + VERSION
        ARTIFACT_NAME = "ArtifactName"

        script 
        {
          if (BRANCH_NAME != 'master') 
          {
            buildName "${VERSION} - ${BRANCH_NAME}-SNAPSHOT"
          } else 
          {
            buildName "${VERSION} - ${BRANCH_NAME}"
          }
        }
      }

    stage("Load Variables")
    {
      withCredentials([string(credentialsId: 'o2-artifact-project', variable: 'o2ArtifactProject')]) {
        step ([$class: "CopyArtifact",
          projectName: o2ArtifactProject,
          filter: "common-variables.groovy",
          flatten: true])
        }
        load "common-variables.groovy"
    }

    stage('Docker build') {
      container('docker') {
        withDockerRegistry(credentialsId: 'dockerCredentials', url: "https://${DOCKER_REGISTRY_DOWNLOAD_URL}") {
          sh """
            docker build --network=host -t "${DOCKER_REGISTRY_PUBLIC_UPLOAD_URL}"/gmt-offset-service:${BRANCH_NAME} .
          """
        }
      }
    }

    stage('Docker push'){
      container('docker') {
        withDockerRegistry(credentialsId: 'dockerCredentials', url: "https://${DOCKER_REGISTRY_PUBLIC_UPLOAD_URL}") {
        sh """
            docker push "${DOCKER_REGISTRY_PUBLIC_UPLOAD_URL}"/gmt-offset-service:${BRANCH_NAME}
        """
        }
      }
    }

    stage('Package chart'){
      container('helm') {
        sh """
            mkdir packaged-chart
            helm package -d packaged-chart chart
          """
      }
    }

    stage('Upload chart'){
      container('builder') {
        withCredentials([usernameColonPassword(credentialsId: 'helmCredentials', variable: 'HELM_CREDENTIALS')]) {
          sh "curl -u ${HELM_CREDENTIALS} ${HELM_UPLOAD_URL} --upload-file packaged-chart/*.tgz -v"
        }
      }
    }
    
    stage('New Deploy'){
        container('kubectl-aws-helm') {
            withAWS(
            credentials: 'Jenkins-AWS-IAM',
            region: 'us-east-1'){
                if (BRANCH_NAME == 'master'){
                    //insert future instructions here
                }
                else if (BRANCH_NAME == 'dev') {
                    sh "aws eks --region us-east-1 update-kubeconfig --name gsp-dev-v2 --alias dev"
                    sh "kubectl config set-context dev --namespace=omar-dev"
                    sh "kubectl rollout restart deployment/gmt-offset-service"   
                }
                else {
                    sh "echo Not deploying ${BRANCH_NAME} branch"
                }
            }
        }
    }

    stage("Clean Workspace")
    {
        if ("${CLEAN_WORKSPACE}" == "true")
            step([$class: 'WsCleanup'])
    }
}
}
