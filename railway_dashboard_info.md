# Railway Dashboard Information

## Project Details
- **Project Name**: tools-project-fresh
- **Project ID**: 0c0d7d31-f7d5-4466-9317-b85c480a0d1b
- **Service Name**: service-1751757808943
- **Service ID**: fda9fdad-3f6b-484b-8163-00e3ed4c70d8
- **Environment**: production (95702724-51d3-4bde-b23e-cf27c0ebd13d)

## Dashboard URLs
- **Project Dashboard**: https://railway.app/project/0c0d7d31-f7d5-4466-9317-b85c480a0d1b
- **Service Dashboard**: https://railway.app/project/0c0d7d31-f7d5-4466-9317-b85c480a0d1b/service/fda9fdad-3f6b-484b-8163-00e3ed4c70d8
- **Deployments Page**: https://railway.app/project/0c0d7d31-f7d5-4466-9317-b85c480a0d1b/service/fda9fdad-3f6b-484b-8163-00e3ed4c70d8/deployments

## Current Issue
Railway is stuck deploying commit `2620cd6` instead of the latest commit `8316bdc` (and previous commits including thermal printer support).

## Commits Not Deployed
1. 8316bdc - Force Railway deployment - thermal printer support
2. 54ed643 - Add version endpoint to verify deployment
3. c852bc0 - FORCE DEPLOY: Candle testing system ready
4. b7d4e52 - Update candle labels for thermal printer roll
5. 06f12a2 - Fix wick validation with better error messages

## Manual Steps Needed
1. Go to the Railway dashboard
2. Navigate to the service deployments page
3. Check GitHub integration settings
4. Manually trigger deployment from latest commit
5. Or disconnect/reconnect GitHub repository