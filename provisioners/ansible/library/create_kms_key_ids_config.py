"""
This module generates a YAML Packer AEM config file and a YAML AEM AWS Stack Builder config file which contains the KMS IDs for all components.
The KMS IDs are based on AWS KMS Alias name searched from defaults vars.
The YAML file is designed to be dropped directly in user configuration path.
"""
#!/usr/bin/python

import sys, json, boto3, yaml, argparse
from ansible.module_utils.basic import *

def aws_get_kms_source_aliases(client):
    StackResources = client.list_aliases(
    )
    aliases = StackResources['Aliases']
    return aliases

def get_kms_key_id(source_aliases, target_alias):
    key_id = ''
    for item in source_aliases:
        if item['AliasName'] == target_alias:
            key_id = item['TargetKeyId']
    return key_id

def aws_get_kms_key_arn(client, key_id):
    response = client.describe_key(
    KeyId = key_id
    )
    keyMetadata = response['KeyMetadata']
    key_arn = keyMetadata['Arn']
    return key_arn

def get_kms_key_arn (client, target_alias):
    if target_alias == "overwrite-me":
        return "overwrite-me"
    source_aliases = aws_get_kms_source_aliases(client)
    key_id = get_kms_key_id(source_aliases, target_alias)
    if key_id == '':
        sys.stderr.write("No kms key id matched target alias: %s.\n" % target_alias)
        raise SystemExit(1)
    key_arn = str(aws_get_kms_key_arn(client, key_id))
    return key_arn

def build_packer_aem_file(ebs_key_arn, out_file_name):
    out_file = open(out_file_name, 'w')
    out_file.write('---\n')
    out_file.write('# Generated by aem-helloworld-user-aws-resources\n')
    out_file.write('# KMS keys for Packer AEM profile on aws platform\n')
    yaml.dump({'aws': {
                    'encryption': {
                        'ebs_volume': {
                            'kms_key_id': ebs_key_arn,
                            }
                        }
                    }
                }, out_file, default_flow_style=False)

def build_stack_builder_aem_file(ebs_key_arn, dynamodb_key_arn, lambda_key_arn, s3_key_arn, sns_key_arn, out_file_name):
    out_file = open(out_file_name, 'w')
    out_file.write('---\n')
    out_file.write('# Generated by aem-helloworld-user-aws-resources\n')
    out_file.write('# KMS keys for Stack Builder AEM profile on aws platform\n')
    yaml.dump({'aws': {
                    'encryption': {
                        'ebs_volume': {
                            'kms_key_id': ebs_key_arn,
                            }
                        },
                    'dynamo_db': {
                        'ebs_volume': {
                            'kms_key_id': dynamodb_key_arn,
                            }
                        },
                    'lambda': {
                        'ebs_volume': {
                            'kms_key_id': lambda_key_arn,
                            }
                        },
                    's3': {
                        'ebs_volume': {
                            'kms_key_id': s3_key_arn,
                            }
                        },
                    'sns': {
                        'ebs_volume': {
                            'kms_key_id': sns_key_arn,
                            }
                        },
                    }
                }, out_file, default_flow_style=False)

def main():
    """
    Run create_kms_key_ids_config module.
    """

    module = AnsibleModule(
        argument_spec = dict(
            region=dict(required=True, type='str'),
            out_file_packer = dict(required = True, type = 'str'),
            out_file_stack_builder = dict(required = True, type = 'str'),
            ebs_key_alias = dict(required = True, type = 'str'),
            dynamodb_key_alias = dict(required = True, type = 'str'),
            lambda_key_alias = dict(required = True, type = 'str'),
            s3_key_alias = dict(required = True, type = 'str'),
            sns_key_alias = dict(required = True, type = 'str'),
        )
    )

    client = boto3.client('kms', region_name=module.params['region'])
    out_file_packer = module.params['out_file_packer']
    out_file_stack_builder = module.params['out_file_stack_builder']
    ebs_key_arn = get_kms_key_arn(client, module.params['ebs_key_alias'])
    dynamodb_key_arn = get_kms_key_arn(client, module.params['dynamodb_key_alias'])
    lambda_key_arn = get_kms_key_arn(client, module.params['lambda_key_alias'])
    s3_key_arn =  get_kms_key_arn(client, module.params['s3_key_alias'])
    sns_key_arn = get_kms_key_arn(client, module.params['sns_key_alias'])

    # build packer kms yml file
    build_packer_aem_file(ebs_key_arn, out_file_packer)

    # build stack builder kms yml file
    build_stack_builder_aem_file(ebs_key_arn, dynamodb_key_arn, lambda_key_arn, s3_key_arn, sns_key_arn, out_file_stack_builder)

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()