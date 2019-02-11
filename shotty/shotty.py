import boto3
import botocore
import click

session= boto3.Session(profile_name='shotty')
ec2=session.resource('ec2')

def filter_instances(project):
    instances=[]

    if project:
        filters=[{'Name':'tag:Project','Values':[project]}]
        instances=ec2.instances.filter(Filters=filters)
    else:
        instances=ec2.instances.all()
    return instances

def has_pending_snapshot(volume):
    snapshots=list(volume.snapshots.all())
    return snapshots and snapshots[0].state=='pending'

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('volumes')
def volumes():
    """Commands for volumes"""
@volumes.command('list')
@click.option('--project', default=None,
    help='Only volumes for project(tag Project: <name>)')

def list_volumes(project):
    "list Ec2 Volumes"
    volumes=[]
    instances= filter_instances(project)

    for i in instances:
        volumes=i.volumes.all()
        for v in volumes:
            print(", ". join((
            v.id,
            i.id,
            v.state,
            str(v.size)+ "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))


    return

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""
@snapshots.command('list')
@click.option('--project', default=None,
    help='Only snapshots for project(tag Project: <name>)')
@click.option('--all','list_all',default=False, is_flag=True,
    help="List all snaphots for each volume, not just the most recent one")

def list_snapshots(project, list_all):
    "list EC2 Volume's snapshots"

    instances= filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ". join((
                s.id,
                v.id,
                i.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))
                if s.state == 'completed' and not list_all:break


    return


@cli.group('instances')
def instance():
    """Commands for instances"""
@instance.command('snapshot', help="Only instances for project(tag Project:<name>)")
@click.option('--project', default=None,
    help='Only instances for project(tag Project: <name>)')
def create_snapshots(project):
    "Create snapshots for Ec2 instances"

    instances= filter_instances(project)

    for i in instances:
        print("Stopping {0}".format(i.id))

        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("Skipping snapshot of {0}. ". format(v.id) )
                continue
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapshotalyzer 30000")

        print("Starting {0}".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's done !")

    return

@instance.command('list')
@click.option('--project', default=None,
    help='Only instances for project(tag Project: <name>)')
def list_instances(project):
    "List EC2 instances"

    instances= filter_instances(project)

    for i in instances:
        tags={ t['Key']: t['Value'] for t in i.tags or []}
        print(' , '. join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name)))

    return

@instance.command('stop')
@click.option('--project', default=None,
    help='Only instances for project')
def stop_instances(project):
    "Stop EC2 instances"

    instances= filter_instances(project)

    for i in instances:
        print("stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instance.command('start')
@click.option('--project', default=None,
    help='Only instances for project')
@click.option('--force',default=False, is_flag=True,
    help='Force flag needed to force start the instances')
def start_instances(project,force):
    "Start EC2 instances"

    instances= filter_instances(project)
    if force:
        for i in instances:
            print("starting {0}...".format(i.id))
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print("Could not start {0}. ".format(i.id) + str(e))
                continue
    else:
        print('Force flag needs to be enabled to force start EC2 instances')


    return

@instance.command('reboot')
@click.option('--project', default=None,
    help='Only instances for project')

def reboot_instances(project):
    "Reboot instances"

    instances=filter_instances(project)

    for i in instances:
        if i.state['Name']=='running':
            print('Rebooting {0} '.format(i.id))
            i.reboot()
        elif i.state['Name']!='running':
            print('The instance {0} is not in running state for it to be restarted'.format(i.id))

    return


if __name__=='__main__':
    cli()
