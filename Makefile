version ?= 0.9.1-pre.0

ci: clean deps lint package

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

package: stage
	tar \
	    --exclude='stage*' \
	    --exclude='.bundle' \
	    --exclude='bin' \
	    --exclude='.git*' \
	    --exclude='.tmp*' \
	    --exclude='.idea*' \
	    --exclude='.DS_Store*' \
	    --exclude='logs*' \
	    --exclude='*.retry' \
	    --exclude='*.iml' \
	    -czf \
	    stage/aem-helloworld-user-aws-resources-$(version).tar.gz .

release:
	rtk release

################################################################################
# AWS resources targets.
################################################################################

create-aws-resources:
	scripts/run-playbook-stack.sh create-aws-resources "${env_type}" "${stack_prefix}"

delete-aws-resources:
	scripts/run-playbook-stack.sh delete-aws-resources "${env_type}" "${stack_prefix}"

################################################################################
# Generate AWS KMS key ids.
################################################################################

gen-kms-keys:
    scripts/run-playbook-stack.sh gen-kms-keys

.PHONY: ci clean deps lint package create-aws-resources delete-aws-resources
