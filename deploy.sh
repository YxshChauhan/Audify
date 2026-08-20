#!/bin/bash
SERVICE=$1

if [ "$SERVICE" == "upload" ]; then
  echo "Building upload-service..."
  docker buildx build \
    --platform linux/amd64 \
    --no-cache \
    -t mpxupd/upload-service:latest \
    --push \
    app/upload-service/

  echo "Restarting pod on server..."
  ssh -i ~/.ssh/converter-key ubuntu@3.236.97.86 \
    "sudo k3s kubectl rollout restart deployment upload-service -n converter && sudo k3s kubectl rollout status deployment upload-service -n converter"

elif [ "$SERVICE" == "converter" ]; then
  echo "Building converter-service..."
  docker buildx build \
    --platform linux/amd64 \
    --no-cache \
    -t mpxupd/converter-service:latest \
    --push \
    app/converter-service/

  echo "Restarting pod on server..."
  ssh -i ~/.ssh/converter-key ubuntu@3.236.97.86 \
    "sudo k3s kubectl rollout restart deployment converter-service -n converter && sudo k3s kubectl rollout status deployment converter-service -n converter"

elif [ "$SERVICE" == "all" ]; then
  echo "Building both services..."
  docker buildx build \
    --platform linux/amd64 \
    --no-cache \
    -t mpxupd/upload-service:latest \
    --push \
    app/upload-service/

  docker buildx build \
    --platform linux/amd64 \
    --no-cache \
    -t mpxupd/converter-service:latest \
    --push \
    app/converter-service/

  echo "Restarting all pods on server..."
  ssh -i ~/.ssh/converter-key ubuntu@3.236.97.86 \
    "sudo k3s kubectl rollout restart deployment upload-service converter-service -n converter"

else
  echo "Usage:"
  echo "  ./deploy.sh upload      <- when you change Flask UI"
  echo "  ./deploy.sh converter   <- when you change worker.py"
  echo "  ./deploy.sh all         <- rebuild everything"
fi

echo ""
echo "Done! App live at http://3.236.97.86"
