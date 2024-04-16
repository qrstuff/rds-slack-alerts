# rds-slack-alerts

CloudFormation template for creating the AWS components for [Slack](https://slack.com/) notifications for [RDS Monitoring Alarms](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/creating_alarms.html)

It also contains a lambda function to add the top queries to the message thread from a five minute window when the alarm is triggered.

## Usage

#### Prerequisites:

1. [Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) AWS CLI.

2. Create [Slack app](https://api.slack.com/start/quickstart#creating).

3. Add the following [scopes](https://api.slack.com/start/quickstart#scopes) for bot token OAuth.
```
channels:read
chat:write
chat:write.customize
```

4. [Install and authorize](https://api.slack.com/start/quickstart#installing) the app for the workspace.

5. Create S3 bucket to store the packaged code used in deployment of Lambda functions.

#### Template Deployment:

The cloudformation template can be deployed directly using cli. Two steps are required: packaging the template to upload the lambda function code and creating the stack.

```shell
aws cloudformation package --template-file ./template.yml --s3-bucket <bucket-name> --output-template-file out.yml

aws cloudformation create-stack --stack-name <stack-name> --template-body file://out.yml \
--parameters \
ParameterKey=ProjectName,ParameterValue=<stack-name> \
ParameterKey=SlackOAuthToken,ParameterValue=<slack-bot-oauth-token> \
ParameterKey=ChannelId,ParameterValue=<slack-channel-id> \
ParameterKey=DbName,ParameterValue=<rds-instance-name> \
--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
```

#### Available Parameters

Following parameters are available for customization. Defaults can be set in the template, and can be overridden via cli as mentioned in the [Template Deployment](#Template-Deployment).

```yaml
  ChannelId:
    Type: String
    Description: Channel ID of the slack channel
  DbName:
    Type: String
    Description: Database Name for the RDS database
  EvaluationPeriod:
    Type: String
    Description: Evaluation period for the RDS alerts
    Default: 60
  FunctionName:
    Type: String
    Description: Function name for lambda function
    Default: rds-slack-notifications
  MaxResults:
    Type: String
    Description: No of results in top queries notification
    Default: 5
  MetricName:
    Type: String
    Description: Metric to be monitored
    Default: CPUUtilization
  ProjectName:
    Type: String
    Description: Project name or app name.
    Default: rds-slack-notification
  SlackOAuthToken:
    Type: String
    Description: OAuth Token for API request to slack
```


## License

See the [LICENSE](LICENSE) file.

## Notes

From the team at [QRStuff](https://qrstuff.com/) with ❤️ for automation with [Cloudformation](https://aws.amazon.com/cloudformation/).