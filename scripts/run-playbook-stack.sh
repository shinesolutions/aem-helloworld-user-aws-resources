#!/usr/bin/env bash
set -o errexit
set -o nounset

if [ "$#" -ne 3 ]; then
  echo 'Usage: ./run-playbook-stack.sh <playbook_type> <env_type> <stack_prefix>'
  exit 1
fi

playbook_type=${1}
env_type=${2}
stack_prefix=${3}

extra_vars=(--extra-vars "@conf/ansible/inventory/group_vars/defaults.yaml")
extra_vars+=(--extra-vars "env_type=$env_type")
extra_vars+=(--extra-vars "stack_prefix=$stack_prefix")

echo "Extra vars:"
echo "  ${extra_vars[*]}"

ANSIBLE_CONFIG=conf/ansible/ansible.cfg \
  ansible-playbook "provisioners/ansible/playbooks/${playbook_type}.yaml" \
  -i conf/ansible/inventory/hosts \
  --module-path provisioners/ansible/library/ \
  "${extra_vars[@]}"
