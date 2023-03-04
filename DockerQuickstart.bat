docker stop bing-rewards
docker rm bing-rewards
REM Enter YOUR path to the Bing rewards folder. Example:
cd C:\Users\premium\Downloads\BingRewards-main
docker build -t bing-rewards .
docker run -itd --env-file ./.env --restart unless-stopped --name bing-rewards bing-rewards
REM Warning: This will remove all dangling images. If you have other images that are not in use, they will be removed. Remove REM to run.
REM docker image prune -f --filter "dangling=true"