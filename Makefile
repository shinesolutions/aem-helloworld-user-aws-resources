ci: clean deps lint

clean:
	rm -rf logs/ stage/ provisioners/ansible/playbooks/*.retry

stage:
	mkdir -p stage/

# resolve dependencies from remote artifact registries
deps: stage
	pip install -r requirements.txt

lint:
	 yamllint \
	   conf/ansible/inventory/group_vars/*.yaml \
	   provisioners/ansible/playbooks/*.yaml \
	   templates/cloudformation/*.yaml
	shellcheck scripts/*.sh
	for playbook in provisioners/ansible/playbooks/*.yaml; do \
		ANSIBLE_LIBRARY=conf/ansible/library ansible-playbook -vvv $$playbook --syntax-check; \
	done

################################################################################
# AWS resources targets.
################################################################################

create-aws-resources:
	scripts/run-playbook-stack.sh create-aws-resources "${env_type}" "${stack_prefix}"

delete-aws-resources:
	scripts/run-playbook-stack.sh delete-aws-resources "${env_type}" "${stack_prefix}"

.PHONY: ci clean deps lint create-aws-resources delete-aws-resources
