mvn -U clean install -DskipTests
docker build --no-cache -t my-java-competitor:0.0.2 .
