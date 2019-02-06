# snapshotalyzer-30000
Demo project to manage EC2 instances

##About
This project is a demo and uses BOTO3 to manage EC2 instances

##Configuring
shotty uses the configuraion file created by the AWS cli

`aws confiture --profile shotty`

##Running

`pipenv run python shotty/shotty.py <command> <--project=Project>`

*command* is instances, volumes or list_snapshots
*subcommand* - depends on command
*project* is optional
